from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import json
from datetime import datetime

from models import (
    PublicRequest, Roadblock, Vehicle, District, UserRole,
    AllocationRequest, RequestStatus
)
from mock_data import (
    get_districts, get_district_geojson, get_warehouses,
    get_vehicles, update_vehicle_positions, get_public_requests,
    add_public_request, get_roadblocks, add_roadblock, get_shelters
)
from ai_placeholders import (
    forecast, optimize_allocation, explain_allocation,
    simulate_vehicle_movements, validate_public_request,
    generate_mission_plan
)


app = FastAPI(
    title="Disaster Management Platform API",
    description="Multi-role disaster management system for India",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Disaster Management Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/dashboard")
async def get_dashboard(role: UserRole = Query(..., description="User role")):
    """
    Get dashboard data based on user role
    
    - **state_admin**: State-level overview with all districts
    - **district_admin**: District-specific data
    - **public**: Public-facing information
    """
    districts = get_districts()
    warehouses = get_warehouses()
    vehicles = get_vehicles()
    
    if role == UserRole.STATE_ADMIN:
        return {
            "role": role,
            "districts": [d.dict() for d in districts],
            "warehouses": [w.dict() for w in warehouses],
            "vehicles": [v.dict() for v in vehicles],
            "total_requests": len(get_public_requests()),
            "active_missions": len([v for v in vehicles if v.status == "in_transit"]),
            "total_roadblocks": len(get_roadblocks()),
            "timestamp": datetime.now().isoformat()
        }
    
    elif role == UserRole.DISTRICT_ADMIN:
        # For demo, return first district
        district = districts[0]
        district_warehouses = [w for w in warehouses if w.district == district.id]
        district_requests = [r for r in get_public_requests() if district.name in r.location]
        
        return {
            "role": role,
            "district": district.dict(),
            "warehouses": [w.dict() for w in district_warehouses],
            "requests": [r.dict() for r in district_requests],
            "roadblocks": [r.dict() for r in get_roadblocks()],
            "timestamp": datetime.now().isoformat()
        }
    
    else:  # PUBLIC
        return {
            "role": role,
            "shelters": get_shelters(),
            "active_alerts": [
                {
                    "id": "ALT001",
                    "type": "weather",
                    "severity": "high",
                    "message": "Heavy rainfall expected in coastal areas",
                    "issued_at": datetime.now().isoformat()
                }
            ],
            "safety_guidelines": [
                "Stay indoors during heavy rainfall",
                "Keep emergency supplies ready",
                "Follow official evacuation orders",
                "Avoid flooded areas"
            ],
            "timestamp": datetime.now().isoformat()
        }


@app.get("/forecast")
async def get_forecast(
    district: str = Query("Mumbai", description="District name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast")
):
    """
    Get surge forecast for a district
    
    Uses AI/ML placeholder to predict resource demand
    """
    forecast_data = forecast(district, days)
    return forecast_data.dict()


@app.post("/optimize_allocation")
async def optimize_resource_allocation(request: AllocationRequest):
    """
    Optimize resource allocation using AI
    
    Returns optimal distribution across warehouses
    """
    result = optimize_allocation(request)
    return result.dict()


@app.get("/explain_allocation")
async def get_allocation_explanation(
    district_id: str = Query(..., description="District ID")
):
    """
    Get explainable AI insights for allocation decisions
    
    Provides SHAP-style feature importance and natural language explanation
    """
    # Mock allocation data
    allocation = {
        "district_id": district_id,
        "resources": {"food": 5000, "water": 10000}
    }
    
    explanation = explain_allocation(district_id, allocation)
    return explanation.dict()


@app.get("/public_requests", response_model=List[PublicRequest])
async def list_public_requests(
    status: Optional[RequestStatus] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get list of public relief requests
    
    Optionally filter by status
    """
    requests = get_public_requests()
    
    if status:
        requests = [r for r in requests if r.status == status]
    
    return requests[:limit]


@app.post("/public_requests", response_model=PublicRequest)
async def create_public_request(request: PublicRequest):
    """
    Submit a new public relief request
    
    Validates and stores the request
    """
    # Validate request using AI placeholder
    validation = validate_public_request(request.dict())
    
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail="Request validation failed")
    
    # Add request
    new_request = add_public_request(request)
    
    return new_request


@app.get("/roadblocks", response_model=List[Roadblock])
async def list_roadblocks():
    """Get list of all roadblocks and affected areas"""
    return get_roadblocks()


@app.post("/roadblocks", response_model=Roadblock)
async def create_roadblock(roadblock: Roadblock):
    """Report a new roadblock"""
    new_roadblock = add_roadblock(roadblock)
    return new_roadblock


@app.get("/vehicles", response_model=List[Vehicle])
async def list_vehicles():
    """Get current positions and status of all vehicles"""
    return get_vehicles()


@app.get("/districts_geo")
async def get_districts_geojson():
    """
    Get district boundaries as GeoJSON
    
    For rendering on maps
    """
    return get_district_geojson()


@app.post("/mission/plan")
async def plan_mission(
    source: str,
    destination: str,
    resources: dict,
    vehicle_type: str = "truck"
):
    """
    Generate mission plan for resource delivery
    
    Returns optimized route and logistics details
    """
    plan = generate_mission_plan(source, destination, resources, vehicle_type)
    return plan


@app.websocket("/ws/vehicles")
async def websocket_vehicles(websocket: WebSocket):
    """
    WebSocket endpoint for real-time vehicle tracking
    
    Broadcasts vehicle positions every 1-2 seconds
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Update vehicle positions
            vehicles = get_vehicles()
            simulate_vehicle_movements(vehicles)
            
            # Broadcast to all connected clients
            await manager.broadcast({
                "type": "vehicle_update",
                "timestamp": datetime.now().isoformat(),
                "vehicles": [v.dict() for v in vehicles]
            })
            
            # Wait 1-2 seconds
            await asyncio.sleep(1.5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background task to update vehicle positions
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    print("🚀 Disaster Management Platform API started")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/vehicles")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
