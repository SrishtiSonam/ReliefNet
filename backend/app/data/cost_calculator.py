# ─── cost_calculator.py ───────────────────────────────────────────────────────
"""Calculate truck and UAV costs using catchment + PIN code data."""
import math
from app.database import get_db

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Distance in km between two coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

async def compute_costs(district_name: str,
                         warehouse_lat: float, warehouse_lon: float,
                         district_lat: float,  district_lon: float) -> dict:
    """
    Truck cost  = road_distance × slope_factor × road_density_factor × base_cost_per_km
    UAV cost    = euclidean_distance × base_uav_cost_per_km
    """
    db = get_db()
    catchment = await db.catchment_characteristics.find_one({})  # Approximate

    road_density = catchment.get("road_density", 1.0) if catchment else 1.0
    ruggedness   = catchment.get("ruggedness_number", 1.0) if catchment else 1.0

    euclidean_dist = haversine(warehouse_lat, warehouse_lon, district_lat, district_lon)

    # Road distance approximated as 1.3× euclidean (standard factor for India roads)
    road_dist = euclidean_dist * 1.3

    # Normalize factors
    road_factor = max(0.5, 1.0 / (road_density + 1e-6))
    slope_factor = 1.0 + (ruggedness / 10.0)

    BASE_TRUCK_COST_PER_KM = 50.0   # INR per km
    BASE_UAV_COST_PER_KM   = 20.0

    truck_cost = road_dist  * BASE_TRUCK_COST_PER_KM * slope_factor * road_factor
    uav_cost   = euclidean_dist * BASE_UAV_COST_PER_KM

    return {
        "truck_cost":      round(truck_cost, 2),
        "uav_cost":        round(uav_cost,   2),
        "euclidean_km":    round(euclidean_dist, 2),
        "road_km":         round(road_dist, 2),
    }
