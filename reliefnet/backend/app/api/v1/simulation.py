# reliefnet/backend/app/api/v1/simulation.py
from fastapi import APIRouter, Depends, HTTPException
from ...models.simulation import SimulationRequest, SimulationResult
from ...dependencies import db_dep
from ...db.repositories.simulation_repo import SimulationRepository
from ...core.simulation.engine import run_disaster_simulation

router = APIRouter()

@router.post("/run", response_model=SimulationResult)
async def run_simulation(request: SimulationRequest, db = Depends(db_dep)):
    try:
        result = await run_disaster_simulation(request, db)
        repo = SimulationRepository(db)
        await repo.create(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{run_id}", response_model=SimulationResult)
async def get_simulation(run_id: str, db = Depends(db_dep)):
    repo = SimulationRepository(db)
    result = await repo.get_by_run_id(run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return result
