from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from models import ForecastRequest, ForecastResponse, DemandPrediction

app = FastAPI(
    title="Disaster Forecasting Service",
    description="ML microservice for predicting disaster resource demand",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Load real ML model here
# Example:
# import pickle
# with open('model_placeholder.pkl', 'rb') as f:
#     model = pickle.load(f)

def placeholder_predict(district: str, disaster_type: str, date_features: dict, other_features: dict) -> ForecastResponse:
    """
    Placeholder prediction function using deterministic logic.
    
    TODO: Replace this with actual ML model inference.
    Team Member 2 should:
    1. Train the forecasting model
    2. Save it as 'model_placeholder.pkl'
    3. Load it at startup (see commented code above)
    4. Replace this function with: predictions = model.predict(features)
    """
    
    # Create a deterministic hash from inputs for consistent placeholder results
    input_str = f"{district}_{disaster_type}"
    hash_val = int(hashlib.md5(input_str.encode()).hexdigest(), 16)
    
    # Disaster type severity mapping
    severity_map = {
        'flood': 'high',
        'earthquake': 'critical',
        'cyclone': 'high',
        'drought': 'medium',
        'landslide': 'medium',
        'fire': 'low'
    }
    
    severity = severity_map.get(disaster_type.lower(), 'medium')
    
    # Base demand multipliers based on severity
    severity_multipliers = {
        'low': 1.0,
        'medium': 2.0,
        'high': 3.5,
        'critical': 5.0
    }
    
    multiplier = severity_multipliers[severity]
    
    # Generate placeholder demand based on hash and severity
    base_food = (hash_val % 3000) + 1000
    base_water = (hash_val % 5000) + 2000
    base_medical = (hash_val % 500) + 100
    
    predicted_demand = DemandPrediction(
        food=int(base_food * multiplier),
        water=int(base_water * multiplier),
        medical=int(base_medical * multiplier)
    )
    
    return ForecastResponse(
        predicted_demand=predicted_demand,
        severity=severity,
        model_version="placeholder-v1.0",
        confidence=0.75 + (hash_val % 20) / 100  # Placeholder confidence
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "forecasting_service",
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": False,  # TODO: Set to True when real model is loaded
        "endpoints": {
            "forecast": "POST /forecast/demand"
        }
    }

@app.post("/forecast/demand", response_model=ForecastResponse)
async def forecast_demand(request: ForecastRequest):
    """
    Predict resource demand for a disaster scenario.
    
    Args:
        request: ForecastRequest containing district, disaster_type, and features
    
    Returns:
        ForecastResponse with predicted demand, severity, and model info
    """
    try:
        # TODO: Preprocess features and prepare for model input
        # features = preprocess_features(request)
        
        # TODO: Use real model for prediction
        # prediction = model.predict(features)
        
        # Using placeholder prediction for now
        result = placeholder_predict(
            district=request.district,
            disaster_type=request.disaster_type,
            date_features=request.date_features,
            other_features=request.other_features
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
