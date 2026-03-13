"""
ML Demand Estimator — Random Forest Regressor
Replaces formula-based estimation with a trained regression model.

Features used:
    DFSI, flooded_area_pct, population, T1d–T5d precipitation,
    flood_duration, ruggedness, road_density

Target:
    Relief demand (units/period) derived from affected population
    and historical flood impact severity.

Adapted for: India Flood Relief AI Engine
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from app.database import get_db
from app.utils.logger import get_logger
from app.ml.config import SimulationConfig, DEFAULT_CONFIG

logger = get_logger(__name__)

MODEL_DIR  = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "demand_rf_model.joblib"

# ─── Feature schema ──────────────────────────────────────────────────────────
FEATURES = [
    "dfsi",             # District Flood Severity Index
    "pct_flooded_area", # % of district area flooded
    "population",       # District population
    "t1d",              # 1-day antecedent precipitation (mm)
    "t2d",              # 2-day antecedent precipitation
    "t3d",
    "t4d",
    "t5d",
    "flood_duration",   # Duration of flood event (days)
    "ruggedness",       # Terrain ruggedness index
    "road_density",     # Road density (km/km²)
]


# ─── Model ────────────────────────────────────────────────────────────────────
class DemandForecaster:
    """
    Random Forest demand forecaster.
    Wraps sklearn Pipeline (scaler + RF) for persistence and prediction.
    """

    def __init__(self,
                 config: Optional[SimulationConfig] = None,
                 flood_predictor=None):
        """
        Parameters
        ----------
        config          : SimulationConfig for RF hyperparameters.
        flood_predictor : Optional FloodPredictor instance.  When provided,
                          the predicted DFSI replaces the historical dfsi
                          feature at inference time.
        """
        self.config          = config or DEFAULT_CONFIG
        self.flood_predictor = flood_predictor
        self.pipeline: Optional[Pipeline] = None
        self._load_if_exists()

    # ── Persistence ──────────────────────────────────────────────────────────
    def _load_if_exists(self):
        if MODEL_PATH.exists():
            self.pipeline = joblib.load(MODEL_PATH)
            logger.info("Loaded pre-trained Random Forest demand model.")

    def _save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, MODEL_PATH)
        logger.info(f"Demand RF model saved → {MODEL_PATH}")

    # ── Training data assembly ────────────────────────────────────────────────
    async def build_training_data(self) -> pd.DataFrame:
        """
        Join: flood_impact + dfsi + flooded_area + precipitation + catchment
        into one training DataFrame.

        Target (demand_target):
            affected_pop × 0.02 × (1 + DFSI) × precipitation_severity_factor
        """
        db = get_db()

        impact_docs   = await db.flood_impact.find({}, {"_id": 0}).to_list(length=5000)
        dfsi_docs     = await db.dfsi.find({}, {"_id": 0}).to_list(length=2000)
        area_docs     = await db.flooded_area.find({}, {"_id": 0}).to_list(length=2000)
        precip_docs   = await db.precipitation.find({}, {"_id": 0}).to_list(length=10000)
        catchment_docs= await db.catchment_characteristics.find({}, {"_id": 0}).to_list(length=2000)
        event_docs    = await db.indofloods_events.find({}, {"_id": 0}).to_list(length=5000)

        df_impact   = pd.DataFrame(impact_docs)   if impact_docs   else pd.DataFrame()
        df_dfsi     = pd.DataFrame(dfsi_docs)     if dfsi_docs     else pd.DataFrame()
        df_area     = pd.DataFrame(area_docs)     if area_docs     else pd.DataFrame()
        df_precip   = pd.DataFrame(precip_docs)   if precip_docs   else pd.DataFrame()
        df_catchment= pd.DataFrame(catchment_docs)if catchment_docs else pd.DataFrame()
        df_events   = pd.DataFrame(event_docs)    if event_docs    else pd.DataFrame()

        if df_precip.empty:
            logger.warning("No precipitation data — cannot build training set.")
            return pd.DataFrame()

        # ── Per-district joins (left merge on shared key) ─────────────────────
        df = df_precip.copy()

        # Determine the join key available in each table
        join_key = "district" if "district" in df.columns else (
                   "station_id" if "station_id" in df.columns else None)

        def _merge(base: pd.DataFrame, other: pd.DataFrame,
                   cols: list, rename: dict = None) -> pd.DataFrame:
            """Left-join `other[cols]` onto `base` on join_key; fall back to mean on NaN."""
            if other.empty or join_key is None or join_key not in other.columns:
                return base
            available = [c for c in cols if c in other.columns]
            if not available:
                return base
            tmp = other[[join_key] + available].copy()
            if rename:
                tmp = tmp.rename(columns=rename)
                available = [rename.get(c, c) for c in available]
            merged = base.merge(tmp, on=join_key, how="left", suffixes=("", "_r"))
            # Fill NaNs with column mean as fallback
            for col in available:
                if col in merged.columns:
                    merged[col] = pd.to_numeric(merged[col], errors="coerce")
                    merged[col] = merged[col].fillna(merged[col].mean())
            return merged

        df = _merge(df, df_dfsi,     ["dfsi"])
        df = _merge(df, df_impact,   ["population"])
        df = _merge(df, df_area,     ["corrected_percent_flooded_area"],
                    rename={"corrected_percent_flooded_area": "pct_flooded_area"})
        df = _merge(df, df_catchment, ["ruggedness_number", "road_density"],
                    rename={"ruggedness_number": "ruggedness"})
        df = _merge(df, df_events,   ["event_duration"],
                    rename={"event_duration": "flood_duration"})

        # Global-mean fallbacks for rows / tables with no join key
        if "dfsi" not in df.columns or df["dfsi"].isna().all():
            df["dfsi"] = (float(df_dfsi["dfsi"].mean())
                          if not df_dfsi.empty and "dfsi" in df_dfsi.columns else 0.5)
        if "population" not in df.columns or df["population"].isna().all():
            df["population"] = (float(df_impact["population"].mean())
                                if not df_impact.empty and "population" in df_impact.columns else 100_000)
        if "pct_flooded_area" not in df.columns or df["pct_flooded_area"].isna().all():
            df["pct_flooded_area"] = (float(df_area["corrected_percent_flooded_area"].mean())
                                      if not df_area.empty else 10.0)
        if "ruggedness" not in df.columns or df["ruggedness"].isna().all():
            df["ruggedness"] = (float(df_catchment["ruggedness_number"].mean())
                                if not df_catchment.empty and "ruggedness_number" in df_catchment.columns else 1.0)
        if "road_density" not in df.columns or df["road_density"].isna().all():
            df["road_density"] = (float(df_catchment["road_density"].mean())
                                  if not df_catchment.empty and "road_density" in df_catchment.columns else 1.0)
        if "flood_duration" not in df.columns or df["flood_duration"].isna().all():
            df["flood_duration"] = (float(df_events["event_duration"].mean())
                                    if not df_events.empty and "event_duration" in df_events.columns else 5.0)

        for col in ["t1d", "t2d", "t3d", "t4d", "t5d"]:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # ── Synthetic target ──────────────────────────────────────────────────
        # demand = affected_pop × supply_rate × DFSI_scale × precip_scale
        precip_sum = df[["t1d", "t2d", "t3d", "t4d", "t5d"]].sum(axis=1)
        df["demand_target"] = (
            df["population"]
            * 0.02                                   # 2% of population needs daily supply
            * (df["pct_flooded_area"] / 100.0)
            * (1.0 + df["dfsi"])                     # DFSI amplifier
            * (1.0 + precip_sum / 500.0)             # Precipitation amplifier
        )

        # Drop nulls on target
        df = df.dropna(subset=["demand_target"])
        df = df[df["demand_target"] > 0]

        logger.info(f"Training dataset assembled: {len(df)} samples.")
        return df

    # ── Train ─────────────────────────────────────────────────────────────────
    async def train(self,
                    n_estimators: int = 300,
                    max_depth: int = 12,
                    min_samples_leaf: int = 3) -> Dict:
        """Train and persist the Random Forest pipeline."""
        df = await self.build_training_data()

        if df.empty or len(df) < 20:
            logger.warning("Insufficient training data — model not updated.")
            return {"status": "insufficient_data", "samples": len(df)}

        for feat in FEATURES:
            if feat not in df.columns:
                df[feat] = 0.0
            df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)

        X = df[FEATURES].values.astype(np.float32)
        y = df["demand_target"].values.astype(np.float32)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators      = n_estimators,
                max_depth         = max_depth,
                min_samples_leaf  = min_samples_leaf,
                max_features      = "sqrt",
                random_state      = 42,
                n_jobs            = -1,
            ))
        ])

        self.pipeline.fit(X_train, y_train)
        y_pred = self.pipeline.predict(X_test)

        mae  = mean_absolute_error(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2   = r2_score(y_test, y_pred)

        # 5-fold CV on full data
        cv_scores = cross_val_score(self.pipeline, X, y, cv=5, scoring="r2")

        self._save()

        metrics = {
            "status":     "trained",
            "samples":    int(len(X)),
            "mae":        round(mae, 2),
            "rmse":       round(rmse, 2),
            "r2":         round(r2, 4),
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std":  round(float(cv_scores.std()),  4),
        }
        logger.info(f"RF demand model trained: {metrics}")
        return metrics

    # ── Predict ───────────────────────────────────────────────────────────────
    def predict(self, features: Dict) -> float:
        """
        Predict demand given a feature dict.
        Falls back to analytical formula if model not yet trained.
        """
        if self.pipeline is None:
            return self._formula_fallback(features)

        row = np.array(
            [[float(features.get(f, 0.0)) for f in FEATURES]],
            dtype=np.float32
        )
        return float(self.pipeline.predict(row)[0])

    def _formula_fallback(self, features: Dict) -> float:
        """Original formula-based fallback."""
        pop   = features.get("population", 100_000)
        pct   = features.get("pct_flooded_area", 10.0)
        dfsi  = features.get("dfsi", 0.5)
        t1d   = features.get("t1d", 0.0)
        return pop * 0.02 * (pct / 100.0) * (1.0 + dfsi) * (1.0 + t1d / 100.0)

    # ── Feature importance ────────────────────────────────────────────────────
    def feature_importance(self) -> Dict[str, float]:
        if self.pipeline is None:
            return {}
        rf = self.pipeline.named_steps["rf"]
        return {
            feat: round(float(imp), 4)
            for feat, imp in zip(FEATURES, rf.feature_importances_)
        }

    @property
    def is_trained(self) -> bool:
        return self.pipeline is not None


# ─── Module-level singleton ───────────────────────────────────────────────────
_forecaster: Optional[DemandForecaster] = None

def get_forecaster() -> DemandForecaster:
    global _forecaster
    if _forecaster is None:
        _forecaster = DemandForecaster()
    return _forecaster