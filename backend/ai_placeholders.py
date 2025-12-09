import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import (
    AllocationRequest, AllocationResult, AllocationExplanation,
    ExplanationFeature, ForecastData
)


def forecast(district: str, days: int = 7) -> ForecastData:
    """
    Generate surge forecast for a district
    
    This is a placeholder function that simulates ML-based forecasting.
    In production, this would use historical data, weather patterns,
    and ML models to predict resource demand.
    """
    predictions = []
    base_demand = random.randint(1000, 5000)
    
    for day in range(days):
        # Simulate increasing demand with some randomness
        demand_multiplier = 1 + (day * 0.1) + random.uniform(-0.2, 0.3)
        predictions.append({
            "day": day + 1,
            "date": (datetime.now() + timedelta(days=day+1)).strftime("%Y-%m-%d"),
            "food_demand": int(base_demand * demand_multiplier),
            "water_demand": int(base_demand * 1.5 * demand_multiplier),
            "medicine_demand": int(base_demand * 0.3 * demand_multiplier),
            "shelter_demand": int(base_demand * 0.5 * demand_multiplier),
            "confidence": random.uniform(0.7, 0.95)
        })
    
    return ForecastData(
        district=district,
        forecast_days=days,
        predictions=predictions,
        confidence=random.uniform(0.75, 0.92)
    )


def optimize_allocation(request: AllocationRequest) -> AllocationResult:
    """
    Optimize resource allocation using placeholder optimization
    
    This is a placeholder for optimization algorithms like:
    - Linear Programming
    - Genetic Algorithms
    - Reinforcement Learning
    
    In production, this would consider:
    - Current stock levels
    - Transportation costs
    - Delivery times
    - Priority levels
    - Vehicle availability
    """
    allocations = []
    total_cost = 0.0
    
    # Simulate allocation from multiple warehouses
    num_warehouses = random.randint(2, 4)
    
    for i in range(num_warehouses):
        allocation = {
            "warehouse_id": f"WH{i+1:03d}",
            "warehouse_name": f"Warehouse {i+1}",
            "resources": {},
            "cost": 0.0,
            "delivery_time_hours": random.randint(2, 12)
        }
        
        for resource, quantity in request.resources.items():
            # Distribute resources across warehouses
            allocated_qty = int(quantity / num_warehouses) + random.randint(-10, 10)
            allocated_qty = max(0, allocated_qty)
            allocation["resources"][resource] = allocated_qty
            
            # Calculate cost (simplified)
            unit_cost = random.uniform(10, 100)
            allocation["cost"] += allocated_qty * unit_cost
        
        total_cost += allocation["cost"]
        allocations.append(allocation)
    
    # Simulate optimization time
    optimization_time = random.uniform(0.5, 2.5)
    
    return AllocationResult(
        allocations=allocations,
        total_cost=total_cost,
        optimization_time=optimization_time
    )


def explain_allocation(district_id: str, allocation: Dict[str, Any]) -> AllocationExplanation:
    """
    Generate explainable AI insights for allocation decisions
    
    This simulates SHAP (SHapley Additive exPlanations) values
    and provides human-readable explanations.
    
    In production, this would use:
    - SHAP library for feature importance
    - LIME for local interpretability
    - Custom explanation generators
    """
    features = [
        ExplanationFeature(
            name="Population Density",
            value=random.uniform(500, 5000),
            impact=random.uniform(-0.5, 0.5),
            description="Higher density areas receive priority allocation"
        ),
        ExplanationFeature(
            name="Historical Demand",
            value=random.uniform(1000, 8000),
            impact=random.uniform(-0.3, 0.6),
            description="Based on past 30 days consumption patterns"
        ),
        ExplanationFeature(
            name="Current Stock Level",
            value=random.uniform(0, 100),
            impact=random.uniform(-0.4, 0.2),
            description="Percentage of warehouse capacity available"
        ),
        ExplanationFeature(
            name="Risk Score",
            value=random.uniform(0, 10),
            impact=random.uniform(0.1, 0.8),
            description="Composite risk based on weather, terrain, and vulnerability"
        ),
        ExplanationFeature(
            name="Transportation Cost",
            value=random.uniform(1000, 10000),
            impact=random.uniform(-0.6, -0.1),
            description="Estimated delivery cost including fuel and vehicle"
        ),
        ExplanationFeature(
            name="Delivery Time",
            value=random.uniform(2, 24),
            impact=random.uniform(-0.5, -0.1),
            description="Expected hours to reach destination"
        ),
    ]
    
    # Sort by absolute impact
    features.sort(key=lambda x: abs(x.impact), reverse=True)
    
    # Generate natural language rationale
    top_feature = features[0]
    rationale = (
        f"The allocation to {district_id} was primarily influenced by {top_feature.name.lower()} "
        f"(impact: {top_feature.impact:.2f}). {top_feature.description}. "
        f"The model also considered {len(features)-1} other factors including "
        f"{features[1].name.lower()} and {features[2].name.lower()} to optimize "
        f"both efficiency and equity in resource distribution."
    )
    
    return AllocationExplanation(
        decision=f"Allocate resources to {district_id}",
        confidence=random.uniform(0.75, 0.95),
        features=features,
        rationale=rationale
    )


