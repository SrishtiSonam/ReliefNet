"""
Quick Setup Script for ReliefNet Demo System
Initializes database and verifies all components
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

print("=" * 60)
print("ReliefNet Interactive ML Demo System - Setup")
print("=" * 60)
print()

# Step 1: Initialize Database
print("Step 1: Initializing SQLite Database...")
try:
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    print(" Database created successfully!")
    print(f"   Location: {db.db_path}")
except Exception as e:
    print(f Database initialization failed: {e}")
    sys.exit(1)

# Step 2: Verify Tables
print("\nStep 2: Verifying Database Tables...")
try:
    warehouses = db.get_warehouse_stock()
    requests = db.get_public_requests(limit=5)
    blockages = db.get_road_blockages()
    vehicles = db.get_vehicles()
    
    print(f" Found {len(warehouses)} warehouses")
    print(f" Found {len(requests)} public requests")
    print(f" Found {len(blockages)} road blockages")
    print(f" Found {len(vehicles)} vehicles")
except Exception as e:
    print(f" Table verification failed: {e}")
    sys.exit(1)

# Step 3: Test Mock ML Logic
print("\nStep 3: Testing Mock ML Logic...")
try:
    from mock_ml_logic import (
        ensemble_forecast,
        allocate_resources,
        generate_shap_explanation,
        calculate_vfa_score
    )
    
    # Test forecasting
    forecast = ensemble_forecast('Mumbai', days=7)
    print(f" Forecasting works - {forecast['forecast_days']} day forecast generated")
    
    # Test VFA
    state = {
        'inventory': {'food': 10000, 'water': 20000},
        'demand': {'food': 8000, 'water': 15000},
        'resources': {'trucks': 5, 'uavs': 10},
        'urgency': 0.6,
        'accessibility': 0.7
    }
    vfa_score, _ = calculate_vfa_score(state)
    print(f" VFA calculation works - Score: {vfa_score}")
    
    # Test allocation
    districts = [
        {
            'name': 'Mumbai',
            'demand_kg': 8000,
            'urgency': 0.9,
            'accessibility': 0.6,
            'population': 1200000,
            'hours_deprived': 48
        }
    ]
    stock = {'food': 15000, 'water': 30000, 'medical': 2000}
    allocations = allocate_resources(districts, stock)
    print(f" Allocation works - {len(allocations)} allocations generated")
    
except Exception as e:
    print(f" ML logic test failed: {e}")
    sys.exit(1)

# Step 4: Display Sample Data
print("\nStep 4: Sample Data Preview...")
print("\n Warehouses (India):")
for wh in warehouses[:3]:
    print(f"   - {wh['warehouse_name']}, {wh['district']}, {wh['state']}")
    print(f"     Stock: {wh['food_kg']}kg food, {wh['water_liters']}L water")

print("\n Public Requests:")
for req in requests[:3]:
    print(f"   - {req['name']} from {req['district']}")
    print(f"     Needs: {req['resource_type']} (Severity: {req['severity_level']})")

print("\n🚧 Road Blockages:")
for block in blockages[:3]:
    print(f"   - {block['location']}, {block['district']}")
    print(f"     Reason: {block['reason']} (Severity: {block['severity']})")

# Final Summary
print("\n" + "=" * 60)
print(" Setup Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Start Backend:")
print("   cd backend")
print("   python main.py")
print("\n2. Start Frontend (in new terminal):")
print("   cd frontend")
print("   npm run dev")
print("\n3. Open Browser:")
print("   http://localhost:5173")
print("\n" + "=" * 60)
print(" Read DEMO_GUIDE.md for interactive tutorials!")
print("=" * 60)
