# ML Model & Data Integration Guide

This guide explains exactly where and how team members should integrate their trained ML models and data into the SDPD system.

## Overview

The system currently runs with **placeholder logic** to ensure all endpoints are functional. Your task is to replace these placeholders with real ML models and data.

---

## Person 2: Forecasting Model Integration

### Your Responsibility

Train and integrate a disaster demand forecasting model that predicts resource requirements (food, water, medical supplies) based on disaster parameters.

### File Location

**Model File**: `ml-fastapi/forecasting_service/model_placeholder.pkl`

### Integration Steps

#### 1. Train Your Model

Train a model that takes these features:
- `district` (string)
- `disaster_type` (string: flood, earthquake, cyclone, drought, landslide, fire)
- `date_features` (dict: month, season, etc.)
- `other_features` (dict: population, rainfall_mm, etc.)

Expected output:
- `food` (int): Number of food packets needed
- `water` (int): Number of water bottles needed
- `medical` (int): Number of medical kits needed
- `severity` (string): low, medium, high, or critical

#### 2. Save Your Model

```python
import pickle

# After training your model
with open('model_placeholder.pkl', 'wb') as f:
    pickle.dump(trained_model, f)
```

#### 3. Update main.py

**File**: `ml-fastapi/forecasting_service/main.py`

**Find this section** (around line 20):
```python
# TODO: Load real ML model here
# Example:
# import pickle
# with open('model_placeholder.pkl', 'rb') as f:
#     model = pickle.load(f)
```

**Replace with**:
```python
# Load trained forecasting model
import pickle
with open('model_placeholder.pkl', 'rb') as f:
    forecasting_model = pickle.load(f)
print("✓ Forecasting model loaded successfully")
```

#### 4. Update Prediction Function

**Find the function** `placeholder_predict` (around line 24)

**Replace the entire function with**:
```python
def ml_predict(district: str, disaster_type: str, date_features: dict, other_features: dict) -> ForecastResponse:
    """
    ML model prediction function.
    """
    # Preprocess features
    features = preprocess_features(district, disaster_type, date_features, other_features)
    
    # Get prediction from model
    prediction = forecasting_model.predict(features)
    
    # Map prediction to response format
    predicted_demand = DemandPrediction(
        food=int(prediction['food']),
        water=int(prediction['water']),
        medical=int(prediction['medical'])
    )
    
    return ForecastResponse(
        predicted_demand=predicted_demand,
        severity=prediction['severity'],
        model_version="your-model-v1.0",
        confidence=prediction.get('confidence', 0.85)
    )
```

**Add your preprocessing function**:
```python
def preprocess_features(district, disaster_type, date_features, other_features):
    """
    Preprocess input features for model.
    Customize this based on your model's requirements.
    """
    # Example preprocessing
    features = {
        'district': district,
        'disaster_type': disaster_type,
        'month': date_features.get('month', 1),
        'season': date_features.get('season', 'unknown'),
        'population': other_features.get('population', 0),
        'rainfall_mm': other_features.get('rainfall_mm', 0)
    }
    
    # Convert to format your model expects (numpy array, DataFrame, etc.)
    # Return processed features
    return features
```

#### 5. Update the Endpoint

**Find** (around line 90):
```python
# Using placeholder prediction for now
result = placeholder_predict(...)
```

**Replace with**:
```python
# Using ML model prediction
result = ml_predict(
    district=request.district,
    disaster_type=request.disaster_type,
    date_features=request.date_features,
    other_features=request.other_features
)
```

#### 6. Update Health Check

**Find** (around line 75):
```python
"model_loaded": False,  # TODO: Set to True when real model is loaded
```

**Replace with**:
```python
"model_loaded": True,
```

### Testing Your Integration

```bash
# Test the endpoint
curl -X POST http://localhost:8001/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Mumbai",
    "disaster_type": "flood",
    "date_features": {"month": 7, "season": "monsoon"},
    "other_features": {"population": 12442373, "rainfall_mm": 250}
  }'
```

---

## Person 3: Routing Algorithm Integration

### Your Responsibility

Implement an advanced routing algorithm (A*, Dijkstra, or ML-based) to find optimal routes between districts.

### File Locations

**Distance Matrix**: `ml-fastapi/routing_service/distance_matrix_placeholder.csv`  
**Main File**: `ml-fastapi/routing_service/main.py`

### Integration Steps

#### 1. Update Distance Matrix

**Replace** `distance_matrix_placeholder.csv` with real road network data:

```csv
from_district,to_district,distance_km,avg_speed_kmh,road_quality,toll_cost
Mumbai,Pune,150,60,good,200
Mumbai,Delhi,1400,70,excellent,800
...
```

Add columns as needed for your algorithm:
- `road_quality`
- `toll_cost`
- `traffic_multiplier`
- `elevation_change`
- etc.

