"""
Quick initialization script for ReliefNet backend
Creates necessary directories and sample data files
"""
import os
from pathlib import Path
import json

# Create directories
dirs = [
    "data/processed",
    "backend/models",
]

for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {dir_path}")

# Create sample processed data files
processed_dir = Path("data/processed")

# Sample demand history
import csv
from datetime import datetime, timedelta

demand_history = []
start_date = datetime(2023, 1, 1)
for i in range(365):
    date = start_date + timedelta(days=i)
    demand_history.append({
        'date': date.strftime('%Y-%m-%d'),
        'food_demand_kg': 5000 + i * 10,
        'water_demand_liters': 10000 + i * 20,
        'medicine_demand_units': 500 + i,
        'shelter_demand_units': 200 + i // 2,
        'active_disasters': 1 if i % 30 < 5 else 0,
        'total_affected': 10000 if i % 30 < 5 else 1000
    })

with open(processed_dir / "demand_history.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=demand_history[0].keys())
    writer.writeheader()
    writer.writerows(demand_history)

print(f"✓ Created demand_history.csv with {len(demand_history)} records")

# Sample warehouses
warehouses = [
    {'warehouse_id': 'WH001', 'wheat_kg': 5000, 'rice_kg': 4000, 'tents_units': 200,
     'blankets_units': 500, 'medicines_units': 300, 'latitude': 19.0760, 'longitude': 72.8777},
    {'warehouse_id': 'WH002', 'wheat_kg': 3000, 'rice_kg': 3500, 'tents_units': 150,
     'blankets_units': 400, 'medicines_units': 250, 'latitude': 28.7041, 'longitude': 77.1025},
    {'warehouse_id': 'WH003', 'wheat_kg': 4000, 'rice_kg': 3000, 'tents_units': 180,
     'blankets_units': 450, 'medicines_units': 280, 'latitude': 13.0827, 'longitude': 80.2707},
]

with open(processed_dir / "warehouses.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=warehouses[0].keys())
    writer.writeheader()
    writer.writerows(warehouses)

print(f"✓ Created warehouses.csv with {len(warehouses)} warehouses")

# Sample historical disasters
disasters = []
for i in range(100):
    date = start_date + timedelta(days=i*3)
    disasters.append({
        'date': date.strftime('%Y-%m-%d'),
        'disaster_type': 'Flood' if i % 2 == 0 else 'Cyclone',
        'disaster_subtype': 'Heavy Rain',
        'total_deaths': i % 10,
        'total_affected': 1000 * (i % 20 + 1),
        'location': 'Mumbai' if i % 3 == 0 else 'Delhi'
    })

with open(processed_dir / "historical_disasters.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=disasters[0].keys())
    writer.writeheader()
    writer.writerows(disasters)

print(f"✓ Created historical_disasters.csv with {len(disasters)} records")

# Create empty placeholder files
for filename in ['flood_risk_scores.csv', 'district_metadata.csv', 'delivery_patterns.csv']:
    (processed_dir / filename).touch()
    print(f"✓ Created {filename}")

print("\n" + "="*60)
print("Initialization complete!")
print("="*60)
print("\nNext steps:")
print("1. Install dependencies: pip install -r backend/requirements.txt")
print("2. Run preprocessing (optional): python backend/data_processing/preprocessing_scripts.py")
print("3. Start backend: python backend/main.py")
