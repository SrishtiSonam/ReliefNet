from pydantic import BaseModel, Field
from typing import Dict, Optional

class ForecastRequest(BaseModel):
    """Request model for disaster demand forecasting"""
    district: str = Field(..., description="District name (e.g., Mumbai, Delhi)")
    disaster_type: str = Field(..., description="Type of disaster (e.g., flood, earthquake, cyclone)")
    date_features: Dict = Field(default_factory=dict, description="Date-related features (month, day, season, etc.)")
    other_features: Optional[Dict] = Field(default_factory=dict, description="Additional features for prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "district": "Mumbai",
                "disaster_type": "flood",
                "date_features": {
                    "month": 7,
                    "day": 15,
                    "season": "monsoon"
                },
                "other_features": {
                    "population": 12442373,
                    "rainfall_mm": 250
                }
            }
        }

class DemandPrediction(BaseModel):
    """Predicted resource demand"""
    food: int = Field(..., description="Food packets required")
    water: int = Field(..., description="Water bottles required")
    medical: int = Field(..., description="Medical kits required")

class ForecastResponse(BaseModel):
    """Response model for disaster demand forecasting"""
    predicted_demand: DemandPrediction
    severity: str = Field(..., description="Disaster severity level (low, medium, high, critical)")
    model_version: str = Field(default="placeholder-v1.0", description="Model version used for prediction")
    confidence: Optional[float] = Field(None, description="Prediction confidence score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_demand": {
                    "food": 5000,
                    "water": 8000,
                    "medical": 300
                },
                "severity": "high",
                "model_version": "placeholder-v1.0",
                "confidence": 0.85
            }
        }
