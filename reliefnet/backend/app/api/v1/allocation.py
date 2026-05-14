# reliefnet/backend/app/api/v1/allocation.py
from fastapi import APIRouter, Depends, HTTPException
from ...models.allocation import AllocationPlan, OverrideRecord
from ...models.simulation import SimulationResult
from ...dependencies import db_dep
from ...db.repositories.simulation_repo import SimulationRepository
from ...db.repositories.allocation_repo import AllocationRepository
from ...core.optimization.service import optimize_resource_allocation
from typing import List

router = APIRouter()

from typing import List
from pydantic import BaseModel
class OptimizationConfig(BaseModel):
    budget_limit: float = 50000.0
    priority_focus: str = "balanced"
    max_warehouses: int = 5
    excluded_warehouses: List[str] = []

@router.post("/optimize/{run_id}", response_model=AllocationPlan)
async def optimize_allocation(run_id: str, config: OptimizationConfig, db = Depends(db_dep)):
    # 1. Fetch the simulation run
    sim_repo = SimulationRepository(db)
    simulation = await sim_repo.get_by_run_id(run_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    
    if simulation.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Simulation is not completed")

    # 2. Run optimization
    try:
        plan = await optimize_resource_allocation(
            simulation, 
            config.budget_limit, 
            config.priority_focus, 
            config.max_warehouses, 
            config.excluded_warehouses, 
            db
        )
        
        # 3. Store the plan
        alloc_repo = AllocationRepository(db)
        await alloc_repo.create(plan)
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=List[AllocationPlan])
async def get_latest_allocations(limit: int = 5, db = Depends(db_dep)):
    alloc_repo = AllocationRepository(db)
    # Get latest allocations that have been officially dispatched
    cursor = db.get_collection("allocations").find({"status": "DISPATCHED"}).sort("created_at", -1).limit(limit)
    plans = await cursor.to_list(length=limit)
    return plans

@router.get("/{id}", response_model=AllocationPlan)
async def get_allocation(id: str, db = Depends(db_dep)):
    repo = AllocationRepository(db)
    plan = await repo.get_by_allocation_id(id)
    if not plan:
        raise HTTPException(status_code=404, detail="Allocation plan not found")
    return plan

@router.post("/override", response_model=AllocationPlan)
async def submit_human_override(override: OverrideRecord, db = Depends(db_dep)):
    """
    Submit a human override for an allocation and re-optimize the remaining plan.
    """
    alloc_repo = AllocationRepository(db)
    # 1. Fetch the original plan
    plan = await alloc_repo.get_by_allocation_id(override.allocation_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Allocation plan not found")
        
    # 2. Store the override logic (Assuming a save_override method exists or we use a separate repo)
    # await alloc_repo.save_override(override)
    
    # 3. Apply override constraints
    # Example: Lock certain allocations, adjust capacities, then re-run optimization
    # This calls the advanced LogisticsOptimizer or PPO agent under the hood.
    # plan = await reoptimize_with_constraints(plan, override, db)
    
    return plan

@router.post("/{id}/dispatch", response_model=AllocationPlan)
async def dispatch_allocation(id: str, modified_plan: AllocationPlan, db = Depends(db_dep)):
    """
    Approve and dispatch the allocation plan, taking into account any manual human edits.
    This executes the plan by updating warehouse inventories and saving the final state.
    """
    alloc_repo = AllocationRepository(db)
    plan = await alloc_repo.get_by_allocation_id(id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Allocation plan not found")
        
    if getattr(plan, "status", "DRAFT") == "DISPATCHED":
        raise HTTPException(status_code=400, detail="Plan is already dispatched")
        
    # Execute the plan based on the MODIFIED payload from the human override
    from ...db.repositories.warehouse_repo import WarehouseRepository
    warehouse_repo = WarehouseRepository(db)
    
    from ...models.infrastructure import WarehouseTransaction

    for item in modified_plan.items:
        # Fetch warehouse
        warehouse = await warehouse_repo.get_by_warehouse_id(item.source_warehouse_id)
        if warehouse:
            # Deduct allocated quantities
            updates = {}
            if item.item_type == "rice":
                updates["stock_rice_tons"] = max(0, float(warehouse.stock_rice_tons - item.quantity))
            elif item.item_type == "wheat":
                updates["stock_wheat_tons"] = max(0, float(warehouse.stock_wheat_tons - item.quantity))
            elif item.item_type == "medicine":
                updates["stock_medicine_kits"] = max(0, int(warehouse.stock_medicine_kits - item.quantity))
            elif item.item_type == "tarpaulin":
                updates["stock_tarpaulin_units"] = max(0, int(warehouse.stock_tarpaulin_units - item.quantity))
                
            if updates:
                # Log transaction
                txn = WarehouseTransaction(
                    resource=item.item_type,
                    amount=item.quantity,
                    type="SUBTRACT",
                    reason=f"AI Dispatch Plan #{modified_plan.allocation_id[:8]}"
                )
                await db.get_collection("warehouses").update_one(
                    {"warehouse_id": warehouse.warehouse_id},
                    {
                        "$set": updates,
                        "$push": {"transactions": txn.model_dump()}
                    }
                )
            
    # Mark plan as dispatched and save the modified items
    modified_plan.status = "DISPATCHED"
    await alloc_repo.update("allocation_id", modified_plan.allocation_id, {
        "status": "DISPATCHED",
        "items": [i.model_dump() for i in modified_plan.items]
    })
    
    return modified_plan
