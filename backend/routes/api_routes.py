from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from backend.ml.arima_model import ArimaForecaster
from backend.solver.mip_solver import DisasterReliefSolver
from backend.simulation.environment import SimulationEnvironment
from backend.explain.rag_explainer import RagExplainer

router = APIRouter()
sim_env = SimulationEnvironment()
rag = RagExplainer()

# Schemas
class ForecastRequest(BaseModel):
    history: List[float]

class AllocationRequest(BaseModel):
    demand: Dict[int, int]
    inventory: int

class ExplainRequest(BaseModel):
    query: str

# 1. Forecast
@router.post("/forecast")
def get_forecast(req: ForecastRequest):
    forecaster = ArimaForecaster()
    forecaster.train(req.history)
    prediction = forecaster.predict(3)
    return {"forecast": prediction}

# 2. Simulate Step
@router.post("/simulate_step")
def simulate_step():
    state = sim_env.step()
    if state is None:
        return {"status": "Simulation Ended"}
    return state

# 3. Allocate
@router.post("/allocate")
def allocate_resources(req: AllocationRequest):
    # Load static data for solver
    districts = sim_env.districts
    vehicles = [{'type': 'Truck', 'capacity_kg': 5000}, {'type': 'UAV', 'capacity_kg': 20}] # Simplified
    roads = sim_env.roads
    
    solver = DisasterReliefSolver(districts, vehicles, roads)
    allocation = solver.solve_allocation(req.demand, req.inventory)
    return {"allocation": allocation}

# 4. Explain
@router.post("/explain")
def explain_logic(req: ExplainRequest):
    answer = rag.query(req.query)
    return {"explanation": answer}

# 5. Reset Sim
@router.post("/reset_sim")
def reset_simulation():
    sim_env.reset()
    return {"status": "Reset"}
