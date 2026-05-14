# reliefnet/backend/app/models/common.py
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float]  # [longitude, latitude]

class TimestampModel(BaseModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
