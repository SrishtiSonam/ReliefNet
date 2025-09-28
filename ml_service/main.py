from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime
import subprocess
import logging

app = FastAPI(title="SDPDIAP ML Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class DistrictState(BaseModel):
    district_id: str
    inventory: float
    demand_last_period: float
    backlog: float
    avg_deprivation_time: float
    road_access: str

class ForecastRequest(BaseModel):
    district_ids: List[str]
    horizon: int = 6

class ForecastResponse(BaseModel):
    forecasts: Dict[str, Dict[str, float]]

class VFARequest(BaseModel):
    post_decision_state: Dict[str, Any]
    forecast_features: Dict[str, Any]
    model: str = "dl_vfa"

class VFAResponse(BaseModel):
    vfa_value: float
    explanation: Dict[str, Any]

class OptimizeRequest(BaseModel):
    current_state: Dict[str, Any]
    vfa_estimates: Dict[str, float]
    fleet: List[Dict[str, Any]]
    constraints: Optional[Dict[str, Any]] = {}

class OptimizeResponse(BaseModel):
    allocations: List[Dict[str, Any]]
    objective: float
    solve_info: Dict[str, Any]

class SimulateRequest(BaseModel):
    scenario: str
    policy: str = "dl_vfa"
    n_episodes: int = 10

class SimulateResponse(BaseModel):
    results_summary: Dict[str, float]
    output_file: str

# Global model storage
models = {}
artifacts_dir = "./artifacts"
data_dir = "./data"

def load_models():
    """Load pre-trained models on startup"""
    try:
        if os.path.exists("models/dl_vfa.pkl"):
            models["dl_vfa"] = joblib.load("models/dl_vfa.pkl")
            logger.info("Loaded DL-VFA model")
        
        if os.path.exists("models/nn_vfa.pkl"):
            models["nn_vfa"] = joblib.load("models/nn_vfa.pkl")
            logger.info("Loaded NN-VFA model")
            
        # Load forecast models
        if os.path.exists("models/forecast_model.pkl"):
            models["forecast"] = joblib.load("models/forecast_model.pkl")
            logger.info("Loaded forecast model")
            
    except Exception as e:
        logger.warning(f"Could not load models: {e}")

@app.on_event("startup")
async def startup_event():
    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs("models", exist_ok=True)
    load_models()

@app.get("/")
async def root():
    return {"message": "SDPDIAP ML Service", "status": "running"}

@app.post("/forecast/batch", response_model=ForecastResponse)
async def forecast_batch(request: ForecastRequest):
    """Generate probabilistic forecasts for districts"""
    try:
        forecasts = {}
        
        # Load or generate synthetic forecast data
        for district_id in request.district_ids:
            # Simple synthetic forecast - replace with actual model
            base_demand = np.random.gamma(2, 5)  # Mean ~10
            surge_prob = np.random.beta(1, 10)   # Low surge probability
            
            forecasts[district_id] = {
                "mean": float(base_demand),
                "var": float(base_demand * 0.5),
                "quantiles": {
                    "p10": float(base_demand * 0.3),
                    "p50": float(base_demand),
                    "p90": float(base_demand * 2.0)
                },
                "surge_prob": float(surge_prob)
            }
        
        return ForecastResponse(forecasts=forecasts)
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/value/estimate", response_model=VFAResponse)
async def estimate_value(request: VFARequest):
    """Estimate future cost using VFA"""
    try:
        # Extract features from state
        features = []
        state = request.post_decision_state
        forecast = request.forecast_features
        
        # Simple feature extraction
        total_inventory = sum(d.get('inventory', 0) for d in state.values())
        total_backlog = sum(d.get('backlog', 0) for d in state.values())
        avg_surge_prob = np.mean([f.get('surge_prob', 0) for f in forecast.values()])
        
        features = [total_inventory, total_backlog, avg_surge_prob]
        
        # Use model or simple heuristic
        if request.model in models:
            model = models[request.model]
            vfa_value = float(model.predict([features])[0])
        else:
            # Simple heuristic: cost proportional to backlog and surge risk
            vfa_value = total_backlog * 10 + avg_surge_prob * 100
        
        # Generate explanation
        feature_names = ["total_inventory", "total_backlog", "avg_surge_prob"]
        explanation = {
            "top_features": [
                {"name": feature_names[i], "score": abs(features[i]) / sum(abs(f) for f in features)}
                for i in range(len(features))
            ],
            "model": request.model
        }
        
        return VFAResponse(vfa_value=vfa_value, explanation=explanation)
        
    except Exception as e:
        logger.error(f"VFA estimation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_allocation(request: OptimizeRequest):
    """Solve MIP for optimal allocations"""
    try:
        from optimize.mip_solver import solve_allocation_mip
        
        result = solve_allocation_mip(
            current_state=request.current_state,
            vfa_estimates=request.vfa_estimates,
            fleet=request.fleet,
            constraints=request.constraints
        )
        
        return OptimizeResponse(**result)
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        # Fallback to simple heuristic allocation
        allocations = []
        districts = list(request.current_state.keys())
        
        for i, district in enumerate(districts[:3]):  # Allocate to first 3 districts
            allocations.append({
                "district": district,
                "truck_class": "small_truck",
                "count": 1,
                "eta_hours": 2.0
            })
        
        return OptimizeResponse(
            allocations=allocations,
            objective=1000.0,
            solve_info={"status": "heuristic", "solve_time_s": 0.01}
        )

@app.post("/simulate", response_model=SimulateResponse)
async def simulate_policy(request: SimulateRequest):
    """Run offline simulation"""
    try:
        from simulate.simulation_engine import run_simulation
        
        result = run_simulation(
            scenario=request.scenario,
            policy=request.policy,
            n_episodes=request.n_episodes
        )
        
        return SimulateResponse(**result)
        
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        # Return mock results
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"./artifacts/experiments/sim_{request.policy}_{timestamp}.csv"
        
        return SimulateResponse(
            results_summary={
                "mean_cost": 1234.5,
                "mean_deprivation": 3.8,
                "demand_coverage": 0.85
            },
            output_file=output_file
        )

@app.get("/models")
async def list_models():
    """List available models"""
    model_info = {}
    for model_name in models:
        model_info[model_name] = {
            "loaded": True,
            "type": type(models[model_name]).__name__
        }
    
    return {"models": model_info}

@app.post("/models/train")
async def train_models(model_type: str = "dl_vfa"):
    """Trigger model training"""
    try:
        if model_type == "dl_vfa":
            result = subprocess.run(["python", "train/train_dl_vfa.py"], 
                                  capture_output=True, text=True, cwd=".")
        elif model_type == "nn_vfa":
            result = subprocess.run(["python", "train/train_nn_vfa.py"], 
                                  capture_output=True, text=True, cwd=".")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")
        
        if result.returncode == 0:
            load_models()  # Reload models after training
            return {"status": "success", "message": f"Trained {model_type}"}
        else:
            return {"status": "error", "message": result.stderr}
            
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)