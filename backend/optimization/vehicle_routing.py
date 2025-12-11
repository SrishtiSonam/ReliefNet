"""
Vehicle Routing Problem (VRP) solver using OR-Tools
Optimizes truck routes for bulk resource delivery
"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from typing import List, Dict, Any, Tuple

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import OPTIMIZATION_CONFIG


def create_distance_matrix(locations: List[Tuple[float, float]]) -> np.ndarray:
    """
    Create distance matrix from locations using haversine formula
    
    Args:
        locations: List of (lat, lng) tuples
    
    Returns:
        Distance matrix in km
    """
    n = len(locations)
    distances = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = locations[i]
                lat2, lon2 = locations[j]
                
                # Haversine formula
                R = 6371  # Earth radius in km
                dlat = np.radians(lat2 - lat1)
                dlon = np.radians(lon2 - lon1)
                
                a = (np.sin(dlat/2)**2 + 
                     np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
                     np.sin(dlon/2)**2)
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                distances[i][j] = R * c
    
    return distances


def solve_vrp(depot_location: Tuple[float, float],
              delivery_locations: List[Tuple[float, float]],
              demands: List[float],
              num_vehicles: int = 5,
              vehicle_capacity: float = None) -> Dict[str, Any]:
    """
    Solve Vehicle Routing Problem with capacity constraints
    
    Args:
        depot_location: (lat, lng) of warehouse/depot
        delivery_locations: List of (lat, lng) for delivery points
        demands: List of demand quantities at each location
        num_vehicles: Number of trucks available
        vehicle_capacity: Truck capacity in kg
    
    Returns:
        Dictionary with routes and metrics
    """
    if vehicle_capacity is None:
        vehicle_capacity = OPTIMIZATION_CONFIG['truck_capacity_kg']
    
    # Create locations list (depot first)
    locations = [depot_location] + delivery_locations
    
    # Create distance matrix (convert to meters for OR-Tools)
    distance_matrix = (create_distance_matrix(locations) * 1000).astype(int)
    
    # Create demands array (depot has 0 demand)
    demands_array = [0] + demands
    
    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(locations),
        num_vehicles,
        0  # Depot index
    )
    
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)
    
    # Create distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Add capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(demands_array[from_node])
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [int(vehicle_capacity)] * num_vehicles,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity'
    )
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = OPTIMIZATION_CONFIG['time_limit_seconds']
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        return {
            'success': False,
            'routes': [],
            'total_distance_km': 0,
            'message': 'No solution found'
        }
    
    # Extract routes
    routes = []
    total_distance = 0
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = {
            'vehicle_id': vehicle_id,
            'vehicle_type': 'truck',
            'stops': [],
            'distance_km': 0,
            'load_kg': 0
        }
        
        route_distance = 0
        route_load = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            
            if node_index > 0:  # Skip depot
                route['stops'].append({
                    'location_index': node_index - 1,  # Adjust for depot
                    'location': delivery_locations[node_index - 1],
                    'demand_kg': demands[node_index - 1]
                })
                route_load += demands[node_index - 1]
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        
        route['distance_km'] = route_distance / 1000  # Convert to km
        route['load_kg'] = route_load
        
        if route['stops']:  # Only include routes with deliveries
            routes.append(route)
            total_distance += route_distance
    
    return {
        'success': True,
        'routes': routes,
        'total_distance_km': total_distance / 1000,
        'num_vehicles_used': len(routes),
        'total_load_kg': sum(r['load_kg'] for r in routes)
    }


def optimize_truck_routes(warehouses: List[Dict], 
                          demand_points: List[Dict]) -> Dict[str, Any]:
    """
    High-level function to optimize truck routes
    
    Args:
        warehouses: List of warehouse dictionaries with lat/lng
        demand_points: List of demand point dictionaries with lat/lng and demand
    
    Returns:
        Optimized routing solution
    """
    if not warehouses or not demand_points:
        return {
            'success': False,
            'routes': [],
            'message': 'No warehouses or demand points provided'
        }
    
    # Use first warehouse as depot (can be extended to multi-depot)
    depot = warehouses[0]
    depot_location = (depot.get('latitude', 20.5937), depot.get('longitude', 78.9629))
    
    # Extract delivery locations and demands
    delivery_locations = [
        (dp.get('latitude', 20.5937), dp.get('longitude', 78.9629))
        for dp in demand_points
    ]
    
    demands = [
        dp.get('total_demand_kg', 1000)
        for dp in demand_points
    ]
    
    # Solve VRP
    solution = solve_vrp(
        depot_location=depot_location,
        delivery_locations=delivery_locations,
        demands=demands,
        num_vehicles=min(len(demand_points), OPTIMIZATION_CONFIG['max_vehicles'])
    )
    
    # Add warehouse info to solution
    solution['depot'] = {
        'warehouse_id': depot.get('warehouse_id', 'WH001'),
        'location': depot_location
    }
    
    # Calculate ETAs
    truck_speed = OPTIMIZATION_CONFIG['truck_speed_kmh']
    for route in solution.get('routes', []):
        route['estimated_time_hours'] = route['distance_km'] / truck_speed
    
    return solution
