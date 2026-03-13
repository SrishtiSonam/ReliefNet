"""
demand_estimator.py  (B.2 — updated)
Uses trained Random Forest model for demand prediction.
Falls back gracefully to the original formula if model is not yet trained.
"""

from app.database import get_db
from app.ml.demand_model import get_forecaster


async def estimate_demand(district_name: str,
                           period_hours: int = 6) -> dict:
    """
    Estimate relief demand for *district_name* over a period of *period_hours*.

    Pipeline:
        1. Fetch district features from MongoDB collections.
        2. Pass features to the Random Forest demand model.
        3. Scale daily prediction to the requested period length.
        4. Return demand_mean, demand_std, plus metadata.
    """
    db = get_db()

    # ── Fetch raw data ────────────────────────────────────────────────────────
    impact    = await db.flood_impact.find_one(
        {"dist_name": {"$regex": district_name, "$options": "i"}}
    )
    dfsi_doc  = await db.dfsi.find_one(
        {"dist_name": {"$regex": district_name, "$options": "i"}}
    )
    area_doc  = await db.flooded_area.find_one(
        {"dist_name": {"$regex": district_name, "$options": "i"}}
    )
    precip    = await db.precipitation.find_one({})           # Approximate (closest record)
    catchment = await db.catchment_characteristics.find_one({})

    # ── Assemble feature vector ───────────────────────────────────────────────
    population     = float(impact.get("population", 100_000))            if impact    else 100_000.0
    pct_flooded    = float(area_doc.get("corrected_percent_flooded_area", 10.0)) if area_doc  else 10.0
    dfsi_score     = float(dfsi_doc.get("dfsi", 0.5))                    if dfsi_doc  else 0.5
    road_density   = float(catchment.get("road_density", 1.0))           if catchment else 1.0
    ruggedness     = float(catchment.get("ruggedness_number", 1.0))      if catchment else 1.0

    features = {
        "dfsi":             dfsi_score,
        "pct_flooded_area": pct_flooded,
        "population":       population,
        "t1d":              float(precip.get("t1d", 0.0)) if precip else 0.0,
        "t2d":              float(precip.get("t2d", 0.0)) if precip else 0.0,
        "t3d":              float(precip.get("t3d", 0.0)) if precip else 0.0,
        "t4d":              float(precip.get("t4d", 0.0)) if precip else 0.0,
        "t5d":              float(precip.get("t5d", 0.0)) if precip else 0.0,
        "flood_duration":   5.0,        # Default; updated if event data available
        "ruggedness":       ruggedness,
        "road_density":     road_density,
    }

    # ── Predict via Random Forest ─────────────────────────────────────────────
    forecaster   = get_forecaster()
    daily_demand = forecaster.predict(features)

    # Scale to period length and add 20 % coefficient of variation
    period_demand = daily_demand * (period_hours / 24.0)
    demand_std    = period_demand * 0.20

    return {
        "demand_mean":  round(max(period_demand, 1.0), 2),
        "demand_std":   round(max(demand_std, 0.1), 2),
        "model_used":   "random_forest" if forecaster.is_trained else "formula_fallback",
        "district":     district_name,
        "period_hours": period_hours,
        "features":     features,
    }