# ─── models/district.py ───────────────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional

class District(BaseModel):
    dist_name:          str
    state_name:         str
    latitude:           float
    longitude:          float
    population:         int
    dfsi_score:         float          # From DFSI.csv
    pct_flooded_area:   float          # From District_FloodedArea.csv
    human_fatality:     int            # From District_FloodImpact.csv
    human_injured:      int
    mean_flood_duration:float
    road_density:       Optional[float] = None   # From catchment_characteristics
    elevation:          Optional[float] = None
    ruggedness:         Optional[float] = None
    demand_per_period:  Optional[float] = None   # Computed by demand_estimator
    uav_cost:           Optional[float] = None   # Computed by cost_calculator
    truck_cost:         Optional[float] = None

class DistrictInDB(District):
    id: Optional[str] = Field(None, alias="_id")
