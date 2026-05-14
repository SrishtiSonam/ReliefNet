# reliefnet/backend/app/models/road_network.py
from pydantic import BaseModel

class RoadEdge(BaseModel):
    source: str                  # district name
    target: str                  # district name
    distance_km: float           # Euclidean distance
    flood_risk: float            # edge flood exposure score
    landslide_risk: float        # elevation-difference risk
    failure_probability: float   # combined edge failure probability [0-1]
