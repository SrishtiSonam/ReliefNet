"""
Mock Temporal Fusion Transformer (TFT) for Educational Demo
Simulates TFT behavior without requiring full PyTorch training
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class MockTFTForecaster:
    """
    Simplified TFT that demonstrates all key concepts:
    - Multi-horizon forecasting
    - Attention mechanisms
    - Uncertainty quantification
    - Variable importance
    
    This is a mock for educational purposes - shows TFT concepts without
    the complexity of full deep learning training.
    """
    
    def __init__(self, max_prediction_length=30):
        self.max_prediction_length = max_prediction_length
        self.is_trained = True  # Mock is always "trained"
        
    def predict(self, district='Mumbai', forecast_horizon=30):
        """
        Generate TFT-style predictions with uncertainty intervals.
        
        Returns:
            Dictionary with predictions, quantiles, and attention weights
        """
        np.random.seed(hash(district) % 1000)
        
        # Base demand varies by district
        base_demands = {
            'Mumbai': 2000,
            'Delhi': 1900,
            'Kolkata': 1400,
            'Chennai': 1000,
            'Bangalore': 1200,
        }
        base = base_demands.get(district, 1500)
        
        # Generate multi-horizon forecast
        predictions = []
        for i in range(forecast_horizon):
            # Trend + seasonality + noise
            trend = base * (1 + i * 0.01)
            seasonality = 100 * np.sin(i / 7 * 2 * np.pi)  # Weekly pattern
            noise = np.random.normal(0, 50)
            pred = trend + seasonality + noise
            predictions.append(max(0, pred))
        
        # Generate uncertainty intervals (quantiles)
        quantiles = self._generate_quantiles(predictions)
        
        # Generate attention weights
        attention = self._generate_attention_weights()
        
        return {
            'predictions': np.array(predictions),
            'quantiles': quantiles,
            'attention': attention,
            'model': 'Temporal Fusion Transformer (Mock)',
            'horizon': forecast_horizon
        }
    
    def _generate_quantiles(self, predictions):
        """
        Generate prediction intervals (10th, 50th, 90th percentiles).
        
        This shows uncertainty in TFT predictions.
        """
        predictions = np.array(predictions)
        
        quantiles = {
            'q10': predictions * 0.85,  # Lower bound
            'q50': predictions,          # Median
            'q90': predictions * 1.15,   # Upper bound
        }
        
        return quantiles
    
    def _generate_attention_weights(self):
        """
        Generate attention weights showing which features the model focuses on.
        
        This is the key interpretability feature of TFT.
        """
        features = [
            'rainfall',
            'temperature', 
            'population',
            'infrastructure',
            'coastal',
            'disaster_history',
            'road_accessibility'
        ]
        
        # Generate realistic attention patterns
        # Rainfall and disaster history get high attention
        attention_weights = {
            'rainfall': 0.35,
            'temperature': 0.10,
            'population': 0.20,
            'infrastructure': 0.08,
            'coastal': 0.12,
            'disaster_history': 0.10,
            'road_accessibility': 0.05
        }
        
        # Temporal attention (which time steps matter most)
        time_steps = 30  # Last 30 days
        temporal_attention = np.exp(-np.arange(time_steps) / 10)  # Recent days matter more
        temporal_attention = temporal_attention / temporal_attention.sum()
        
        return {
            'variable_attention': attention_weights,
            'temporal_attention': temporal_attention.tolist(),
            'features': features
        }
    
    def get_variable_importance(self):
        """
        Return variable importance scores.
        
        Shows which features contribute most to predictions.
        """
        attention = self._generate_attention_weights()
        
        importance = []
        for feature, weight in attention['variable_attention'].items():
            importance.append({
                'feature': feature,
                'importance': weight,
                'rank': 0  # Will be filled after sorting
            })
        
        # Sort by importance
        importance.sort(key=lambda x: x['importance'], reverse=True)
        for i, item in enumerate(importance):
            item['rank'] = i + 1
        
        return importance
    
    def compare_with_arima(self, district='Mumbai', days=7):
        """
        Compare TFT predictions with ARIMA baseline.
        
        Shows the advantage of deep learning.
        """
        # Get TFT predictions
        tft_result = self.predict(district, days)
        tft_forecast = tft_result['predictions']
        
        # Simulate ARIMA predictions (simpler, less accurate)
        np.random.seed(hash(district) % 1000 + 1)
        base = 1500
        arima_forecast = []
        for i in range(days):
            pred = base * (1 + i * 0.008) + np.random.normal(0, 100)
            arima_forecast.append(max(0, pred))
        
        # Calculate metrics
        tft_variance = np.var(np.diff(tft_forecast))
        arima_variance = np.var(np.diff(arima_forecast))
        
        # TFT typically has smoother, more accurate predictions
        improvement = ((arima_variance - tft_variance) / arima_variance * 100)
        
        return {
            'tft': {
                'forecast': tft_forecast.tolist(),
                'variance': float(tft_variance),
                'model': 'Temporal Fusion Transformer'
            },
            'arima': {
                'forecast': arima_forecast,
                'variance': float(arima_variance),
                'model': 'ARIMA + GARCH'
            },
            'improvement': f'{improvement:.1f}%',
            'winner': 'TFT' if tft_variance < arima_variance else 'ARIMA'
        }

# Global instance
mock_tft = MockTFTForecaster()

def get_tft_forecast(district='Mumbai', horizon=30):
    """Convenience function for API"""
    return mock_tft.predict(district, horizon)

def get_tft_attention(district='Mumbai'):
    """Get attention weights for visualization"""
    result = mock_tft.predict(district, 7)
    return result['attention']

def get_tft_comparison(district='Mumbai'):
    """Compare TFT vs ARIMA"""
    return mock_tft.compare_with_arima(district, 7)

def get_variable_importance():
    """Get feature importance"""
    return mock_tft.get_variable_importance()
