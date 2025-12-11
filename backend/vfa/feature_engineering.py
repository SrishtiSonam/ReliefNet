"""
Feature engineering for VFA state representation
Extracts features from current state for value function approximation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any


def extract_state_features(state: Dict[str, Any]) -> np.ndarray:
    """
    Extract feature vector from state for VFA input
    
    State includes:
    - Warehouse inventory levels
    - Current demand
    - Time information
    - Risk scores
    - Vehicle availability
    
    Returns:
        Feature vector of shape (20,)
    """
    features = []
    
    # Inventory features (normalized by capacity)
    inventory = state.get('inventory', {})
    features.append(inventory.get('food_kg', 0) / 10000)  # Normalize by 10k kg
    features.append(inventory.get('water_liters', 0) / 20000)
    features.append(inventory.get('medicine_units', 0) / 1000)
    features.append(inventory.get('shelter_units', 0) / 500)
    features.append(inventory.get('blankets_units', 0) / 1000)
    
    # Demand features (normalized)
    demand = state.get('demand', {})
    features.append(demand.get('food_kg', 0) / 10000)
    features.append(demand.get('water_liters', 0) / 20000)
    features.append(demand.get('medicine_units', 0) / 1000)
    features.append(demand.get('shelter_units', 0) / 500)
    
    # Time features
    time_info = state.get('time', {})
    features.append(time_info.get('hour_of_day', 12) / 24)  # Normalize to [0, 1]
    features.append(time_info.get('day_of_week', 3) / 7)
    features.append(time_info.get('days_since_disaster', 0) / 30)  # Normalize by 30 days
    
    # Risk features
    risk = state.get('risk', {})
    features.append(risk.get('flood_risk', 0.5))  # Already [0, 1]
    features.append(risk.get('accessibility', 0.8))  # Road accessibility
    
    # Resource availability
    resources = state.get('resources', {})
    features.append(resources.get('trucks_available', 10) / 20)
    features.append(resources.get('uavs_available', 5) / 10)
    
    # Geographic features
    geo = state.get('geographic', {})
    features.append(geo.get('population_density', 500) / 5000)  # Normalize
    features.append(geo.get('distance_to_warehouse_km', 50) / 500)
    
    # Urgency features
    urgency = state.get('urgency', {})
    features.append(urgency.get('deprivation_time_hours', 0) / 72)  # Normalize by 3 days
    features.append(urgency.get('priority_score', 0.5))  # [0, 1]
    
    return np.array(features, dtype=np.float32)


def create_sample_state() -> Dict[str, Any]:
    """Create a sample state for testing"""
    return {
        'inventory': {
            'food_kg': 5000,
            'water_liters': 10000,
            'medicine_units': 500,
            'shelter_units': 200,
            'blankets_units': 600,
        },
        'demand': {
            'food_kg': 3000,
            'water_liters': 6000,
            'medicine_units': 300,
            'shelter_units': 100,
        },
        'time': {
            'hour_of_day': 14,
            'day_of_week': 3,
            'days_since_disaster': 5,
        },
        'risk': {
            'flood_risk': 0.7,
            'accessibility': 0.6,
        },
        'resources': {
            'trucks_available': 8,
            'uavs_available': 4,
        },
        'geographic': {
            'population_density': 2000,
            'distance_to_warehouse_km': 120,
        },
        'urgency': {
            'deprivation_time_hours': 24,
            'priority_score': 0.8,
        }
    }
