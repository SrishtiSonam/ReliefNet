from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RoutingRequest(BaseModel):
    """Request model for optimal route calculation"""
    from_district: str = Field(..., description="Starting district name")
    to_district: str = Field(..., description="Destination district name")
    vehicle_type: str = Field(..., description="Type of vehicle (truck, ambulance, drone)")
    constraints: Optional[Dict] = Field(default_factory=dict, description="Additional routing constraints")

    class Config:
        json_schema_extra = {
            "example": {
                "from_district": "Mumbai",
                "to_district": "Pune",
                "vehicle_type": "truck",
                "constraints": {
                    "avoid_tolls": False,
                    "max_distance_km": 500
                }
            }
        }

class RoutingResponse(BaseModel):
    """Response model for optimal route"""
    route: List[str] = Field(..., description="List of districts/waypoints in the route")
    travel_time_min: float = Field(..., description="Estimated travel time in minutes")
    cost: float = Field(..., description="Estimated cost in INR")
    distance_km: Optional[float] = Field(None, description="Total distance in kilometers")
    model_version: str = Field(default="placeholder-v1.0", description="Routing algorithm version")

    class Config:
        json_schema_extra = {
            "example": {
                "route": ["Mumbai", "Lonavala", "Pune"],
                "travel_time_min": 180.5,
                "cost": 1250.0,
                "distance_km": 150.0,
                "model_version": "placeholder-v1.0"
            }
        }
