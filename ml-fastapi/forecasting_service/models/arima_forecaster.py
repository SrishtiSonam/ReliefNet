"""
ARIMA forecaster for demand prediction
Uses statsmodels for time series forecasting
"""
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from backend.config import FORECASTING_CONFIG


class ARIMAForecaster:
    """ARIMA-based demand forecaster"""
    
    def __init__(self, order=(2, 1, 2), seasonal_order=(1, 1, 1, 7)):
        """
        Initialize ARIMA forecaster
        
        Args:
            order: (p, d, q) for ARIMA
            seasonal_order: (P, D, Q, s) for seasonal component
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted_model = None
    
    def fit(self, time_series: pd.Series):
        """
        Fit ARIMA model to time series
        
        Args:
            time_series: Pandas Series with datetime index
        """
        try:
            self.model = SARIMAX(
                time_series,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            self.fitted_model = self.model.fit(disp=False, maxiter=200)
            
        except Exception as e:
            print(f"ARIMA fitting error: {e}")
            # Fallback to simpler model
            self.model = SARIMAX(
                time_series,
                order=(1, 1, 1),
                enforce_stationarity=False
            )
            self.fitted_model = self.model.fit(disp=False)
    
    def forecast(self, steps: int = 7) -> Dict[str, Any]:
        """
        Generate forecast
        
        Args:
            steps: Number of steps ahead to forecast
        
        Returns:
            Dictionary with predictions and confidence intervals
        """
        if self.fitted_model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Get forecast
        forecast_result = self.fitted_model.get_forecast(steps=steps)
        predictions = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        
        return {
            'predictions': predictions.tolist(),
            'lower_bound': conf_int.iloc[:, 0].tolist(),
            'upper_bound': conf_int.iloc[:, 1].tolist(),
            'confidence': 0.95
        }


def forecast_with_arima(historical_data: pd.DataFrame,
                       target_column: str = 'food_demand_kg',
                       forecast_days: int = 7) -> Dict[str, Any]:
    """
    High-level ARIMA forecasting function
    
    Args:
        historical_data: DataFrame with 'date' and demand columns
        target_column: Column to forecast
        forecast_days: Number of days to forecast
    
    Returns:
        Forecast dictionary
    """
    # Prepare time series
    if 'date' in historical_data.columns:
        historical_data = historical_data.set_index('date')
    
    time_series = historical_data[target_column]
    
    # Create and fit model
    forecaster = ARIMAForecaster(**FORECASTING_CONFIG['arima'])
    forecaster.fit(time_series)
    
    # Generate forecast
    forecast = forecaster.forecast(steps=forecast_days)
    
    # Add metadata
    forecast['model'] = 'ARIMA'
    forecast['target'] = target_column
    forecast['historical_mean'] = float(time_series.mean())
    forecast['historical_std'] = float(time_series.std())
    
    return forecast
