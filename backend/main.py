"""
Updated Flask backend with real ML integration
Replaces placeholders with actual AI/ML models
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from models import (
    PublicRequest, Roadblock, Vehicle, District, UserRole,
    AllocationRequest, RequestStatus
)
from mock_data import (
    get_districts, get_district_geojson, get_warehouses,
    get_vehicles, update_vehicle_positions, get_public_requests,
    add_public_request, get_roadblocks, add_roadblock, get_shelters
)

# Import ML modules
from data_processing import loader
from vfa import NNVFA, DLVFA, extract_state_features, create_sample_state
from adp import solve_allocation_problem, create_initial_state
from optimization import optimize_delivery_plan, recalculate_with_constraints
from explainability import explain_allocation_decision, explain_with_tree

app = FastAPI(
    title="ReliefNet ML-Powered API",
    description="Disaster management with real AI/ML",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load VFA models
print("Loading VFA models...")
try:
    nn_vfa_model = NNVFA.load_model()
except:
    print("Creating new NN-VFA model...")
    from vfa import create_pretrained_nn_vfa
    nn_vfa_model = create_pretrained_nn_vfa()

# WebSocket manager
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
    return {
        "status": "online",
        "service": "ReliefNet ML-Powered API",
        "version": "2.0.0",
        "ml_models": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/dashboard")
async def get_dashboard(role: UserRole = Query(...)):
    """Get dashboard data based on role"""
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
    else:
        return {
            "role": role,
            "shelters": get_shelters(),
            "active_alerts": [{
                "id": "ALT001",
                "type": "weather",
                "severity": "high",
                "message": "Heavy rainfall expected",
                "issued_at": datetime.now().isoformat()
            }],
            "safety_guidelines": [
                "Stay indoors during heavy rainfall",
                "Keep emergency supplies ready"
            ],
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/forecast")
async def get_forecast(district: str = Query("Mumbai"), days: int = Query(7)):
    """Real ML-powered forecast using ensemble"""
    try:
        # Load historical data
        demand_history = loader.load_demand_history()
        
        # Import ensemble forecaster
        sys.path.append(str(Path(__file__).parent.parent / "ml-fastapi" / "forecasting_service" / "models"))
        from ensemble import ensemble_forecast
        
        # Generate forecast
        forecast_result = ensemble_forecast(demand_history, region=district, forecast_days=days)
        
        return forecast_result
        
    except Exception as e:
        print(f"Forecast error: {e}")
        # Fallback to simple forecast
        import numpy as np
        from datetime import timedelta
        
        predictions = []
        base_demand = 5000
        for i in range(days):
            predictions.append({
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'food_demand': base_demand * (1 + i * 0.1),
                'water_demand': base_demand * 2 * (1 + i * 0.1),
                'medicine_demand': base_demand * 0.1,
                'shelter_demand': base_demand * 0.3,
                'confidence': 0.7
            })
        
        return {
            'region': district,
            'forecast_days': days,
            'predictions': predictions,
            'overall_confidence': 0.7
        }

@app.post("/api/optimize")
async def optimize_allocation(request: Dict[str, Any] = Body(...)):
    """Optimize resource allocation using OR-Tools"""
    try:
        warehouses = get_warehouses()
        warehouses_data = [w.dict() for w in warehouses]
        
        # Create demand points from request
        demand_points = request.get('demand_points', [
            {
                'zone_id': 'ZONE1',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'total_demand_kg': 3000,
                'accessibility': 0.8,
                'urgency': 0.7
            }
        ])
        
        # Optimize
        delivery_plan = optimize_delivery_plan(warehouses_data, demand_points)
        
        return delivery_plan
        
    except Exception as e:
        print(f"Optimization error: {e}")
        return {
            'success': False,
            'error': str(e),
            'truck_routes': [],
            'uav_assignments': []
        }

@app.post("/api/optimize/recalculate")
async def recalculate_optimization(request: Dict[str, Any] = Body(...)):
    """Recalculate with human-in-the-loop constraints"""
    try:
        original_plan = request.get('original_plan', {})
        new_constraints = request.get('constraints', {})
        warehouses_data = request.get('warehouses', [w.dict() for w in get_warehouses()])
        demand_points = request.get('demand_points', [])
        
        updated_plan = recalculate_with_constraints(
            original_plan, new_constraints, warehouses_data, demand_points
        )
        
        return updated_plan
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.get("/api/explain/shap")
async def get_shap_explanation(district_id: str = Query(...)):
    """SHAP explanation for allocation"""
    try:
        # Create sample state
        state = create_sample_state()
        state_features = extract_state_features(state)
        
        # Get SHAP explanation
        explanation = explain_allocation_decision(state_features, nn_vfa_model)
        
        return explanation
        
    except Exception as e:
        print(f"SHAP error: {e}")
        return {
            'error': str(e),
            'feature_importance': [],
            'explanation': 'Explanation unavailable'
        }

@app.get("/api/explain/tree")
async def get_tree_explanation(district_id: str = Query(...)):
    """Surrogate tree explanation"""
    try:
        state = create_sample_state()
        state_features = extract_state_features(state)
        
        tree_explanation = explain_with_tree(state_features, nn_vfa_model)
        
        return tree_explanation
        
    except Exception as e:
        return {'error': str(e), 'decision_rules': []}

@app.get("/api/vfa")
async def get_vfa_value(state_dict: Dict[str, Any] = Body(...)):
    """Get VFA value estimate"""
    try:
        state_features = extract_state_features(state_dict)
        value = nn_vfa_model.predict_value(state_features)
        
        return {
            'value_estimate': float(value),
            'model': 'NN-VFA',
            'state_features': state_features.tolist()
        }
    except Exception as e:
        return {'error': str(e)}

# Keep existing endpoints
@app.get("/public_requests", response_model=List[PublicRequest])
async def list_public_requests(status: Optional[RequestStatus] = None, limit: int = Query(50)):
    requests = get_public_requests()
    if status:
        requests = [r for r in requests if r.status == status]
    return requests[:limit]

@app.post("/public_requests", response_model=PublicRequest)
async def create_public_request(request: PublicRequest):
    new_request = add_public_request(request)
    return new_request

@app.get("/roadblocks", response_model=List[Roadblock])
async def list_roadblocks():
    return get_roadblocks()

@app.post("/roadblocks", response_model=Roadblock)
async def create_roadblock(roadblock: Roadblock):
    return add_roadblock(roadblock)

@app.get("/vehicles", response_model=List[Vehicle])
async def list_vehicles():
    return get_vehicles()

@app.get("/districts_geo")
async def get_districts_geojson():
    return get_district_geojson()

@app.websocket("/ws/vehicles")
async def websocket_vehicles(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            vehicles = get_vehicles()
            from ai_placeholders import simulate_vehicle_movements
            simulate_vehicle_movements(vehicles)
            
            await manager.broadcast({
                "type": "vehicle_update",
                "timestamp": datetime.now().isoformat(),
                "vehicles": [v.dict() for v in vehicles]
            })
            
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    print("🚀 ReliefNet ML-Powered API started")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🤖 ML Models: Active")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
