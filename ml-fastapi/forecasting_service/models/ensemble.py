"""
Ensemble forecaster combining ARIMA, GARCH, and simple predictions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from backend.config import FORECASTING_CONFIG

try:
    from .arima_forecaster import forecast_with_arima
    from .garch_forecaster import forecast_surge_with_garch
except:
    # Fallback imports
    pass


def simple_forecast(historical_data: pd.DataFrame,
                   target_column: str,
                   forecast_days: int) -> Dict[str, Any]:
    """
    Simple moving average forecast as fallback
    
    Args:
        historical_data: Historical demand data
        target_column: Column to forecast
        forecast_days: Forecast horizon
    
    Returns:
        Simple forecast dictionary
    """
    if 'date' in historical_data.columns:
        historical_data = historical_data.set_index('date')
    
    # Use last 30 days
    recent_data = historical_data[target_column].tail(30)
    
    # Calculate trend
    mean_value = recent_data.mean()
    trend = (recent_data.iloc[-1] - recent_data.iloc[0]) / len(recent_data)
    
    # Generate predictions
    predictions = []
    for i in range(forecast_days):
        pred = mean_value + trend * (i + 1)
        predictions.append(max(0, pred))  # Ensure non-negative
    
    return {
        'predictions': predictions,
        'confidence': 0.6,
        'model': 'Simple'
    }


def ensemble_forecast(historical_data: pd.DataFrame,
                     region: str = 'India',
                     forecast_days: int = 7) -> Dict[str, Any]:
    """
    Ensemble forecast combining multiple models
    
    Args:
        historical_data: Historical demand data
        region: Region name
        forecast_days: Forecast horizon
    
    Returns:
        Combined forecast dictionary
    """
    target_column = 'food_demand_kg'
    
    # Get weights from config
    weights = FORECASTING_CONFIG['ensemble']['weights']
    
    forecasts = {}
    
    # Try ARIMA
    try:
        arima_forecast = forecast_with_arima(historical_data, target_column, forecast_days)
        forecasts['arima'] = arima_forecast['predictions']
    except Exception as e:
        print(f"ARIMA failed: {e}")
        forecasts['arima'] = simple_forecast(historical_data, target_column, forecast_days)['predictions']
    
    # Try GARCH for surge
    try:
        garch_forecast = forecast_surge_with_garch(historical_data, target_column, forecast_days)
        # Convert surge probability to demand multiplier
        surge_multipliers = [1 + sp * 0.5 for sp in garch_forecast['surge_probability']]
        base_demand = historical_data[target_column].tail(7).mean()
        forecasts['garch'] = [base_demand * mult for mult in surge_multipliers]
    except Exception as e:
        print(f"GARCH failed: {e}")
        forecasts['garch'] = simple_forecast(historical_data, target_column, forecast_days)['predictions']
    
    # Simple forecast as transformer replacement
    forecasts['transformer'] = simple_forecast(historical_data, target_column, forecast_days)['predictions']
    
    # Combine with weights
    ensemble_predictions = []
    for i in range(forecast_days):
        weighted_sum = (
            forecasts['arima'][i] * weights['arima'] +
            forecasts['garch'][i] * weights['garch'] +
            forecasts['transformer'][i] * weights['transformer']
        )
        ensemble_predictions.append(weighted_sum)
    
    # Calculate confidence based on agreement
    confidence_scores = []
    for i in range(forecast_days):
        values = [forecasts['arima'][i], forecasts['garch'][i], forecasts['transformer'][i]]
        std = np.std(values)
        mean = np.mean(values)
        # Lower std relative to mean = higher confidence
        conf = 1 / (1 + std / (mean + 1))
        confidence_scores.append(conf)
    
    # Generate dates
    last_date = historical_data['date'].max() if 'date' in historical_data.columns else datetime.now()
    forecast_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                     for i in range(forecast_days)]
    
    return {
        'region': region,
        'forecast_days': forecast_days,
        'predictions': [
            {
                'date': forecast_dates[i],
                'food_demand': ensemble_predictions[i],
                'water_demand': ensemble_predictions[i] * 2,  # Proportional
                'medicine_demand': ensemble_predictions[i] * 0.1,
                'shelter_demand': ensemble_predictions[i] * 0.3,
                'confidence': confidence_scores[i]
            }
            for i in range(forecast_days)
        ],
        'model_contributions': {
            'arima': weights['arima'],
            'garch': weights['garch'],
            'transformer': weights['transformer']
        },
        'overall_confidence': np.mean(confidence_scores)
    }
