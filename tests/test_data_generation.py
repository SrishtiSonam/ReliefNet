# train/generate_synthetic_data.py
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta

def generate_district_time_series(n_periods=100, n_districts=5, seed=42):
    """Generate synthetic time series data for districts"""
    np.random.seed(seed)
    
    data = []
    district_ids = [f"D{i:03d}" for i in range(1, n_districts + 1)]
    
    for period in range(n_periods):
        timestamp = datetime.now() - timedelta(hours=n_periods - period)
        
        for district_id in district_ids:
            # Base demand with trend and seasonality
            base_demand = 15 + 5 * np.sin(2 * np.pi * period / 24)  # Daily cycle
            
            # Add random shocks
            if np.random.random() < 0.05:  # 5% chance of surge
                base_demand *= np.random.uniform(2, 4)
            
            # Add noise
            demand = max(0, base_demand + np.random.normal(0, 3))
            
            # Other district features
            inventory = np.random.uniform(50, 200)
            backlog = max(0, np.random.exponential(10))
            deprivation = np.random.gamma(2, 2)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "district_id": district_id,
                "demand": demand,
                "inventory": inventory,
                "backlog": backlog,
                "avg_deprivation_time": deprivation,
                "road_access": "open"
            })
    
    return pd.DataFrame(data)

def generate_scenarios():
    """Generate example scenarios for simulation"""
    scenarios = [
        {
            "name": "baseline",
            "description": "Normal operations scenario",
            "seed": 42,
            "periods": 24,
            "shock_times": [],
            "shock_multipliers": {"districts": [], "mult": []},
            "road_failures": []
        },
        {
            "name": "surge_heavy",
            "description": "Heavy surge in urban districts",
            "seed": 123,
            "periods": 24,
            "shock_times": [6, 7, 8],
            "shock_multipliers": {
                "districts": ["D001", "D002"], 
                "mult": [3.5, 2.8]
            },
            "road_failures": []
        },
        {
            "name": "infrastructure_failure",
            "description": "Road network disruption",
            "seed": 456,
            "periods": 24,
            "shock_times": [4, 5],
            "shock_multipliers": {
                "districts": ["D003"], 
                "mult": [2.0]
            },
            "road_failures": [
                {"time": 8, "edge": ["D003", "D004"]},
                {"time": 12, "edge": ["D001", "D002"]}
            ]
        },
        {
            "name": "multi_district_surge",
            "description": "Simultaneous surge across multiple districts",
            "seed": 789,
            "periods": 48,
            "shock_times": [12, 13, 14, 24, 25],
            "shock_multipliers": {
                "districts": ["D001", "D002", "D003", "D004"], 
                "mult": [2.5, 3.0, 2.2, 1.8]
            },
            "road_failures": []
        }
    ]
    
    return scenarios

def create_fleet_config():
    """Create fleet configuration"""
    return [
        {
            "class": "small_truck",
            "capacity": 100,
            "speed": 40,
            "range_km": 500,
            "count": 5,
            "cost_per_hour": 50,
            "fuel_consumption": 0.3
        },
        {
            "class": "large_truck", 
            "capacity": 200,
            "speed": 35,
            "range_km": 600,
            "count": 3,
            "cost_per_hour": 80,
            "fuel_consumption": 0.5
        },
        {
            "class": "uav_light",
            "capacity": 10,
            "speed": 60,
            "range_km": 50,
            "count": 8,
            "cost_per_hour": 25,
            "fuel_consumption": 0.05
        },
        {
            "class": "uav_heavy",
            "capacity": 30,
            "speed": 50,
            "range_km": 80,
            "count": 4,
            "cost_per_hour": 40,
            "fuel_consumption": 0.1
        }
    ]

def create_road_network():
    """Create road network graph"""
    return {
        "nodes": [
            {"id": "D001", "name": "Central", "coords": [28.6139, 77.2090]},
            {"id": "D002", "name": "North", "coords": [28.6448, 77.2167]},
            {"id": "D003", "name": "South", "coords": [28.5832, 77.2275]},
            {"id": "D004", "name": "East", "coords": [28.6139, 77.2455]},
            {"id": "D005", "name": "West", "coords": [28.6139, 77.1724]}
        ],
        "edges": [
            {"u": "D001", "v": "D002", "distance": 12.4, "travel_time_mean": 0.5, "failure_prob": 0.02},
            {"u": "D001", "v": "D003", "distance": 18.1, "travel_time_mean": 0.7, "failure_prob": 0.01},
            {"u": "D001", "v": "D004", "distance": 15.2, "travel_time_mean": 0.6, "failure_prob": 0.03},
            {"u": "D001", "v": "D005", "distance": 10.8, "travel_time_mean": 0.4, "failure_prob": 0.02},
            {"u": "D002", "v": "D003", "distance": 25.6, "travel_time_mean": 1.2, "failure_prob": 0.04},
            {"u": "D002", "v": "D004", "distance": 20.3, "travel_time_mean": 0.9, "failure_prob": 0.02},
            {"u": "D003", "v": "D004", "distance": 22.7, "travel_time_mean": 1.0, "failure_prob": 0.03},
            {"u": "D003", "v": "D005", "distance": 28.4, "travel_time_mean": 1.3, "failure_prob": 0.05},
            {"u": "D004", "v": "D005", "distance": 26.1, "travel_time_mean": 1.1, "failure_prob": 0.04}
        ]
    }

def main():
    """Generate all synthetic data"""
    print("Generating synthetic data...")
    
    # Create directories
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True) 
    os.makedirs("data/scenarios", exist_ok=True)
    
    # Generate time series data
    df = generate_district_time_series()
    df.to_csv("data/raw/district_timeseries.csv", index=False)
    print(f"Generated {len(df)} time series records")
    
    # Generate scenarios
    scenarios = generate_scenarios()
    for scenario in scenarios:
        filename = f"data/scenarios/{scenario['name']}.json"
        with open(filename, 'w') as f:
            json.dump(scenario, f, indent=2)
        print(f"Created scenario: {scenario['name']}")
    
    # Generate fleet config
    fleet = create_fleet_config()
    with open("data/processed/fleet_config.json", 'w') as f:
        json.dump(fleet, f, indent=2)
    print("Created fleet configuration")
    
    # Generate road network
    roads = create_road_network()
    with open("data/processed/road_network.json", 'w') as f:
        json.dump(roads, f, indent=2)
    print("Created road network")
    
    # Create sample processed data
    summary_stats = df.groupby('district_id').agg({
        'demand': ['mean', 'std', 'min', 'max'],
        'backlog': ['mean', 'std'],
        'inventory': ['mean', 'std']
    }).round(2)
    
    summary_stats.to_csv("data/processed/district_summary.csv")
    print("Created summary statistics")
    
    print("Synthetic data generation complete!")

if __name__ == "__main__":
    main()