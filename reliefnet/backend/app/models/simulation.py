# reliefnet/backend/app/models/simulation.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SimulationRequest(BaseModel):
    disaster_type: str
    severity: float  # 0.0 to 1.0
    impact_radius_km: float
    center_lat: float
    center_lon: float

class AffectedDistrict(BaseModel):
    district: str
    estimated_damage_score: float
    estimated_shortage_rice_tons: float
    estimated_shortage_wheat_tons: float
    estimated_shortage_medicine_kits: int
    estimated_shortage_tarpaulin_units: int
    accessibility_score: float

class SimulationResult(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request: SimulationRequest
    affected_districts: List[AffectedDistrict]
    status: str  # COMPLETED|FAILED|RUNNING
