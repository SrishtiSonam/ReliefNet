# reliefnet/backend/app/models/infrastructure.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .common import GeoLocation

class WarehouseTransaction(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resource: str
    amount: float
    type: str  # ADD | SUBTRACT
    reason: str

class Warehouse(BaseModel):
    warehouse_id: str
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    location: Optional[GeoLocation] = None
    capacity_tons: float
    stock_rice_tons: float
    stock_wheat_tons: float
    stock_medicine_kits: int
    stock_tarpaulin_units: int
    transactions: List[WarehouseTransaction] = Field(default_factory=list)

class Shelter(BaseModel):
    shelter_id: str
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    location: Optional[GeoLocation] = None
    capacity_total: int
    current_occupancy: int = 0

class Hospital(BaseModel):
    hospital_id: str
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    location: Optional[GeoLocation] = None
    num_beds: int
    has_icu: bool
    has_emergency: bool

# Force Pydantic to rebuild schemas to resolve types
Warehouse.model_rebuild()
Shelter.model_rebuild()
Hospital.model_rebuild()
