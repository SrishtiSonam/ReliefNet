"""
Main optimization engine orchestrator
Combines truck routing and UAV allocation for complete delivery plan
"""
from typing import List, Dict, Any
import json

from .vehicle_routing import optimize_truck_routes
from .uav_allocation import allocate_uavs


def optimize_delivery_plan(warehouses: List[Dict],
                           demand_points: List[Dict],
                           constraints: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate complete optimized delivery plan
    
    Combines:
    - Truck routing for bulk deliveries
    - UAV allocation for remote/urgent deliveries
    
    Args:
        warehouses: List of warehouse dictionaries
        demand_points: List of demand point dictionaries
        constraints: Optional constraints (avoid routes, disable UAVs, etc.)
    
    Returns:
        Complete delivery plan with routes and assignments
    """
    if constraints is None:
        constraints = {}
    
    # Separate demand points by suitability
    truck_demand_points = []
    uav_demand_points = []
    
    for dp in demand_points:
        total_demand = dp.get('total_demand_kg', 0)
        accessibility = dp.get('accessibility', 0.8)
        
        # UAV for small, remote deliveries
        if total_demand <= 50 and accessibility < 0.6:
            uav_demand_points.append(dp)
        else:
            truck_demand_points.append(dp)
    
    # Check constraints
    disable_uavs = constraints.get('disable_uavs', False)
    avoid_routes = constraints.get('avoid_routes', [])
    prioritize_medical = constraints.get('prioritize_medical', False)
    
    # Optimize truck routes
    truck_solution = {}
    if truck_demand_points and not constraints.get('disable_trucks', False):
        truck_solution = optimize_truck_routes(warehouses, truck_demand_points)
    
    # Allocate UAVs
    uav_solution = {}
    if uav_demand_points and not disable_uavs:
        uav_solution = allocate_uavs(warehouses, uav_demand_points)
    
    # Combine solutions
    delivery_plan = {
        'success': True,
        'truck_routes': truck_solution.get('routes', []),
        'uav_assignments': uav_solution.get('assignments', []),
        'summary': {
            'total_trucks_used': truck_solution.get('num_vehicles_used', 0),
            'total_uavs_used': uav_solution.get('num_uavs_used', 0),
            'total_distance_km': truck_solution.get('total_distance_km', 0),
            'total_load_kg': (
                truck_solution.get('total_load_kg', 0) +
                uav_solution.get('total_load_kg', 0)
            ),
            'demand_points_served': len(truck_demand_points) + len(uav_demand_points),
        },
        'constraints_applied': constraints,
        'depot': truck_solution.get('depot', {})
    }
    
    return delivery_plan


def recalculate_with_constraints(original_plan: Dict[str, Any],
                                 new_constraints: Dict[str, Any],
                                 warehouses: List[Dict],
                                 demand_points: List[Dict]) -> Dict[str, Any]:
    """
    Recalculate delivery plan with new constraints (human-in-the-loop)
    
    Args:
        original_plan: Original delivery plan
        new_constraints: New constraints to apply
        warehouses: Warehouse data
        demand_points: Demand point data
    
    Returns:
        Updated delivery plan
    """
    # Merge constraints
    all_constraints = original_plan.get('constraints_applied', {}).copy()
    all_constraints.update(new_constraints)
    
    # Re-optimize
    new_plan = optimize_delivery_plan(warehouses, demand_points, all_constraints)
    
    # Add metadata
    new_plan['recalculated'] = True
    new_plan['previous_plan_summary'] = original_plan.get('summary', {})
    
    return new_plan
