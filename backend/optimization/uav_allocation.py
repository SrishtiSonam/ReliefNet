"""
UAV (Unmanned Aerial Vehicle) allocation for remote/inaccessible areas
Assigns drones to high-priority, low-volume deliveries
"""
import numpy as np
from typing import List, Dict, Any, Tuple

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import OPTIMIZATION_CONFIG


def calculate_priority_score(demand_point: Dict) -> float:
    """
    Calculate priority score for UAV assignment
    
    Higher priority for:
    - Remote/inaccessible locations
    - Medical supplies
    - High urgency
    
    Args:
        demand_point: Demand point dictionary
    
    Returns:
        Priority score (0-1, higher is more urgent)
    """
    score = 0.0
    
    # Accessibility (lower = higher priority for UAV)
    accessibility = demand_point.get('accessibility', 0.5)
    score += (1 - accessibility) * 0.4
    
    # Medical demand (high priority)
    medical_demand = demand_point.get('medicine_demand_units', 0)
    if medical_demand > 0:
        score += 0.3
    
    # Urgency
    urgency = demand_point.get('urgency', 0.5)
    score += urgency * 0.3
    
    return min(score, 1.0)


def allocate_uavs(warehouses: List[Dict],
                  demand_points: List[Dict],
                  num_uavs: int = None) -> Dict[str, Any]:
    """
    Allocate UAVs to demand points
    
    Strategy:
    1. Filter demand points suitable for UAV (small demand, remote)
    2. Prioritize by urgency and accessibility
    3. Assign UAVs to top priority points within range
    
    Args:
        warehouses: List of warehouse dictionaries
        demand_points: List of demand point dictionaries
        num_uavs: Number of available UAVs
    
    Returns:
        UAV allocation plan
    """
    if num_uavs is None:
        num_uavs = OPTIMIZATION_CONFIG['uav_capacity_kg']
    
    if not warehouses or not demand_points:
        return {
            'success': False,
            'assignments': [],
            'message': 'No warehouses or demand points'
        }
    
    uav_capacity = OPTIMIZATION_CONFIG['uav_capacity_kg']
    uav_range = OPTIMIZATION_CONFIG['uav_range_km']
    
    # Use first warehouse as base
    base = warehouses[0]
    base_location = (base.get('latitude', 20.5937), base.get('longitude', 78.9629))
    
    # Filter and score demand points for UAV suitability
    uav_candidates = []
    
    for dp in demand_points:
        total_demand = dp.get('total_demand_kg', 0)
        
        # UAV suitable if demand is small
        if total_demand > 0 and total_demand <= uav_capacity:
            dp_location = (dp.get('latitude', 20.5937), dp.get('longitude', 78.9629))
            
            # Calculate distance
            distance = haversine_distance(base_location, dp_location)
            
            # Check if within range
            if distance <= uav_range:
                priority = calculate_priority_score(dp)
                
                uav_candidates.append({
                    'demand_point': dp,
                    'location': dp_location,
                    'distance_km': distance,
                    'demand_kg': total_demand,
                    'priority': priority
                })
    
    # Sort by priority (descending)
    uav_candidates.sort(key=lambda x: x['priority'], reverse=True)
    
    # Assign UAVs
    assignments = []
    uavs_used = 0
    
    for candidate in uav_candidates:
        if uavs_used >= num_uavs:
            break
        
        uav_speed = OPTIMIZATION_CONFIG['uav_speed_kmh']
        flight_time = candidate['distance_km'] / uav_speed
        
        assignments.append({
            'uav_id': f'UAV{uavs_used + 1:03d}',
            'base_warehouse': base.get('warehouse_id', 'WH001'),
            'destination': candidate['demand_point'].get('zone_id', f'ZONE{uavs_used}'),
            'location': candidate['location'],
            'distance_km': candidate['distance_km'],
            'load_kg': candidate['demand_kg'],
            'priority': candidate['priority'],
            'estimated_flight_time_hours': flight_time,
            'round_trip_time_hours': flight_time * 2
        })
        
        uavs_used += 1
    
    return {
        'success': True,
        'assignments': assignments,
        'num_uavs_used': uavs_used,
        'total_load_kg': sum(a['load_kg'] for a in assignments),
        'average_priority': np.mean([a['priority'] for a in assignments]) if assignments else 0
    }


def haversine_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """
    Calculate haversine distance between two lat/lng points
    
    Args:
        loc1: (lat, lng) tuple
        loc2: (lat, lng) tuple
    
    Returns:
        Distance in km
    """
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    
    a = (np.sin(dlat/2)**2 + 
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
         np.sin(dlon/2)**2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c
