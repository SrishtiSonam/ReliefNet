import pandas as pd
import numpy as np
import random
import os

def generate_data(output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Districts
    num_districts = 12
    districts = []
    for i in range(num_districts):
        districts.append({
            "district_id": i,
            "name": f"District_{chr(65+i)}",
            "lat": 34.05 + np.random.uniform(-0.1, 0.1),
            "lon": -118.25 + np.random.uniform(-0.1, 0.1),
            "base_demand": np.random.randint(50, 200),
            "vulnerability_score": np.random.uniform(0.1, 0.9)
        })
    df_districts = pd.DataFrame(districts)
    df_districts.to_csv(f"{output_dir}/districts.csv", index=False)
    print("Generated districts.csv")

    # 2. Population
    population = []
    for d in districts:
        population.append({
            "district_id": d["district_id"],
            "total_pop": np.random.randint(1000, 50000),
            "elderly_ratio": np.random.uniform(0.1, 0.3),
            "children_ratio": np.random.uniform(0.1, 0.3)
        })
    df_pop = pd.DataFrame(population)
    df_pop.to_csv(f"{output_dir}/population.csv", index=False)
    print("Generated population.csv")

    # 3. Roads (Edges)
    roads = []
    for i in range(num_districts):
        for j in range(i + 1, num_districts):
            if np.random.random() < 0.4: # 40% connectivity
                dist = np.sqrt((districts[i]["lat"] - districts[j]["lat"])**2 + 
                               (districts[i]["lon"] - districts[j]["lon"])**2) * 111 # approx km
                roads.append({
                    "source": i,
                    "target": j,
                    "distance_km": round(dist, 2),
                    "capacity_trucks": np.random.randint(5, 20),
                    "risk_factor": np.random.uniform(0.0, 0.5)
                })
    df_roads = pd.DataFrame(roads)
    df_roads.to_csv(f"{output_dir}/roads.csv", index=False)
    print("Generated roads.csv")

    # 4. Vehicle Specs
    truck_specs = [{
        "type": "Heavy_Truck",
        "capacity_kg": 5000,
        "speed_kmh": 60,
        "cost_per_km": 2.5
    }, {
        "type": "Light_Truck",
        "capacity_kg": 1500,
        "speed_kmh": 80,
        "cost_per_km": 1.5
    }]
    pd.DataFrame(truck_specs).to_csv(f"{output_dir}/truck_specs.csv", index=False)
    
    uav_specs = [{
        "type": "Drone_A",
        "capacity_kg": 10,
        "speed_kmh": 100,
        "range_km": 50,
        "battery_kwh": 2.0
    }, {
        "type": "Drone_B",
        "capacity_kg": 25,
        "speed_kmh": 80,
        "range_km": 40,
        "battery_kwh": 3.5
    }]
    pd.DataFrame(uav_specs).to_csv(f"{output_dir}/uav_specs.csv", index=False)
    print("Generated vehicle specs")

    # 5. Synthetic Demand (Time Series)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    demand_data = []
    for d in districts:
        base = d["base_demand"]
        trend = np.linspace(0, 20, 100)
        seasonality = 10 * np.sin(np.linspace(0, 3.14 * 4, 100))
        noise = np.random.normal(0, 5, 100)
        series = base + trend + seasonality + noise
        # Add a surge
        series[80:85] += 100 
        
        for date, val in zip(dates, series):
            demand_data.append({
                "date": date,
                "district_id": d["district_id"],
                "demand": max(0, int(val))
            })
    df_demand = pd.DataFrame(demand_data)
    df_demand.to_csv(f"{output_dir}/synthetic_demand.csv", index=False)
    print("Generated synthetic_demand.csv")

if __name__ == "__main__":
    generate_data("project/data")
