import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import (
    Vehicle, VehicleType, District, Warehouse, PublicRequest,
    RequestType, RequestStatus, Roadblock
)


# India districts with coordinates (Major cities across India)
DISTRICTS_DATA = [
    {"id": "DL01", "name": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090, "population": 16787941, "risk_level": "medium"},
    {"id": "MH01", "name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "population": 12442373, "risk_level": "high"},
    {"id": "KA01", "name": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "population": 8443675, "risk_level": "low"},
    {"id": "TN01", "name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "population": 7088000, "risk_level": "high"},
    {"id": "WB01", "name": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "population": 4496694, "risk_level": "high"},
    {"id": "TG01", "name": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "population": 6809970, "risk_level": "medium"},
    {"id": "MH02", "name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "population": 3124458, "risk_level": "medium"},
    {"id": "GJ01", "name": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "population": 5577940, "risk_level": "medium"},
    {"id": "GJ02", "name": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311, "population": 4467797, "risk_level": "high"},
    {"id": "RJ01", "name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "population": 3046163, "risk_level": "low"},
    {"id": "UP01", "name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "population": 2817105, "risk_level": "medium"},
    {"id": "UP02", "name": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319, "population": 2767031, "risk_level": "medium"},
    {"id": "UP03", "name": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739, "population": 1198491, "risk_level": "high"},
    {"id": "MP01", "name": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "population": 1960631, "risk_level": "low"},
    {"id": "MP02", "name": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "population": 1798218, "risk_level": "medium"},
    {"id": "KL01", "name": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673, "population": 677381, "risk_level": "high"},
    {"id": "OR01", "name": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245, "population": 837737, "risk_level": "high"},
    {"id": "PB01", "name": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794, "population": 1055450, "risk_level": "low"},
    {"id": "AS01", "name": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362, "population": 963429, "risk_level": "high"},
    {"id": "BR01", "name": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "population": 1684222, "risk_level": "high"},
]


def get_districts() -> List[District]:
    """Get list of all districts"""
    return [District(**d) for d in DISTRICTS_DATA]


def get_district_geojson() -> Dict[str, Any]:
    """Generate GeoJSON for district boundaries"""
    features = []
    for district in DISTRICTS_DATA:
        # Create a simple polygon around the district center
        offset = 0.5
        coordinates = [[
            [district["lng"] - offset, district["lat"] - offset],
            [district["lng"] + offset, district["lat"] - offset],
            [district["lng"] + offset, district["lat"] + offset],
            [district["lng"] - offset, district["lat"] + offset],
            [district["lng"] - offset, district["lat"] - offset],
        ]]
        
        features.append({
            "type": "Feature",
            "properties": {
                "id": district["id"],
                "name": district["name"],
                "state": district["state"],
                "population": district["population"],
                "risk_level": district["risk_level"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def get_warehouses() -> List[Warehouse]:
    """Get list of warehouses with stock levels"""
    warehouses = []
    for i, district in enumerate(DISTRICTS_DATA):
        warehouses.append(Warehouse(
            id=f"WH{i+1:03d}",
            name=f"{district['name']} Central Warehouse",
            district=district["id"],
            lat=district["lat"] + random.uniform(-0.1, 0.1),
            lng=district["lng"] + random.uniform(-0.1, 0.1),
            stocks={
                "food_packets": random.randint(1000, 10000),
                "water_bottles": random.randint(2000, 15000),
                "medicine_kits": random.randint(500, 5000),
                "blankets": random.randint(1000, 8000),
                "tents": random.randint(100, 1000),
            }
        ))
    return warehouses


# Global vehicle state (Vehicles across India)
VEHICLES = [
    Vehicle(
        id="TRK001",
        type=VehicleType.TRUCK,
        name="NDRF Relief Truck Delhi-1",
        lat=28.6139,
        lng=77.2090,
        status="in_transit",
        capacity=5000,
        current_load=3500,
        destination="Mumbai"
    ),
    Vehicle(
        id="TRK002",
        type=VehicleType.TRUCK,
        name="SDRF Maharashtra Truck-1",
        lat=19.0760,
        lng=72.8777,
        status="loading",
        capacity=5000,
        current_load=1200,
        destination="Pune"
    ),
    Vehicle(
        id="TRK003",
        type=VehicleType.TRUCK,
        name="Relief Truck Chennai-1",
        lat=13.0827,
        lng=80.2707,
        status="in_transit",
        capacity=4500,
        current_load=2800,
        destination="Bangalore"
    ),
    Vehicle(
        id="TRK004",
        type=VehicleType.TRUCK,
        name="Gujarat Relief Truck-1",
        lat=23.0225,
        lng=72.5714,
        status="idle",
        capacity=5000,
        current_load=0,
        destination=None
    ),
    Vehicle(
        id="TRK005",
        type=VehicleType.TRUCK,
        name="Hyderabad Supply Truck",
        lat=17.3850,
        lng=78.4867,
        status="in_transit",
        capacity=4800,
        current_load=4200,
        destination="Bhubaneswar"
    ),
    Vehicle(
        id="UAV001",
        type=VehicleType.UAV,
        name="NDRF Drone Alpha",
        lat=13.0827,
        lng=80.2707,
        status="in_transit",
        capacity=50,
        current_load=35,
        destination="Kochi"
    ),
    Vehicle(
        id="UAV002",
        type=VehicleType.UAV,
        name="Survey Drone Beta",
        lat=12.9716,
        lng=77.5946,
        status="idle",
        capacity=50,
        current_load=0,
        destination=None
    ),
    Vehicle(
        id="UAV003",
        type=VehicleType.UAV,
        name="Medical Drone Kolkata",
        lat=22.5726,
        lng=88.3639,
        status="in_transit",
        capacity=30,
        current_load=25,
        destination="Guwahati"
    ),
    Vehicle(
        id="UAV004",
        type=VehicleType.UAV,
        name="Relief Drone Mumbai",
        lat=19.0760,
        lng=72.8777,
        status="in_transit",
        capacity=40,
        current_load=30,
        destination="Surat"
    ),
    Vehicle(
        id="AMB001",
        type=VehicleType.AMBULANCE,
        name="108 Ambulance Kolkata-1",
        lat=22.5726,
        lng=88.3639,
        status="in_transit",
        capacity=4,
        current_load=2,
        destination="SSKM Hospital"
    ),
    Vehicle(
        id="AMB002",
        type=VehicleType.AMBULANCE,
        name="108 Ambulance Delhi-1",
        lat=28.6139,
        lng=77.2090,
        status="idle",
        capacity=4,
        current_load=0,
        destination=None
    ),
    Vehicle(
        id="AMB003",
        type=VehicleType.AMBULANCE,
        name="Emergency Ambulance Chennai",
        lat=13.0827,
        lng=80.2707,
        status="in_transit",
        capacity=4,
        current_load=3,
        destination="Apollo Hospital"
    ),
    Vehicle(
        id="AMB004",
        type=VehicleType.AMBULANCE,
        name="108 Ambulance Hyderabad",
        lat=17.3850,
        lng=78.4867,
        status="in_transit",
        capacity=4,
        current_load=1,
        destination="Gandhi Hospital"
    ),
    Vehicle(
        id="AMB005",
        type=VehicleType.AMBULANCE,
        name="Emergency Ambulance Patna",
        lat=25.5941,
        lng=85.1376,
        status="idle",
        capacity=4,
        current_load=0,
        destination=None
    ),
]


def get_vehicles() -> List[Vehicle]:
    """Get current vehicle positions"""
    return VEHICLES


def update_vehicle_positions():
    """Simulate vehicle movement"""
    for vehicle in VEHICLES:
        if vehicle.status == "in_transit":
            # Random walk simulation
            vehicle.lat += random.uniform(-0.01, 0.01)
            vehicle.lng += random.uniform(-0.01, 0.01)


# Public requests storage
PUBLIC_REQUESTS: List[PublicRequest] = [
    PublicRequest(
        id="REQ001",
        name="Rajesh Kumar",
        phone="+91-9876543210",
        location="Andheri East, Mumbai",
        lat=19.1136,
        lng=72.8697,
        request_type=RequestType.FOOD,
        description="Need food supplies for 20 people",
        urgency=4,
        status=RequestStatus.APPROVED,
        created_at=datetime.now() - timedelta(hours=2)
    ),
    PublicRequest(
        id="REQ002",
        name="Priya Sharma",
        phone="+91-9876543211",
        location="T Nagar, Chennai",
        lat=13.0418,
        lng=80.2341,
        request_type=RequestType.WATER,
        description="Urgent water needed for flooded area",
        urgency=5,
        status=RequestStatus.IN_PROGRESS,
        created_at=datetime.now() - timedelta(hours=1)
    ),
    PublicRequest(
        id="REQ003",
        name="Amit Patel",
        phone="+91-9876543212",
        location="Whitefield, Bangalore",
        lat=12.9698,
        lng=77.7499,
        request_type=RequestType.MEDICINE,
        description="Medical supplies needed",
        urgency=3,
        status=RequestStatus.PENDING,
        created_at=datetime.now() - timedelta(minutes=30)
    ),
]


def get_public_requests() -> List[PublicRequest]:
    """Get all public requests"""
    return PUBLIC_REQUESTS


def add_public_request(request: PublicRequest) -> PublicRequest:
    """Add a new public request"""
    request.id = f"REQ{len(PUBLIC_REQUESTS)+1:03d}"
    request.created_at = datetime.now()
    PUBLIC_REQUESTS.append(request)
    return request


# Roadblocks storage
ROADBLOCKS: List[Roadblock] = [
    Roadblock(
        id="RB001",
        location="NH48 near Panvel",
        lat=18.9894,
        lng=73.1102,
        severity="high",
        description="Road blocked due to landslide",
        reported_by="District Officer",
        created_at=datetime.now() - timedelta(hours=3)
    ),
    Roadblock(
        id="RB002",
        location="OMR Chennai",
        lat=12.9342,
        lng=80.2275,
        severity="medium",
        description="Waterlogging on main road",
        reported_by="Public",
        created_at=datetime.now() - timedelta(hours=1)
    ),
]


def get_roadblocks() -> List[Roadblock]:
    """Get all roadblocks"""
    return ROADBLOCKS


def add_roadblock(roadblock: Roadblock) -> Roadblock:
    """Add a new roadblock"""
    roadblock.id = f"RB{len(ROADBLOCKS)+1:03d}"
    roadblock.created_at = datetime.now()
    ROADBLOCKS.append(roadblock)
    return roadblock


def get_shelters() -> List[Dict[str, Any]]:
    """Get list of shelters across India"""
    shelters = []
    shelter_types = ["Community Hall", "Government School", "Sports Stadium", "Municipal Building", "Relief Camp"]
    
    for district in DISTRICTS_DATA:
        num_shelters = random.randint(3, 6)
        for i in range(num_shelters):
            shelter_type = random.choice(shelter_types)
            capacity = random.randint(200, 1000) if "Stadium" in shelter_type else random.randint(100, 500)
            occupancy = random.randint(int(capacity * 0.1), int(capacity * 0.7))
            
            # Determine facilities based on shelter type
            base_facilities = ["water", "food", "sanitation"]
            if shelter_type in ["Sports Stadium", "Municipal Building"]:
                base_facilities.extend(["medical", "electricity", "security"])
            elif shelter_type == "Government School":
                base_facilities.extend(["medical", "electricity"])
            else:
                base_facilities.append("medical")
            
            shelters.append({
                "id": f"SH{district['id']}{i+1:02d}",
                "name": f"{district['name']} {shelter_type} - Zone {i+1}",
                "district": district["id"],
                "lat": district["lat"] + random.uniform(-0.15, 0.15),
                "lng": district["lng"] + random.uniform(-0.15, 0.15),
                "capacity": capacity,
                "current_occupancy": occupancy,
                "facilities": base_facilities,
                "type": shelter_type
            })
    return shelters
