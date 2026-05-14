# reliefnet/backend/app/models/forecast.py
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class ForecastRequest(BaseModel):
    district: str
    horizon_days: int

class ForecastResult(BaseModel):
    forecast_id: str
    district: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    forecasted_demand: Dict[str, float]  # { "rice": 100, ... }
    confidence_interval: List[float]
    model_type: str
