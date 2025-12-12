# Feature extraction for the VFA models
# Takes the current state and converts it into a 20-dimensional feature vector
import numpy as np
import pandas as pd
from typing import Dict, List, Any


def extract_state_features(state: Dict[str, Any]) -> np.ndarray:
    """
    Converts a state dict into a feature vector for the neural network.
    
    We normalize everything to [0, 1] range so the network trains better.
    Total of 20 features covering inventory, demand, time, risk, etc.
    """
    features = []
    
    # Inventory levels (5 features)
    # Normalized by typical max capacity
    inventory = state.get('inventory', {})
    features.append(inventory.get('food_kg', 0) / 10000)  # Max ~10k kg
    features.append(inventory.get('water_liters', 0) / 20000)  # Max ~20k liters
    features.append(inventory.get('medicine_units', 0) / 1000)
    features.append(inventory.get('shelter_units', 0) / 500)
    features.append(inventory.get('blankets_units', 0) / 1000)
    
    # Current demand (4 features)
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
    """Creates a sample state for testing the feature extraction"""
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
