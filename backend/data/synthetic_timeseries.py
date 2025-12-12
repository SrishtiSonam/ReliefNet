"""
Synthetic Time Series Data Generator for TFT Training
Generates realistic disaster relief demand patterns for Indian districts
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_timeseries(
    num_districts=10,
    num_days=365,
    start_date='2023-01-01'
):
    """
    Generate synthetic time series data for disaster relief demand forecasting.
    
    Features:
    - Seasonality (monsoon patterns)
    - Trends
    - Disaster events (spikes in demand)
    - Multiple resource types
    """
    
    np.random.seed(42)
    
    districts = [
        'Mumbai', 'Delhi', 'Kolkata', 'Chennai', 'Bangalore',
        'Hyderabad', 'Ahmedabad', 'Pune', 'Jaipur', 'Lucknow'
    ][:num_districts]
    
    # Static features for each district
    district_info = {
        'Mumbai': {'population': 20_000_000, 'infrastructure': 0.8, 'coastal': 1},
        'Delhi': {'population': 19_000_000, 'infrastructure': 0.7, 'coastal': 0},
        'Kolkata': {'population': 14_000_000, 'infrastructure': 0.6, 'coastal': 1},
        'Chennai': {'population': 10_000_000, 'infrastructure': 0.7, 'coastal': 1},
        'Bangalore': {'population': 12_000_000, 'infrastructure': 0.8, 'coastal': 0},
        'Hyderabad': {'population': 10_000_000, 'infrastructure': 0.7, 'coastal': 0},
        'Ahmedabad': {'population': 8_000_000, 'infrastructure': 0.7, 'coastal': 0},
        'Pune': {'population': 7_000_000, 'infrastructure': 0.7, 'coastal': 0},
        'Jaipur': {'population': 3_000_000, 'infrastructure': 0.6, 'coastal': 0},
        'Lucknow': {'population': 3_000_000, 'infrastructure': 0.6, 'coastal': 0},
    }
    
    dates = pd.date_range(start=start_date, periods=num_days, freq='D')
    
    data = []
    
    for district in districts:
        pop = district_info[district]['population']
        infra = district_info[district]['infrastructure']
        coastal = district_info[district]['coastal']
        
        for i, date in enumerate(dates):
            # Time features
            day_of_year = date.dayofyear
            month = date.month
            
            # Seasonality (monsoon season: June-September)
            monsoon_factor = 1.0
            if 6 <= month <= 9:
                monsoon_factor = 2.0 + np.sin(day_of_year / 365 * 2 * np.pi)
            
            # Coastal areas get more monsoon impact
            if coastal:
                monsoon_factor *= 1.3
            
            # Base demand (proportional to population)
            base_demand = pop / 1_000_000 * 100
            
            # Trend (slight increase over time)
            trend = 1 + (i / num_days) * 0.1
            
            # Random disasters (5% chance per day)
            disaster_spike = 1.0
            if np.random.random() < 0.05:
                disaster_spike = np.random.uniform(2.0, 5.0)
            
            # Weather simulation
            rainfall = max(0, np.random.normal(
                50 * monsoon_factor, 
                30
            ))
            temperature = 25 + 10 * np.sin(day_of_year / 365 * 2 * np.pi) + np.random.normal(0, 3)
            
            # Resource demands
            food_demand = base_demand * trend * monsoon_factor * disaster_spike * np.random.uniform(0.8, 1.2)
            water_demand = base_demand * trend * monsoon_factor * disaster_spike * np.random.uniform(0.7, 1.3)
            medicine_demand = base_demand * 0.5 * trend * disaster_spike * np.random.uniform(0.6, 1.4)
            shelter_demand = base_demand * 0.3 * trend * disaster_spike * np.random.uniform(0.5, 1.5)
            
            data.append({
                'date': date,
                'district': district,
                'population': pop,
                'infrastructure': infra,
                'coastal': coastal,
                'rainfall': rainfall,
                'temperature': temperature,
                'food_demand': max(0, food_demand),
                'water_demand': max(0, water_demand),
                'medicine_demand': max(0, medicine_demand),
                'shelter_demand': max(0, shelter_demand),
                'disaster_event': 1 if disaster_spike > 1.5 else 0,
                'day_of_week': date.dayofweek,
                'month': month,
                'day_of_year': day_of_year,
            })
    
    df = pd.DataFrame(data)
    
    # Add time index for TFT
    df['time_idx'] = (df['date'] - df['date'].min()).dt.days
    
    return df

def save_training_data(output_path='data/tft_training_data.csv'):
    """Generate and save training data"""
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df = generate_synthetic_timeseries()
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows of training data")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Districts: {df['district'].nunique()}")
    return df

if __name__ == '__main__':
    df = save_training_data()
    print("\nSample data:")
    print(df.head(10))