def simulate_vehicle_movements(vehicles: List[Any]) -> None:
    """
    Simulate vehicle GPS position updates
    
    This is a placeholder for real-time vehicle tracking.
    In production, this would:
    - Receive GPS data from vehicle trackers
    - Update positions in real-time database
    - Calculate ETAs based on route and traffic
    - Detect anomalies and delays
    """
    for vehicle in vehicles:
        if vehicle.status == "in_transit":
            # Simulate movement along a route
            # Random walk with slight bias toward destination
            vehicle.lat += random.uniform(-0.01, 0.01)
            vehicle.lng += random.uniform(-0.01, 0.01)
            
            # Occasionally update status
            if random.random() < 0.05:
                vehicle.status = random.choice(["in_transit", "loading", "unloading"])


def validate_public_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and score public relief requests
    
    This is a placeholder for ML-based validation.
    In production, this would:
    - Detect duplicate requests
    - Verify location accuracy
    - Score urgency using NLP on description
    - Flag suspicious patterns
    - Prioritize based on vulnerability indices
    """
    validation_result = {
        "is_valid": True,
        "confidence": random.uniform(0.8, 0.99),
        "duplicate_probability": random.uniform(0.0, 0.3),
        "urgency_score": random.uniform(0.5, 1.0),
        "location_verified": random.choice([True, True, True, False]),
        "flags": []
    }
    
    # Add some random flags
    if validation_result["duplicate_probability"] > 0.2:
        validation_result["flags"].append("Possible duplicate request")
    
    if not validation_result["location_verified"]:
        validation_result["flags"].append("Location coordinates need verification")
    
    if request.get("urgency", 3) >= 4 and validation_result["urgency_score"] < 0.6:
        validation_result["flags"].append("Urgency mismatch - manual review recommended")
    
    return validation_result


def predict_roadblock_impact(roadblock: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict impact of roadblocks on logistics
    
    Placeholder for ML-based impact analysis.
    In production, this would:
    - Analyze affected routes
    - Calculate delay estimates
    - Suggest alternative routes
    - Predict clearance time
    """
    return {
        "affected_routes": random.randint(2, 10),
        "estimated_delay_hours": random.uniform(1, 12),
        "alternative_routes_available": random.choice([True, True, False]),
        "clearance_probability_24h": random.uniform(0.3, 0.9),
        "impact_score": random.uniform(0, 10)
    }


def generate_mission_plan(
    source: str,
    destination: str,
    resources: Dict[str, int],
    vehicle_type: str
) -> Dict[str, Any]:
    """
    Generate optimal mission plan
    
    Placeholder for route optimization and mission planning.
    In production, this would:
    - Use routing APIs (OSRM, Google Maps)
    - Consider real-time traffic
    - Optimize multi-stop routes
    - Account for vehicle constraints
    """
    return {
        "mission_id": f"MSN{random.randint(1000, 9999)}",
        "route": {
            "distance_km": random.uniform(50, 500),
            "estimated_time_hours": random.uniform(2, 12),
            "waypoints": [
                {"lat": random.uniform(10, 30), "lng": random.uniform(70, 90), "name": source},
                {"lat": random.uniform(10, 30), "lng": random.uniform(70, 90), "name": "Checkpoint 1"},
                {"lat": random.uniform(10, 30), "lng": random.uniform(70, 90), "name": destination},
            ]
        },
        "fuel_required_liters": random.uniform(20, 200),
        "crew_required": random.randint(2, 4),
        "estimated_cost": random.uniform(5000, 50000),
        "risk_assessment": {
            "overall_risk": random.choice(["low", "medium", "high"]),
            "weather_risk": random.uniform(0, 1),
            "terrain_risk": random.uniform(0, 1),
            "security_risk": random.uniform(0, 1)
        }
    }
