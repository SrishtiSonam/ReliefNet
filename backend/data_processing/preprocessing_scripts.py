"""
Data preprocessing scripts for ReliefNet
Processes real-world datasets from data/raw into clean formats for ML models
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_DISASTER_PATH, RAW_WAREHOUSE_PATH, RAW_FLOOD_RISK_PATH,
    RAW_FLOODS_INVENTORY_PATH, RAW_DELIVERY_LOGISTICS_PATH,
    RAW_EMERGENCY_ROUTING_PATH, RAW_DISTRICT_POINTS_PATH,
    DEMAND_HISTORY_PATH, WAREHOUSES_PATH, FLOOD_RISK_PATH,
    HISTORICAL_DISASTERS_PATH, DELIVERY_PATTERNS_PATH,
    DISTRICT_METADATA_PATH, PROCESSED_DATA_DIR
)


def preprocess_disaster_data():
    """
    Process disasterIND.csv to extract historical disaster patterns
    Creates time series of disaster events for forecasting
    """
    print("Processing disaster inventory data...")
    
    try:
        # Read disaster data
        df = pd.read_csv(RAW_DISASTER_PATH, encoding='latin1', low_memory=False)
        
        # Clean and extract relevant columns
        # Typical columns: DisNo, Start Date, End Date, Disaster Type, Location, etc.
        disaster_records = []
        
        for idx, row in df.iterrows():
            try:
                # Extract date information
                start_date = pd.to_datetime(row.get('Start Date', None), errors='coerce')
                if pd.isna(start_date):
                    continue
                    
                disaster_records.append({
                    'date': start_date,
                    'disaster_type': str(row.get('Disaster Type', 'Unknown')),
                    'disaster_subtype': str(row.get('Disaster Subtype', 'Unknown')),
                    'total_deaths': pd.to_numeric(row.get('Total Deaths', 0), errors='coerce') or 0,
                    'total_affected': pd.to_numeric(row.get('Total Affected', 0), errors='coerce') or 0,
                    'location': str(row.get('Location', 'Unknown'))
                })
            except Exception as e:
                continue
        
        # Create DataFrame
        disasters_df = pd.DataFrame(disaster_records)
        disasters_df = disasters_df.sort_values('date')
        
        # Save processed data
        disasters_df.to_csv(HISTORICAL_DISASTERS_PATH, index=False)
        print(f"✓ Saved {len(disasters_df)} disaster records to {HISTORICAL_DISASTERS_PATH}")
        
        return disasters_df
        
    except Exception as e:
        print(f"✗ Error processing disaster data: {e}")
        # Create empty placeholder
        pd.DataFrame(columns=['date', 'disaster_type', 'total_affected']).to_csv(
            HISTORICAL_DISASTERS_PATH, index=False
        )
        return None


def preprocess_warehouse_data():
    """
    Process Warehouse_Data.csv to extract warehouse locations and inventory
    """
    print("Processing warehouse data...")
    
    try:
        df = pd.read_csv(RAW_WAREHOUSE_PATH, low_memory=False)
        
        # Extract and clean warehouse information
        warehouses = []
        
        for idx, row in df.iterrows():
            try:
                warehouse_id = row.get('Warehouse_ID', f'WH{idx:03d}')
                
                warehouses.append({
                    'warehouse_id': warehouse_id,
                    'wheat_kg': pd.to_numeric(row.get('Wheat_kg', 0), errors='coerce') or 0,
                    'rice_kg': pd.to_numeric(row.get('Rice_kg', 0), errors='coerce') or 0,
                    'tents_units': pd.to_numeric(row.get('Tents_units', 0), errors='coerce') or 0,
                    'blankets_units': pd.to_numeric(row.get('Blankets_units', 0), errors='coerce') or 0,
                    'medicines_units': pd.to_numeric(row.get('Medicines_units', 0), errors='coerce') or 0,
                    'source_type': row.get('Source_Type', 'Warehouse'),
                    'latitude': pd.to_numeric(row.get('Latitude', 20.5937), errors='coerce') or 20.5937,
                    'longitude': pd.to_numeric(row.get('Longitude', 78.9629), errors='coerce') or 78.9629,
                })
            except Exception as e:
                continue
        
        warehouses_df = pd.DataFrame(warehouses)
        warehouses_df.to_csv(WAREHOUSES_PATH, index=False)
        print(f"✓ Saved {len(warehouses_df)} warehouses to {WAREHOUSES_PATH}")
        
        return warehouses_df
        
    except Exception as e:
        print(f"✗ Error processing warehouse data: {e}")
        # Create sample data
        sample_warehouses = pd.DataFrame([
            {'warehouse_id': 'WH001', 'wheat_kg': 5000, 'rice_kg': 4000, 'tents_units': 200,
             'blankets_units': 500, 'medicines_units': 300, 'latitude': 19.0760, 'longitude': 72.8777},
            {'warehouse_id': 'WH002', 'wheat_kg': 3000, 'rice_kg': 3500, 'tents_units': 150,
             'blankets_units': 400, 'medicines_units': 250, 'latitude': 28.7041, 'longitude': 77.1025},
        ])
        sample_warehouses.to_csv(WAREHOUSES_PATH, index=False)
        return sample_warehouses


def preprocess_flood_risk_data():
    """
    Process flood_risk_dataset_india.csv to extract risk scores and features
    """
    print("Processing flood risk data...")
    
    try:
        df = pd.read_csv(RAW_FLOOD_RISK_PATH, low_memory=False)
        
        # Extract relevant features for forecasting
        flood_risk_records = []
        
        for idx, row in df.iterrows():
            try:
                flood_risk_records.append({
                    'latitude': pd.to_numeric(row.get('Latitude', 0), errors='coerce'),
                    'longitude': pd.to_numeric(row.get('Longitude', 0), errors='coerce'),
                    'rainfall_mm': pd.to_numeric(row.get('Rainfall (mm)', 0), errors='coerce'),
                    'temperature_c': pd.to_numeric(row.get('Temperature (C)', 25), errors='coerce'),
                    'humidity': pd.to_numeric(row.get('Humidity (%)', 60), errors='coerce'),
                    'elevation_m': pd.to_numeric(row.get('Elevation (m)', 0), errors='coerce'),
                    'flood_risk_score': pd.to_numeric(row.get('Flood Risk', 0), errors='coerce'),
                    'terrain_type': row.get('Terrain Type', 'Unknown'),
                })
            except Exception as e:
                continue
        
        flood_risk_df = pd.DataFrame(flood_risk_records)
        flood_risk_df.to_csv(FLOOD_RISK_PATH, index=False)
        print(f"✓ Saved {len(flood_risk_df)} flood risk records to {FLOOD_RISK_PATH}")
        
        return flood_risk_df
        
    except Exception as e:
        print(f"✗ Error processing flood risk data: {e}")
        return None


def preprocess_delivery_logistics():
    """
    Process Delivery_Logistics.csv to extract demand patterns
    """
    print("Processing delivery logistics data...")
    
    try:
        df = pd.read_csv(RAW_DELIVERY_LOGISTICS_PATH, low_memory=False)
        
        # Extract delivery patterns
        delivery_records = []
        
        for idx, row in df.iterrows():
            try:
                delivery_records.append({
                    'delivery_id': row.get('Delivery_ID', f'DEL{idx:05d}'),
                    'origin': row.get('Origin', 'Unknown'),
                    'destination': row.get('Destination', 'Unknown'),
                    'distance_km': pd.to_numeric(row.get('Distance_km', 0), errors='coerce'),
                    'delivery_time_hours': pd.to_numeric(row.get('Delivery_Time_hours', 0), errors='coerce'),
                    'vehicle_type': row.get('Vehicle_Type', 'Truck'),
                    'cargo_weight_kg': pd.to_numeric(row.get('Cargo_Weight_kg', 0), errors='coerce'),
                })
            except Exception as e:
                continue
        
        delivery_df = pd.DataFrame(delivery_records)
        delivery_df.to_csv(DELIVERY_PATTERNS_PATH, index=False)
        print(f"✓ Saved {len(delivery_df)} delivery records to {DELIVERY_PATTERNS_PATH}")
        
        return delivery_df
        
    except Exception as e:
        print(f"✗ Error processing delivery logistics: {e}")
        return None


def create_demand_history():
    """
    Create demand history time series from disaster and logistics data
    This is used for training forecasting models
    """
    print("Creating demand history time series...")
    
    try:
        # Load processed disaster data
        disasters_df = pd.read_csv(HISTORICAL_DISASTERS_PATH)
        disasters_df['date'] = pd.to_datetime(disasters_df['date'])
        
        # Create daily demand time series
        start_date = disasters_df['date'].min()
        end_date = datetime.now()
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        demand_history = []
        
        for date in date_range:
            # Find disasters within 30 days of this date
            recent_disasters = disasters_df[
                (disasters_df['date'] >= date - timedelta(days=30)) &
                (disasters_df['date'] <= date)
            ]
            
            # Calculate demand based on affected population
            total_affected = recent_disasters['total_affected'].sum()
            
            # Estimate resource demand (simplified model)
            food_demand = int(total_affected * 0.5)  # 0.5 kg per person per day
            water_demand = int(total_affected * 2.0)  # 2 liters per person per day
            medicine_demand = int(total_affected * 0.1)  # 10% need medicine
            shelter_demand = int(total_affected * 0.3)  # 30% need shelter
            
            demand_history.append({
                'date': date,
                'food_demand_kg': food_demand,
                'water_demand_liters': water_demand,
                'medicine_demand_units': medicine_demand,
                'shelter_demand_units': shelter_demand,
                'active_disasters': len(recent_disasters),
                'total_affected': total_affected,
            })
        
        demand_df = pd.DataFrame(demand_history)
        demand_df.to_csv(DEMAND_HISTORY_PATH, index=False)
        print(f"✓ Created demand history with {len(demand_df)} days of data")
        
        return demand_df
        
    except Exception as e:
        print(f"✗ Error creating demand history: {e}")
        # Create sample demand history
        dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
        sample_demand = pd.DataFrame({
            'date': dates,
            'food_demand_kg': np.random.randint(1000, 10000, len(dates)),
            'water_demand_liters': np.random.randint(2000, 20000, len(dates)),
            'medicine_demand_units': np.random.randint(100, 1000, len(dates)),
            'shelter_demand_units': np.random.randint(50, 500, len(dates)),
        })
        sample_demand.to_csv(DEMAND_HISTORY_PATH, index=False)
        return sample_demand


def preprocess_all():
    """
    Run all preprocessing steps
    """
    print("=" * 60)
    print("ReliefNet Data Preprocessing Pipeline")
    print("=" * 60)
    
    # Process each dataset
    disasters_df = preprocess_disaster_data()
    warehouses_df = preprocess_warehouse_data()
    flood_risk_df = preprocess_flood_risk_data()
    delivery_df = preprocess_delivery_logistics()
    
    # Create derived datasets
    demand_df = create_demand_history()
    
    print("\n" + "=" * 60)
    print("Preprocessing Complete!")
    print("=" * 60)
    print(f"\nProcessed files saved to: {PROCESSED_DATA_DIR}")
    print("\nSummary:")
    print(f"  - Historical disasters: {len(disasters_df) if disasters_df is not None else 0} records")
    print(f"  - Warehouses: {len(warehouses_df) if warehouses_df is not None else 0} locations")
    print(f"  - Flood risk data: {len(flood_risk_df) if flood_risk_df is not None else 0} records")
    print(f"  - Delivery patterns: {len(delivery_df) if delivery_df is not None else 0} records")
    print(f"  - Demand history: {len(demand_df) if demand_df is not None else 0} days")
    

if __name__ == "__main__":
    preprocess_all()
