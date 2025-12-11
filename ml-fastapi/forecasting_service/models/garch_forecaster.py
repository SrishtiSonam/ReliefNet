"""
GARCH forecaster for volatility/surge modeling
Predicts demand surges and volatility
"""
from arch import arch_model
import pandas as pd
import numpy as np
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from backend.config import FORECASTING_CONFIG


class GARCHForecaster:
    """GARCH model for surge/volatility forecasting"""
    
    def __init__(self, p=1, q=1):
        """
        Initialize GARCH forecaster
        
        Args:
            p: GARCH p parameter
            q: GARCH q parameter
        """
        self.p = p
        self.q = q
        self.model = None
        self.fitted_model = None
    
    def fit(self, time_series: pd.Series):
        """
        Fit GARCH model
        
        Args:
            time_series: Pandas Series with datetime index
        """
        try:
            # GARCH models returns, so compute returns
            returns = time_series.pct_change().dropna() * 100
            
            # Fit GARCH model
            self.model = arch_model(
                returns,
                vol='Garch',
                p=self.p,
                q=self.q
            )
            
            self.fitted_model = self.model.fit(disp='off', show_warning=False)
            
        except Exception as e:
            print(f"GARCH fitting error: {e}")
            self.fitted_model = None
    
    def forecast(self, steps: int = 7, last_value: float = None) -> Dict[str, Any]:
        """
        Generate volatility forecast
        
        Args:
            steps: Number of steps ahead
            last_value: Last observed value for converting volatility to levels
        
        Returns:
            Forecast dictionary with surge probabilities
        """
        if self.fitted_model is None:
            # Return default forecast if model failed
            return {
                'surge_probability': [0.3] * steps,
                'volatility': [0.1] * steps,
                'confidence': 0.5
            }
        
        # Get volatility forecast
        forecast_result = self.fitted_model.forecast(horizon=steps)
        volatility = np.sqrt(forecast_result.variance.values[-1, :])
        
        # Convert volatility to surge probability
        # Higher volatility = higher surge probability
        surge_prob = 1 / (1 + np.exp(-volatility / 10))  # Sigmoid transformation
        
        return {
            'surge_probability': surge_prob.tolist(),
            'volatility': volatility.tolist(),
            'confidence': 0.75
        }


def forecast_surge_with_garch(historical_data: pd.DataFrame,
                              target_column: str = 'food_demand_kg',
                              forecast_days: int = 7) -> Dict[str, Any]:
    """
    High-level GARCH surge forecasting
    
    Args:
        historical_data: DataFrame with demand data
        target_column: Column to analyze
        forecast_days: Forecast horizon
    
    Returns:
        Surge forecast dictionary
    """
    # Prepare time series
    if 'date' in historical_data.columns:
        historical_data = historical_data.set_index('date')
    
    time_series = historical_data[target_column]
    last_value = time_series.iloc[-1]
    
    # Create and fit model
    forecaster = GARCHForecaster(**FORECASTING_CONFIG['garch'])
    forecaster.fit(time_series)
    
    # Generate forecast
    forecast = forecaster.forecast(steps=forecast_days, last_value=last_value)
    
    # Add metadata
    forecast['model'] = 'GARCH'
    forecast['target'] = target_column
    forecast['last_value'] = float(last_value)
    
    return forecast