#### 2. Implement Routing Algorithm

**File**: `ml-fastapi/routing_service/main.py`

**Find** the function `placeholder_route_calculation` (around line 35)

**Replace with your algorithm**:
```python
def advanced_routing(from_district: str, to_district: str, vehicle_type: str, constraints: dict) -> RoutingResponse:
    """
    Advanced routing algorithm implementation.
    """
    # Load graph from distance matrix
    graph = build_graph_from_matrix(distance_matrix)
    
    # Apply vehicle-specific constraints
    graph = apply_vehicle_constraints(graph, vehicle_type)
    
    # Apply user constraints
    if constraints.get('avoid_tolls'):
        graph = remove_toll_roads(graph)
    
    # Run routing algorithm (A*, Dijkstra, etc.)
    path, distance, time, cost = find_optimal_path(
        graph, 
        from_district, 
        to_district,
        algorithm='astar'  # or 'dijkstra', 'ml_based'
    )
    
    return RoutingResponse(
        route=path,
        travel_time_min=time,
        cost=cost,
        distance_km=distance,
        model_version="advanced-routing-v1.0"
    )
```

**Add helper functions**:
```python
def build_graph_from_matrix(df):
    """Build graph data structure from distance matrix."""
    # Your implementation
    pass

def apply_vehicle_constraints(graph, vehicle_type):
    """Apply vehicle-specific constraints to graph."""
    # Example: drones can fly direct, trucks need roads
    pass

def find_optimal_path(graph, start, end, algorithm='astar'):
    """Run pathfinding algorithm."""
    # Your A*/Dijkstra/ML implementation
    pass
```

#### 3. Update the Endpoint

**Find** (around line 140):
```python
# Using placeholder calculation for now
result = placeholder_route_calculation(...)
```

**Replace with**:
```python
# Using advanced routing algorithm
result = advanced_routing(
    from_district=request.from_district,
    to_district=request.to_district,
    vehicle_type=request.vehicle_type,
    constraints=request.constraints
)
```

### Testing Your Integration

```bash
curl -X POST http://localhost:8002/routing/optimal-route \
  -H "Content-Type: application/json" \
  -d '{
    "from_district": "Mumbai",
    "to_district": "Pune",
    "vehicle_type": "ambulance",
    "constraints": {"avoid_tolls": false}
  }'
```

---

## Person 4: Dispatch Decision Model Integration

### Your Responsibility

Train and integrate a dispatch decision model (classification or recommendation system) that suggests optimal resource deployment.

### File Location

**Model File**: `ml-fastapi/decision_service/dispatch_model_placeholder.pkl`

### Integration Steps

#### 1. Train Your Model

Train a model that takes these features:
- `severity` (categorical: low, medium, high, critical)
- `weather` (categorical: clear, rain, storm, fog)
- `traffic` (categorical: low, medium, high)
- `distance` (float: km)
- `hospital_capacity` (int: 0-100%)
- `ambulance_availability` (int)
- `drone_availability` (int)
- `truck_availability` (int)
- `time_of_day` (categorical: morning, afternoon, evening, night)

Expected output:
- Decision string (e.g., "Deploy 3 ambulances + 1 drone")
- Confidence score (0-1)
- Explanation text

#### 2. Save Your Model

```python
import pickle

with open('dispatch_model_placeholder.pkl', 'wb') as f:
    pickle.dump(trained_decision_model, f)
```

#### 3. Update main.py

**File**: `ml-fastapi/decision_service/main.py`

**Find** (around line 20):
```python
# TODO: Load real ML model here
```

**Replace with**:
```python
# Load trained decision model
import pickle
with open('dispatch_model_placeholder.pkl', 'rb') as f:
    decision_model = pickle.load(f)
print("✓ Decision model loaded successfully")
```

#### 4. Create ML Prediction Function

**Add this function**:
```python
def ml_decision(request: DecisionRequest) -> DecisionResponse:
    """
    ML model-based decision function.
    """
    # Preprocess features
    features = preprocess_decision_features(request)
    
    # Get prediction from model
    prediction = decision_model.predict(features)
    
    # Map prediction to decision text
    decision_text = map_prediction_to_action(prediction)
    
    # Get confidence and explanation
    confidence = decision_model.predict_proba(features).max()
    explanation = generate_explanation(request, prediction)
    
    # Get alternative options
    alternatives = get_alternative_decisions(features, prediction)
    
    return DecisionResponse(
        decision=decision_text,
        confidence=float(confidence),
        explanation=explanation,
        model_version="ml-decision-v1.0",
        alternative_options=alternatives
    )

def preprocess_decision_features(request):
    """Preprocess request into model features."""
    # Convert categorical to numerical, normalize, etc.
    features = {
        'severity_encoded': encode_severity(request.severity),
        'weather_encoded': encode_weather(request.weather),
        'traffic_encoded': encode_traffic(request.traffic),
        'distance': request.distance,
        'hospital_capacity': request.hospital_capacity,
        'ambulance_availability': request.ambulance_availability,
        'drone_availability': request.drone_availability,
        'truck_availability': request.truck_availability or 0
    }
    return features

def map_prediction_to_action(prediction):
    """Convert model prediction to human-readable action."""
    # Your mapping logic
    pass

def generate_explanation(request, prediction):
    """Generate explanation for the decision."""
    # Your explanation logic
    pass
```

