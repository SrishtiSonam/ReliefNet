from pydantic import BaseModel, Field
from typing import Optional

class DecisionRequest(BaseModel):
    """Request model for dispatch decision recommendation"""
    severity: str = Field(..., description="Disaster severity (low, medium, high, critical)")
    weather: str = Field(..., description="Current weather conditions (clear, rain, storm, fog)")
    traffic: str = Field(..., description="Traffic conditions (low, medium, high)")
    distance: float = Field(..., description="Distance to disaster site in km")
    hospital_capacity: int = Field(..., description="Hospital capacity percentage (0-100)")
    ambulance_availability: int = Field(..., description="Number of ambulances available")
    drone_availability: int = Field(..., description="Number of drones available")
    truck_availability: Optional[int] = Field(None, description="Number of trucks available")
    time_of_day: Optional[str] = Field(None, description="Time of day (morning, afternoon, evening, night)")

    class Config:
        json_schema_extra = {
            "example": {
                "severity": "high",
                "weather": "clear",
                "traffic": "low",
                "distance": 50.0,
                "hospital_capacity": 80,
                "ambulance_availability": 5,
                "drone_availability": 2,
                "truck_availability": 3,
                "time_of_day": "afternoon"
            }
        }

class DecisionResponse(BaseModel):
    """Response model for dispatch decision"""
    decision: str = Field(..., description="Recommended dispatch decision")
    confidence: float = Field(..., description="Confidence score (0-1)")
    explanation: str = Field(..., description="Human-readable explanation of the decision")
    model_version: str = Field(default="placeholder-v1.0", description="Decision model version")
    alternative_options: Optional[list] = Field(None, description="Alternative dispatch options")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Deploy 2 ambulances + 1 drone for aerial assessment",
                "confidence": 0.87,
                "explanation": "High severity with good weather conditions. Ambulances for ground transport, drone for rapid assessment.",
                "model_version": "placeholder-v1.0",
                "alternative_options": [
                    "Deploy 3 ambulances only",
                    "Deploy helicopter if available"
                ]
            }
        }
