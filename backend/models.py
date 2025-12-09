from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STATE_ADMIN = "state_admin"
    DISTRICT_ADMIN = "district_admin"
    PUBLIC = "public"


class RequestType(str, Enum):
    FOOD = "food"
    WATER = "water"
    SHELTER = "shelter"
    MEDICINE = "medicine"
    RESCUE = "rescue"


class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class VehicleType(str, Enum):
    TRUCK = "truck"
    UAV = "uav"
    AMBULANCE = "ambulance"


class PublicRequest(BaseModel):
    id: Optional[str] = None
    name: str
    phone: str
    location: str
    lat: float
    lng: float
    request_type: RequestType
    description: str
    urgency: int = Field(ge=1, le=5)
    status: RequestStatus = RequestStatus.PENDING
    created_at: Optional[datetime] = None


class Roadblock(BaseModel):
    id: Optional[str] = None
    location: str
    lat: float
    lng: float
    severity: str
    description: str
    reported_by: str
    created_at: Optional[datetime] = None


class Vehicle(BaseModel):
    id: str
    type: VehicleType
    name: str
    lat: float
    lng: float
    status: str
    capacity: int
    current_load: int
    destination: Optional[str] = None


class District(BaseModel):
    id: str
    name: str
    state: str
    lat: float
    lng: float
    population: int
    risk_level: str


class Warehouse(BaseModel):
    id: str
    name: str
    district: str
    lat: float
    lng: float
    stocks: Dict[str, int]


class AllocationRequest(BaseModel):
    district_id: str
    resources: Dict[str, int]
    priority: int


class AllocationResult(BaseModel):
    allocations: List[Dict[str, Any]]
    total_cost: float
    optimization_time: float


class ExplanationFeature(BaseModel):
    name: str
    value: float
    impact: float
    description: str


class AllocationExplanation(BaseModel):
    decision: str
    confidence: float
    features: List[ExplanationFeature]
    rationale: str


class ForecastData(BaseModel):
    district: str
    forecast_days: int
    predictions: List[Dict[str, Any]]
    confidence: float