#### 5. Update the Endpoint

**Find** (around line 180):
```python
# Using rule-based decision for now
result = rule_based_decision(request)
```

**Replace with**:
```python
# Using ML model decision
try:
    result = ml_decision(request)
except Exception as e:
    # Fallback to rule-based if ML fails
    print(f"ML decision failed: {e}, using rule-based fallback")
    result = rule_based_decision(request)
```

**Note**: Keep the `rule_based_decision` function as a fallback!

#### 6. Update Health Check

**Find** (around line 150):
```python
"model_loaded": False,
"decision_mode": "rule-based",
```

**Replace with**:
```python
"model_loaded": True,
"decision_mode": "ml-model",
```

### Testing Your Integration

```bash
curl -X POST http://localhost:8003/decision/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "weather": "clear",
    "traffic": "low",
    "distance": 50,
    "hospital_capacity": 80,
    "ambulance_availability": 5,
    "drone_availability": 2
  }'
```

---

## Common Integration Tasks

### Adding New Dependencies

If your model requires additional Python packages:

**Edit** `requirements.txt` in your service directory:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
scikit-learn==1.3.2      # Add your dependencies
tensorflow==2.15.0       # Add your dependencies
xgboost==2.0.3          # Add your dependencies
```

**Rebuild the Docker container**:
```bash
docker-compose up --build forecasting_service
```

### Handling Large Models

If your model file is large (>100MB):

1. **Use Git LFS** for version control
2. **Mount as volume** in docker-compose.yml:
```yaml
forecasting_service:
  volumes:
    - ./models/large_model.pkl:/app/model_placeholder.pkl
```
3. **Download at runtime** from cloud storage (S3, GCS)

### Logging and Debugging

Add logging to track model performance:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your prediction function
logger.info(f"Prediction request: {request}")
logger.info(f"Model output: {prediction}")
logger.info(f"Confidence: {confidence}")
```

---

## Verification Checklist

After integration, verify:

- [ ] Model loads without errors on service startup
- [ ] Health check endpoint shows `model_loaded: true`
- [ ] Predictions return valid JSON responses
- [ ] Response format matches Pydantic models
- [ ] Error handling works (try invalid inputs)
- [ ] Performance is acceptable (< 5 seconds per request)
- [ ] Docker container builds and runs successfully
- [ ] Integration tests pass

---

## Getting Help

If you encounter issues:

1. Check service logs: `docker-compose logs <service-name>`
2. Test endpoint directly: `curl http://localhost:800X/`
3. Review FastAPI auto-docs: `http://localhost:800X/docs`
4. Verify model file exists and is readable
5. Check Python dependencies are installed

---

## Example: Complete Integration Flow

```bash
# 1. Train your model locally
python train_forecasting_model.py

# 2. Copy model to service directory
cp trained_model.pkl ml-fastapi/forecasting_service/model_placeholder.pkl

# 3. Update main.py with integration code
# (as described above)

# 4. Test locally
cd ml-fastapi/forecasting_service
pip install -r requirements.txt
python main.py

# 5. Test endpoint
curl -X POST http://localhost:8001/forecast/demand -H "Content-Type: application/json" -d '...'

# 6. Rebuild Docker container
docker-compose up --build forecasting_service

# 7. Test via Express backend
curl -X POST http://localhost:5000/api/forecast/demand -H "Content-Type: application/json" -d '...'

# 8. Test via frontend
# Open http://localhost:3000/prediction and submit form
```

---

## Summary of File Paths

| Team Member | Model/Data File | Main Code File |
|-------------|----------------|----------------|
| Person 2 (Forecasting) | `ml-fastapi/forecasting_service/model_placeholder.pkl` | `ml-fastapi/forecasting_service/main.py` |
| Person 3 (Routing) | `ml-fastapi/routing_service/distance_matrix_placeholder.csv` | `ml-fastapi/routing_service/main.py` |
| Person 4 (Decision) | `ml-fastapi/decision_service/dispatch_model_placeholder.pkl` | `ml-fastapi/decision_service/main.py` |

All TODO markers in the code indicate exact integration points!
