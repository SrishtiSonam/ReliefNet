# reliefnet/scratch/generate_synthetic_data.py
import pandas as pd
import numpy as np
from pathlib import Path
import os

def generate_mock_data():
    # Use absolute path relative to this script
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parents[1]
    out_path = root_dir / "reliefnet" / "data" / "exports"
    
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating data in: {out_path}")
    
    # 1. Generate Districts
    districts = ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane", "Solapur", "Amravati"]
    data = []
    for d in districts:
        data.append({
            "district": d,
            "state": "Maharashtra",
            "vulnerability_score": np.random.uniform(0.1, 0.9),
            "population_density": np.random.uniform(500, 5000),
            "latitude": 19.0 + np.random.uniform(-1, 1),
            "longitude": 73.0 + np.random.uniform(-1, 1),
            "num_hospitals": np.random.randint(5, 50),
            "num_warehouses": np.random.randint(2, 10),
            "num_shelters": np.random.randint(10, 100),
            "historical_damage_score": np.random.uniform(0.1, 0.8),
            "transport_accessibility": np.random.uniform(0.4, 0.9),
            "avg_road_failure_prob": np.random.uniform(0.01, 0.1),
            "vulnerability_tier": "HIGH" if np.random.random() > 0.5 else "MEDIUM"
        })
    
    df_districts = pd.DataFrame(data)
    df_districts.to_csv(out_path / "reliefnet_district_features.csv", index=False)
    
    # 2. Generate Road Network
    roads = []
    for i in range(len(districts)):
        for j in range(i + 1, len(districts)):
            if np.random.random() > 0.4:
                roads.append({
                    "source": districts[i],
                    "target": districts[j],
                    "distance_km": np.random.uniform(50, 300),
                    "failure_probability": np.random.uniform(0.01, 0.2)
                })
    df_roads = pd.DataFrame(roads)
    df_roads.to_csv(out_path / "reliefnet_road_network.csv", index=False)
    print(f"Generated synthetic datasets in {out_path}")

if __name__ == "__main__":
    generate_mock_data()
