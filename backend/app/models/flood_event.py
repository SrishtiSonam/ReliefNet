# ─── models/flood_event.py ────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import Optional

class FloodEvent(BaseModel):
    event_id:           str
    start_date:         str
    end_date:           str
    peak_flood_level:   Optional[float] = None
    peak_discharge:     Optional[float] = None
    flood_volume:       Optional[float] = None
    event_duration:     int
    time_to_peak:       int
    recession_time:     int
    flood_type:         str            # "Flood" or "Severe Flood"
    state:              Optional[str] = None
    district:           Optional[str] = None
    # Precipitation antecedents T1d–T10d
    t1d: Optional[float] = None
    t2d: Optional[float] = None
    t3d: Optional[float] = None
    t4d: Optional[float] = None
    t5d: Optional[float] = None
