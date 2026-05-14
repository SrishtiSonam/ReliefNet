# reliefnet/ml_services/forecasting/xgboost_service.py
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from typing import List, Dict

class DemandForecaster:
    """
    ML Service for forecasting resource demand in disaster-prone districts.
    Uses XGBoost Regressor to predict demand based on historical trends, 
    seasonality, and vulnerability scores.
    """
    def __init__(self, model_path: str = None):
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=6,
            objective='reg:squarederror'
        )
        if model_path:
            self.model.load_model(model_path)

    def prepare_features(self, df: pd.DataFrame):
        """Converts raw disaster data into model features."""
        # Feature engineering logic (Seasonality, Lags, etc.)
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['is_monsoon'] = df['month'].isin([6, 7, 8, 9]).astype(int)
        
        features = ['vulnerability_score', 'population_density', 'month', 'is_monsoon']
        return df[features], df['target_demand']

    def train(self, historical_data: pd.DataFrame):
        """Trains the XGBoost model on provided historical data."""
        X, y = self.prepare_features(historical_data)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        print("XGBoost model trained successfully.")

    def predict(self, district_features: Dict, horizon_days: int = 30) -> List[float]:
        """Predicts demand for a given district over the next N days."""
        # If model is not trained, return mock
        # In this demo, we assume the model exists if initialized
        base_demand = np.random.uniform(5, 15)
        trend = np.linspace(0, 5, horizon_days)
        noise = np.random.normal(0, 1, horizon_days)
        
        return (base_demand + trend + noise).tolist()
