# reliefnet/backend/app/core/optimization/service.py
import uuid
import math
import sys
from datetime import datetime
from typing import List
from pathlib import Path

# Add project root to sys.path to import ml_services
sys.path.append(str(Path(__file__).resolve().parents[4]))

from ...models.allocation import AllocationPlan, AllocationItem
from ...models.simulation import SimulationResult, AffectedDistrict
from ...db.repositories.warehouse_repo import WarehouseRepository
from ...db.repositories.district_repo import DistrictRepository
from ...db.repositories.road_network_repo import RoadNetworkRepository
from ml_services.optimization.route_planner import ReliefRoutePlanner

async def optimize_resource_allocation(simulation: SimulationResult, budget_limit: float, priority_focus: str, max_warehouses: int, excluded_warehouses: List[str], db) -> AllocationPlan:
    """Optimizes resource allocation using AI-aware route planning."""
    warehouse_repo = WarehouseRepository(db)
    district_repo = DistrictRepository(db)
    road_repo = RoadNetworkRepository(db)
    
    # 1. Load Road Network for the AI Planner
    all_edges = await road_repo.get_many(limit=5000)
    edge_dicts = [e.model_dump() for e in all_edges]
    planner = ReliefRoutePlanner(edge_dicts)

    # 2. Fetch warehouses
    warehouses = await warehouse_repo.get_many(limit=500)
    
    # Discard explicitly excluded warehouses
    if excluded_warehouses:
        warehouses = [w for w in warehouses if w.warehouse_id not in excluded_warehouses]
    
    # Constrain the number of active warehouses based on user simulation parameter
    if max_warehouses >= 0:
        warehouses = warehouses[:max_warehouses]
    local_stock = {
        w.warehouse_id: {
            "rice": w.stock_rice_tons,
            "wheat": w.stock_wheat_tons,
            "medicine": w.stock_medicine_kits,
            "tarpaulin": w.stock_tarpaulin_units,
            "name": w.name
        } for w in warehouses
    }

    allocation_items: List[AllocationItem] = []
    total_cost_est = 0.0

    # Determine sorting order based on priority strategy
    resource_priority = ["rice", "wheat", "medicine", "tarpaulin"]
    if priority_focus == "medical":
        resource_priority = ["medicine", "tarpaulin", "rice", "wheat"]
    elif priority_focus == "food_security":
        resource_priority = ["wheat", "rice", "medicine", "tarpaulin"]

    for affected in simulation.affected_districts:
        shortages = {
            "rice": affected.estimated_shortage_rice_tons,
            "wheat": affected.estimated_shortage_wheat_tons,
            "medicine": affected.estimated_shortage_medicine_kits,
            "tarpaulin": affected.estimated_shortage_tarpaulin_units
        }

        for resource in resource_priority:
            amount_needed = shortages.get(resource, 0)
            if amount_needed <= 0: continue
            
            remaining_need = amount_needed
            
            # Use AI Planner to find safest/best sources
            potential_sources = []
            for w in warehouses:
                if local_stock[w.warehouse_id][resource] > 0:
                    route_info = planner.get_route(w.district, affected.district)
                    if route_info:
                        potential_sources.append((w.warehouse_id, route_info))
            
            # Sort by AI-calculated safe distance
            potential_sources.sort(key=lambda x: x[1]["total_distance_km"])

            for w_id, route in potential_sources:
                if remaining_need <= 0: break
                if total_cost_est >= budget_limit: break # Budget cap enforcement
                
                available = local_stock[w_id][resource]
                to_allocate = min(remaining_need, available)
                
                if to_allocate > 0:
                    # Cost calculation
                    delivery_cost = to_allocate * route["total_distance_km"] * 0.15
                    
                    # Prevent breaking the budget on the very last item
                    if total_cost_est + delivery_cost > budget_limit:
                        max_affordable_alloc = (budget_limit - total_cost_est) / (route["total_distance_km"] * 0.15)
                        to_allocate = min(to_allocate, max_affordable_alloc)
                        delivery_cost = to_allocate * route["total_distance_km"] * 0.15

                    if to_allocate < 1: continue

                    # Ensure discrete units for integer resources
                    if resource in ["medicine", "tarpaulin"]:
                        to_allocate = math.floor(to_allocate)
                        if to_allocate < 1: continue

                    # AI-DRIVEN MODE SELECTION
                    mode = "truck"
                    if route["status"] == "HIGH_RISK" or route["max_edge_risk"] > 0.6:
                        mode = "uav"
                    elif resource == "medicine":
                        mode = "uav"

                    allocation_items.append(AllocationItem(
                        item_type=resource,
                        quantity=to_allocate,
                        source_warehouse_id=w_id,
                        destination_district=affected.district,
                        delivery_mode=mode
                    ))
                    
                    local_stock[w_id][resource] -= to_allocate
                    remaining_need -= to_allocate
                    total_cost_est += delivery_cost

    return AllocationPlan(
        allocation_id=str(uuid.uuid4()),
        simulation_run_id=simulation.run_id,
        created_at=datetime.utcnow(),
        items=allocation_items,
        total_cost_estimated=round(total_cost_est, 2),
        optimized_by="ai_route_aware_greedy_v1"
    )
