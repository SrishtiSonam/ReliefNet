from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from models import RoutingRequest, RoutingResponse

app = FastAPI(
    title="Routing Optimization Service",
    description="ML microservice for optimal route calculation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load distance matrix
# TODO: Replace with real distance/time matrix from your routing data
distance_matrix = None
try:
    distance_matrix = pd.read_csv('distance_matrix_placeholder.csv')
    print(f"✓ Loaded distance matrix with {len(distance_matrix)} routes")
except Exception as e:
    print(f"⚠ Warning: Could not load distance matrix: {e}")
    print("  Service will use fallback distance calculations")

def placeholder_route_calculation(from_district: str, to_district: str, vehicle_type: str, constraints: dict) -> RoutingResponse:
    """
    Placeholder routing function using simple distance matrix lookup.
    
    TODO: Replace this with actual routing optimization algorithm.
    Team Member 3 should:
    1. Implement advanced routing algorithm (A*, Dijkstra, or custom ML-based)
    2. Update distance_matrix_placeholder.csv with real road network data
    3. Consider traffic patterns, road conditions, vehicle constraints
    4. Replace this function with: route = routing_algorithm.find_optimal_path(...)
    """
    
    # Vehicle speed multipliers
    vehicle_speeds = {
        'truck': 1.0,
        'ambulance': 1.2,  # Faster due to priority
        'drone': 3.0  # Much faster, direct line
    }
    
    speed_multiplier = vehicle_speeds.get(vehicle_type.lower(), 1.0)
    
    # Try to find route in distance matrix
    if distance_matrix is not None:
        route_data = distance_matrix[
            (distance_matrix['from_district'].str.lower() == from_district.lower()) &
            (distance_matrix['to_district'].str.lower() == to_district.lower())
        ]
        
        if not route_data.empty:
            distance_km = float(route_data.iloc[0]['distance_km'])
            avg_speed = float(route_data.iloc[0]['avg_speed_kmh']) * speed_multiplier
            travel_time_min = (distance_km / avg_speed) * 60
            
            # Simple cost calculation: base rate + distance rate
            base_cost = {'truck': 500, 'ambulance': 800, 'drone': 1500}.get(vehicle_type.lower(), 500)
            cost = base_cost + (distance_km * 10)  # ₹10 per km
            
            return RoutingResponse(
                route=[from_district, to_district],  # Direct route for now
                travel_time_min=round(travel_time_min, 2),
                cost=round(cost, 2),
                distance_km=distance_km,
                model_version="placeholder-v1.0"
            )
    
    # Fallback: estimate based on district names
    # This is a very rough placeholder
    import hashlib
    hash_val = int(hashlib.md5(f"{from_district}{to_district}".encode()).hexdigest(), 16)
    
    distance_km = (hash_val % 800) + 100  # Random distance between 100-900 km
    avg_speed = 65 * speed_multiplier
    travel_time_min = (distance_km / avg_speed) * 60
    
    base_cost = {'truck': 500, 'ambulance': 800, 'drone': 1500}.get(vehicle_type.lower(), 500)
    cost = base_cost + (distance_km * 10)
    
    # Generate intermediate waypoint for realism
    waypoints = ["Waypoint-1"] if distance_km > 200 else []
    route = [from_district] + waypoints + [to_district]
    
    return RoutingResponse(
        route=route,
        travel_time_min=round(travel_time_min, 2),
        cost=round(cost, 2),
        distance_km=float(distance_km),
        model_version="placeholder-v1.0-fallback"
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "routing_service",
        "status": "healthy",
        "version": "1.0.0",
        "distance_matrix_loaded": distance_matrix is not None,
        "routes_available": len(distance_matrix) if distance_matrix is not None else 0,
        "endpoints": {
            "routing": "POST /routing/optimal-route"
        }
    }

@app.post("/routing/optimal-route", response_model=RoutingResponse)
async def calculate_optimal_route(request: RoutingRequest):
    """
    Calculate optimal route between two districts.
    
    Args:
        request: RoutingRequest with from_district, to_district, vehicle_type, constraints
    
    Returns:
        RoutingResponse with route, travel time, cost, and distance
    """
    try:
        # TODO: Implement advanced routing algorithm
        # route_result = routing_algorithm.calculate(
        #     start=request.from_district,
        #     end=request.to_district,
        #     vehicle=request.vehicle_type,
        #     constraints=request.constraints
        # )
        
        # Using placeholder calculation for now
        result = placeholder_route_calculation(
            from_district=request.from_district,
            to_district=request.to_district,
            vehicle_type=request.vehicle_type,
            constraints=request.constraints
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Routing calculation error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
