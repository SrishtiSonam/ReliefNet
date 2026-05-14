# reliefnet/backend/app/models/disaster.py
from pydantic import BaseModel, Field
from typing import Optional
from .common import GeoLocation

class DisasterEvent(BaseModel):
    dis_no: str
    year: int
    start_month: int
    end_month: int
    disaster_type: str
    disaster_subtype: str
    country: str
    province: str
    district: str
    district_canonical: str
    district_lgd_code: str
    total_deaths: float
    total_affected: float
    total_damage_usd: float
    latitude: float
    longitude: float
    location: Optional[GeoLocation] = None
    disaster_start_date: str
    disaster_end_date: str
    disaster_duration_days: int
    season: str # Monsoon|Post-Monsoon|Winter|Pre-Monsoon
    decade: int
    recency_weight: float
