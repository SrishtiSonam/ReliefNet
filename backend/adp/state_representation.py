# State representation for the ADP solver
# Keeps track of inventory, demand, time, vehicles, and risk scores
from typing import Dict, List, Any
import numpy as np

class State:
    """
    Represents the current state of the disaster response system.
    
    Tracks everything we need to make allocation decisions:
    inventory, demand, time, vehicles, and risk.
    """
    
    def __init__(self, 
                 inventory: Dict[str, float],
                 demand: Dict[str, float],
                 time_step: int,
                 vehicles_available: Dict[str, int],
                 risk_scores: Dict[str, float]):
        """
        Initialize state
        
        Args:
            inventory: Dict of resource_type -> quantity
            demand: Dict of zone_id -> {resource_type -> quantity}
            time_step: Current time step (hours since disaster)
            vehicles_available: Dict of vehicle_type -> count
            risk_scores: Dict of zone_id -> risk_score
        """
        self.inventory = inventory
        self.demand = demand
        self.time_step = time_step
        self.vehicles_available = vehicles_available
        self.risk_scores = risk_scores
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'inventory': self.inventory,
            'demand': self.demand,
            'time_step': self.time_step,
            'vehicles_available': self.vehicles_available,
            'risk_scores': self.risk_scores
        }
    
    def to_feature_vector(self) -> np.ndarray:
        """
        Convert state to feature vector for VFA
        
        Returns:
            Feature vector suitable for VFA input
        """
        from vfa.feature_engineering import extract_state_features
        
        # Convert to format expected by feature engineering
        state_dict = {
            'inventory': self.inventory,
            'demand': {
                'food_kg': sum(d.get('food_kg', 0) for d in self.demand.values()),
                'water_liters': sum(d.get('water_liters', 0) for d in self.demand.values()),
                'medicine_units': sum(d.get('medicine_units', 0) for d in self.demand.values()),
                'shelter_units': sum(d.get('shelter_units', 0) for d in self.demand.values()),
            },
            'time': {
                'hour_of_day': self.time_step % 24,
                'day_of_week': (self.time_step // 24) % 7,
                'days_since_disaster': self.time_step // 24,
            },
            'risk': {
                'flood_risk': np.mean(list(self.risk_scores.values())) if self.risk_scores else 0.5,
                'accessibility': 0.7,  # Default
            },
            'resources': {
                'trucks_available': self.vehicles_available.get('truck', 0),
                'uavs_available': self.vehicles_available.get('uav', 0),
            },
            'geographic': {
                'population_density': 1000,  # Default
                'distance_to_warehouse_km': 100,  # Default
            },
            'urgency': {
                'deprivation_time_hours': self.time_step,
                'priority_score': 0.5,  # Default
            }
        }
        
        return extract_state_features(state_dict)
    
    def copy(self):
        """Create a deep copy of the state"""
        return State(
            inventory=self.inventory.copy(),
            demand={k: v.copy() for k, v in self.demand.items()},
            time_step=self.time_step,
            vehicles_available=self.vehicles_available.copy(),
            risk_scores=self.risk_scores.copy()
        )
    
    def __repr__(self):
        return f"State(t={self.time_step}, inventory={self.inventory}, demand_zones={len(self.demand)})"


def create_initial_state(warehouses_data: List[Dict], demand_data: Dict) -> State:
    """
    Create initial state from warehouse and demand data
    
    Args:
        warehouses_data: List of warehouse dictionaries
        demand_data: Dictionary of zone demands
    
    Returns:
        Initial State object
    """
    # Aggregate warehouse inventory
    total_inventory = {
        'food_kg': 0,
        'water_liters': 0,
        'medicine_units': 0,
        'shelter_units': 0,
        'blankets_units': 0,
    }
    
    for warehouse in warehouses_data:
        total_inventory['food_kg'] += warehouse.get('wheat_kg', 0) + warehouse.get('rice_kg', 0)
        total_inventory['medicine_units'] += warehouse.get('medicines_units', 0)
        total_inventory['shelter_units'] += warehouse.get('tents_units', 0)
        total_inventory['blankets_units'] += warehouse.get('blankets_units', 0)
        # Assume water is proportional to food
        total_inventory['water_liters'] += total_inventory['food_kg'] * 2
    
    # Initial vehicle availability
    vehicles_available = {
        'truck': 20,
        'uav': 10,
    }
    
    # Default risk scores
    risk_scores = {zone_id: 0.5 for zone_id in demand_data.keys()}
    
    return State(
        inventory=total_inventory,
        demand=demand_data,
        time_step=0,
        vehicles_available=vehicles_available,
        risk_scores=risk_scores
    )
