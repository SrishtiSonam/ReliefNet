# reliefnet/backend/app/models/allocation.py
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class AllocationItem(BaseModel):
    item_type: str
    quantity: float
    source_warehouse_id: str
    destination_district: str
    delivery_mode: str  # truck|uav

class AllocationPlan(BaseModel):
    allocation_id: str
    simulation_run_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    items: List[AllocationItem]
    total_cost_estimated: float
    optimized_by: str  # genetic_algorithm|lp_solver
    status: str = "DRAFT"

class OverrideRecord(BaseModel):
    override_id: str
    allocation_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str
    previous_value: Dict
    new_value: Dict

# reliefnet/backend/app/models/user.py
from pydantic import BaseModel

class User(BaseModel):
    email: str
    full_name: str
    role: str  # ADMIN|COORDINATOR|VIEWER
    hashed_password: str
    is_active: bool = True
