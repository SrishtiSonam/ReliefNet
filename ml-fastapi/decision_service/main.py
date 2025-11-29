from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import DecisionRequest, DecisionResponse

app = FastAPI(
    title="Dispatch Decision Service",
    description="ML microservice for intelligent dispatch recommendations",
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
# with open('dispatch_model_placeholder.pkl', 'rb') as f:
#     decision_model = pickle.load(f)

def rule_based_decision(request: DecisionRequest) -> DecisionResponse:
    """
    Rule-based decision logic as fallback/baseline.
    
    TODO: Replace this with actual ML model inference.
    Team Member 4 should:
    1. Train the dispatch decision model (classification/recommendation model)
    2. Save it as 'dispatch_model_placeholder.pkl'
    3. Load it at startup (see commented code above)
    4. Replace this function with: decision = model.predict(features)
    
    This rule-based system provides a working baseline and can be used
    as a fallback if the ML model fails.
    """
    
    severity_scores = {
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 4
    }
    
    weather_scores = {
        'clear': 0,
        'rain': 1,
        'storm': 2,
        'fog': 1
    }
    
    traffic_scores = {
        'low': 0,
        'medium': 1,
        'high': 2
    }
    
    severity_score = severity_scores.get(request.severity.lower(), 2)
    weather_score = weather_scores.get(request.weather.lower(), 0)
    traffic_score = traffic_scores.get(request.traffic.lower(), 0)
    
    # Decision logic
    decision_parts = []
    alternatives = []
    confidence = 0.7  # Base confidence
    
    # Critical severity - deploy everything available
    if severity_score >= 4:
        if request.ambulance_availability > 0:
            decision_parts.append(f"Deploy ALL {request.ambulance_availability} ambulances")
        if request.drone_availability > 0:
            decision_parts.append(f"Deploy {request.drone_availability} drone(s) for assessment")
        if request.truck_availability and request.truck_availability > 0:
            decision_parts.append(f"Deploy {request.truck_availability} truck(s) with supplies")
        
        explanation = "CRITICAL severity requires maximum resource deployment. "
        confidence = 0.95
        
    # High severity
    elif severity_score == 3:
        ambulances_needed = min(request.ambulance_availability, 3)
        drones_needed = min(request.drone_availability, 1)
        
        if ambulances_needed > 0:
            decision_parts.append(f"Deploy {ambulances_needed} ambulance(s)")
        if drones_needed > 0:
            decision_parts.append(f"Deploy {drones_needed} drone for aerial assessment")
        
        explanation = "High severity with "
        confidence = 0.85
        
        # Weather considerations
        if weather_score >= 2:
            explanation += "severe weather conditions - prioritize ground vehicles. "
            alternatives.append("Wait for weather to improve if not urgent")
        else:
            explanation += "favorable weather conditions. "
        
        # Distance considerations
        if request.distance > 100:
            alternatives.append("Consider helicopter deployment for faster response")
            explanation += f"Long distance ({request.distance}km) may require air support. "
        
    # Medium severity
    elif severity_score == 2:
        ambulances_needed = min(request.ambulance_availability, 2)
        
        if ambulances_needed > 0:
            decision_parts.append(f"Deploy {ambulances_needed} ambulance(s)")
        
        if request.drone_availability > 0 and weather_score == 0:
            decision_parts.append("Deploy 1 drone for initial assessment")
        
        explanation = "Medium severity - standard response protocol. "
        confidence = 0.75
        
        alternatives.append("Monitor situation before deploying additional resources")
        
    # Low severity
    else:
        if request.ambulance_availability > 0:
            decision_parts.append("Deploy 1 ambulance for assessment")
        
        explanation = "Low severity - minimal resource deployment. "
        confidence = 0.80
        
        alternatives.append("Local emergency services may be sufficient")
    
    # Hospital capacity check
    if request.hospital_capacity < 30:
        decision_parts.append("ALERT: Hospital capacity critical - coordinate with nearby facilities")
        explanation += "Hospital capacity is low - consider patient distribution. "
        confidence -= 0.1
    
    # Traffic considerations
    if traffic_score >= 2:
        explanation += "Heavy traffic may delay ground vehicles. "
        if request.drone_availability > 0 and 'drone' not in ' '.join(decision_parts).lower():
            alternatives.append("Use drones to bypass traffic")
        confidence -= 0.05
    
    # Construct final decision
    if not decision_parts:
        decision = "Insufficient resources available - request backup from neighboring districts"
        confidence = 0.5
    else:
        decision = " + ".join(decision_parts)
    
    return DecisionResponse(
        decision=decision,
        confidence=round(max(0.5, min(1.0, confidence)), 2),
        explanation=explanation.strip(),
        model_version="rule-based-v1.0",
        alternative_options=alternatives if alternatives else None
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "decision_service",
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": False,  # TODO: Set to True when real model is loaded
        "decision_mode": "rule-based",  # TODO: Change to "ml-model" when model is integrated
        "endpoints": {
            "decision": "POST /decision/recommend"
        }
    }

@app.post("/decision/recommend", response_model=DecisionResponse)
async def recommend_dispatch(request: DecisionRequest):
    """
    Generate dispatch recommendation based on disaster parameters.
    
    Args:
        request: DecisionRequest with severity, weather, resources, etc.
    
    Returns:
        DecisionResponse with recommended decision, confidence, and explanation
    """
    try:
        # TODO: Preprocess features for ML model
        # features = preprocess_decision_features(request)
        
        # TODO: Use real ML model for prediction
        # prediction = decision_model.predict(features)
        # decision = map_prediction_to_decision(prediction)
        
        # Using rule-based decision for now
        result = rule_based_decision(request)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Decision generation error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
