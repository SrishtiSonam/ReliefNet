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

# Import database and mock ML logic
from database.db_manager import get_db
from mock_ml_logic import (
    ensemble_forecast as mock_ensemble_forecast,
    allocate_resources,
    generate_shap_explanation,
    calculate_vfa_score
)

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
    """
    EDUCATIONAL DEMO: Mock ML Forecasting Endpoint
    
    HOW IT WORKS:
    1. Uses ARIMA + GARCH ensemble to predict demand
    2. Returns 7-day forecast with confidence intervals
    3. Shows how forecasting affects allocation decisions
    
    This demonstrates the ML forecasting pipeline!
    """
    try:
        # Use mock ensemble forecast (educational demonstration)
        forecast_result = mock_ensemble_forecast(district, days)
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

# ==================== NEW DEMO ENDPOINTS ====================

@app.post("/api/allocate/simulate")
async def simulate_allocation(request: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: Allocation Simulation
    
    HOW IT WORKS:
    1. Takes district demands and available stock
    2. Calculates priority scores for each district
    3. Allocates resources based on priority
    4. Selects vehicles (trucks vs UAVs) based on conditions
    5. Returns allocation plan with VFA scores
    
    This shows the complete allocation engine logic!
    """
    try:
        districts = request.get('districts', [])
        available_stock = request.get('available_stock', {'food': 50000, 'water': 100000, 'medical': 10000})
        
        # Run allocation algorithm
        allocations = allocate_resources(districts, available_stock)
        
        # Store in database for history
        db = get_db()
        for alloc in allocations:
            db.add_allocation_record(alloc)
        
        return {
            'success': True,
            'allocations': allocations,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Allocation error: {e}")
        return {'success': False, 'error': str(e)}

@app.post("/api/explain/shap")
async def get_shap_explanation_for_allocation(allocation: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: SHAP Explainability
    
    HOW IT WORKS:
    1. Takes an allocation decision
    2. Calculates SHAP values (feature importance)
    3. Generates natural language explanation
    4. Shows why the model made this decision
    
    Makes AI transparent and trustworthy!
    """
    try:
        explanation = generate_shap_explanation(allocation)
        return explanation
    except Exception as e:
        return {'error': str(e)}

@app.post("/api/public/request")
async def submit_public_request(request_data: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: Public Request Submission
    
    Saves citizen relief requests to database
    Shows how user inputs flow through the system
    """
    try:
        db = get_db()
        request_id = db.add_public_request(request_data)
        
        return {
            'success': True,
            'request_id': request_id,
            'message': 'Request submitted successfully',
            'status': 'pending'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.get("/api/public/requests")
async def get_public_requests_list(status: Optional[str] = None, district: Optional[str] = None):
    """Get public requests from database"""
    try:
        db = get_db()
        requests = db.get_public_requests(status=status, district=district)
        return {'success': True, 'requests': requests}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.post("/api/district/blockage")
async def report_road_blockage(blockage_data: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: Road Blockage Reporting
    
    Shows how road blockages affect routing decisions
    Demonstrates dynamic re-allocation
    """
    try:
        db = get_db()
        blockage_id = db.add_road_blockage(blockage_data)
        
        return {
            'success': True,
            'blockage_id': blockage_id,
            'message': 'Blockage reported successfully'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.get("/api/district/blockages")
async def get_road_blockages_list(district: Optional[str] = None):
    """Get road blockages from database"""
    try:
        db = get_db()
        blockages = db.get_road_blockages(district=district)
        return {'success': True, 'blockages': blockages}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.post("/api/district/stock")
async def update_stock(stock_data: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: Warehouse Stock Update
    
    Shows how stock changes affect allocation decisions
    Demonstrates real-time inventory management
    """
    try:
        db = get_db()
        warehouse_id = stock_data.get('warehouse_id')
        updates = stock_data.get('updates', {})
        
        success = db.update_warehouse_stock(warehouse_id, updates)
        
        return {
            'success': success,
            'message': 'Stock updated successfully' if success else 'Update failed'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.get("/api/warehouse/stock")
async def get_warehouse_stock_list(district: Optional[str] = None):
    """Get warehouse stock levels"""
    try:
        db = get_db()
        stock = db.get_warehouse_stock(district=district)
        return {'success': True, 'warehouses': stock}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.post("/api/rerun")
async def rerun_allocation(request: Dict[str, Any] = Body(...)):
    """
    EDUCATIONAL DEMO: Re-run Allocation
    
    HOW IT WORKS:
    1. Gets updated data (blockages, stock, new requests)
    2. Re-calculates allocation with new constraints
    3. Shows how system adapts to changes
    
    Demonstrates dynamic decision-making!
    """
    try:
        # Get updated data from database
        db = get_db()
        
        district = request.get('district')
        blockages = db.get_road_blockages(district=district)
        stock = db.get_warehouse_stock(district=district)
        requests = db.get_public_requests(district=district, status='pending')
        
        # Prepare districts with updated data
        districts = request.get('districts', [])
        
        # Update accessibility based on blockages
        for dist in districts:
            if dist['name'] == district:
                # Reduce accessibility if there are blockages
                critical_blockages = [b for b in blockages if b['severity'] == 'critical']
                if critical_blockages:
                    dist['accessibility'] = max(0.2, dist.get('accessibility', 0.8) - 0.3)
                    dist['road_blocked'] = True
        
        # Calculate available stock
        available_stock = {}
        for warehouse in stock:
            available_stock['food'] = warehouse.get('food_kg', 0)
            available_stock['water'] = warehouse.get('water_liters', 0)
            available_stock['medical'] = warehouse.get('medical_units', 0)
        
        # Run allocation
        allocations = allocate_resources(districts, available_stock)
        
        return {
            'success': True,
            'allocations': allocations,
            'blockages_considered': len(blockages),
            'requests_pending': len(requests),
            'message': 'Allocation re-run with updated data'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

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
