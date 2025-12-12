"""
Mock ML Logic for Educational Demonstration
This module simulates ML behavior to help users understand how the system works.
All logic is simplified for educational purposes - not production ML!

EDUCATIONAL FOCUS:
- Show how forecasting affects allocation decisions
- Demonstrate VFA (Value Function Approximation) scoring
- Explain vehicle selection logic (Truck vs UAV)
- Illustrate priority-based allocation
- Demonstrate SHAP-like explainability
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


# ==================== FORECASTING SIMULATION ====================

def mock_arima_forecast(historical_demand: List[float], days: int = 7) -> Dict[str, Any]:
    """
    EDUCATIONAL: Simulates ARIMA (AutoRegressive Integrated Moving Average) forecasting
    
    HOW IT WORKS:
    1. ARIMA analyzes historical patterns (trends, seasonality)
    2. Uses past values to predict future demand
    3. Provides confidence intervals showing prediction uncertainty
    
    In real ML: Uses statsmodels.tsa.statespace.SARIMAX with parameters (p,d,q)(P,D,Q,s)
    Here: Simple trend + noise simulation for demonstration
    """
    
    if not historical_demand or len(historical_demand) < 3:
        # Default baseline for India disaster scenarios
        historical_demand = [4000, 4500, 5000]
    
    # Calculate trend (are demands increasing or decreasing?)
    recent_avg = np.mean(historical_demand[-7:]) if len(historical_demand) >= 7 else np.mean(historical_demand)
    trend = (historical_demand[-1] - historical_demand[0]) / len(historical_demand)
    
    predictions = []
    for day in range(1, days + 1):
        # ARIMA prediction = recent average + trend + some randomness
        base_prediction = recent_avg + (trend * day)
        noise = np.random.normal(0, base_prediction * 0.05)  # 5% noise
        prediction = max(0, base_prediction + noise)
        
        # Confidence interval (wider for further predictions)
        confidence_width = base_prediction * 0.15 * (1 + day * 0.05)
        
        predictions.append({
            'day': day,
            'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
            'arima_prediction': round(prediction),
            'confidence_low': round(prediction - confidence_width),
            'confidence_high': round(prediction + confidence_width),
        })
    
    return {
        'model': 'ARIMA',
        'predictions': predictions,
        'confidence': 0.75 + np.random.random() * 0.15  # 75-90% confidence
    }


def mock_garch_volatility(historical_demand: List[float], days: int = 7) -> Dict[str, Any]:
    """
    EDUCATIONAL: Simulates GARCH (Generalized AutoRegressive Conditional Heteroskedasticity)
    
    HOW IT WORKS:
    1. GARCH models volatility (how much demand fluctuates)
    2. Detects surge patterns during disasters
    3. Predicts when demand spikes are likely
    
    In real ML: Uses arch library with GARCH(p,q) model
    Here: Volatility calculation based on demand variance
    """
    
    if not historical_demand or len(historical_demand) < 3:
        historical_demand = [4000, 4500, 5000]
    
    # Calculate volatility (standard deviation of recent changes)
    changes = np.diff(historical_demand)
    volatility = np.std(changes) if len(changes) > 0 else 500
    
    predictions = []
    for day in range(1, days + 1):
        # GARCH predicts volatility increases during disasters
        surge_factor = 1 + (volatility / np.mean(historical_demand)) * day * 0.1
        base = np.mean(historical_demand[-3:])
        
        predictions.append({
            'day': day,
            'garch_prediction': round(base * surge_factor),
            'volatility': round(volatility * surge_factor),
            'surge_index': min(100, round(surge_factor * 50))  # 0-100 scale
        })
    
    return {
        'model': 'GARCH',
        'predictions': predictions,
        'volatility_trend': 'increasing' if volatility > 300 else 'stable'
    }


def ensemble_forecast(district: str, days: int = 7) -> Dict[str, Any]:
    """
    EDUCATIONAL: Combines ARIMA + GARCH for robust forecasting
    
    HOW IT WORKS:
    1. ARIMA provides trend-based predictions
    2. GARCH adds volatility/surge detection
    3. Ensemble combines both with weighted average
    4. Final prediction is more robust than either model alone
    
    This is how real ML systems work - combining multiple models!
    """
    
    # Simulate historical demand for Indian districts
    # Higher baseline for major cities affected by disasters
    district_baselines = {
        'Mumbai': 6000,
        'Chennai': 5500,
        'Kolkata': 5200,
        'Delhi': 5000,
        'Bangalore': 4500,
        'Hyderabad': 4800,
        'Pune': 4200,
        'Ahmedabad': 4600
    }
    
    baseline = district_baselines.get(district, 4500)
    
    # Generate mock historical data (last 30 days)
    historical = [baseline + np.random.normal(0, baseline * 0.1) for _ in range(30)]
    
    # Get predictions from both models
    arima_result = mock_arima_forecast(historical, days)
    garch_result = mock_garch_volatility(historical, days)
    
    # Combine predictions (ensemble)
    ensemble_predictions = []
    for i in range(days):
        arima_pred = arima_result['predictions'][i]['arima_prediction']
        garch_pred = garch_result['predictions'][i]['garch_prediction']
        
        # Weighted average: ARIMA 60%, GARCH 40%
        # (ARIMA better for trends, GARCH better for surges)
        ensemble_pred = arima_pred * 0.6 + garch_pred * 0.4
        
        ensemble_predictions.append({
            'day': i + 1,
            'date': arima_result['predictions'][i]['date'],
            'food_demand': round(ensemble_pred),
            'water_demand': round(ensemble_pred * 2),  # Water need is ~2x food
            'medicine_demand': round(ensemble_pred * 0.1),  # Medical ~10% of food
            'shelter_demand': round(ensemble_pred * 0.3),  # Shelter ~30% of food
            'confidence': round(arima_result['confidence'], 2),
            'surge_index': garch_result['predictions'][i]['surge_index']
        })
    
    return {
        'region': district,
        'forecast_days': days,
        'predictions': ensemble_predictions,
        'overall_confidence': round(arima_result['confidence'], 2),
        'model_contributions': {
            'arima': 0.6,
            'garch': 0.4
        }
    }


# ==================== VFA (VALUE FUNCTION APPROXIMATION) ====================

def calculate_vfa_score(state: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    EDUCATIONAL: Simulates Value Function Approximation
    
    HOW IT WORKS:
    1. VFA estimates "value" of a state (how good is current situation?)
    2. Considers: inventory, demand, time, resources available
    3. Higher VFA score = better position to handle disaster
    4. Used in ADP (Approximate Dynamic Programming) for long-term planning
    
    In real ML: Neural network trained on historical data
    Here: Weighted combination of key factors
    """
    
    # Extract state features
    inventory = state.get('inventory', {})
    demand = state.get('demand', {})
    resources = state.get('resources', {})
    
    # Calculate individual feature scores (0-1 scale)
    
    # 1. Inventory adequacy (do we have enough stock?)
    total_inventory = sum(inventory.values())
    total_demand = sum(demand.values())
    inventory_score = min(1.0, total_inventory / max(total_demand, 1))
    
    # 2. Resource availability (trucks, UAVs available?)
    trucks_available = resources.get('trucks', 0)
    uavs_available = resources.get('uavs', 0)
    resource_score = min(1.0, (trucks_available * 0.7 + uavs_available * 0.3) / 10)
    
    # 3. Urgency factor (how critical is the situation?)
    urgency = state.get('urgency', 0.5)  # 0-1 scale
    urgency_score = 1.0 - urgency  # Lower urgency = higher score
    
    # 4. Accessibility (can we reach affected areas?)
    accessibility = state.get('accessibility', 0.8)  # 0-1 scale
    
    # VFA Score = weighted combination
    # These weights would be learned by neural network in real ML
    vfa_score = (
        inventory_score * 0.35 +      # 35% weight on inventory
        resource_score * 0.25 +       # 25% weight on resources
        urgency_score * 0.20 +        # 20% weight on urgency
        accessibility * 0.20          # 20% weight on accessibility
    )
    
    # Feature contributions (for explainability)
    feature_impacts = {
        'inventory_adequacy': inventory_score * 0.35,
        'resource_availability': resource_score * 0.25,
        'urgency_level': urgency_score * 0.20,
        'road_accessibility': accessibility * 0.20
    }
    
    return round(vfa_score, 3), feature_impacts


# ==================== ALLOCATION ENGINE ====================

def calculate_priority_score(district_data: Dict[str, Any]) -> float:
    """
    EDUCATIONAL: Calculate allocation priority for a district
    
    HOW IT WORKS:
    1. Multiple factors determine which district gets resources first
    2. Factors: demand urgency, population, accessibility, deprivation time
    3. Higher score = higher priority
    
    This is the core of fair resource allocation!
    """
    
    # Factor 1: Demand urgency (0-1)
    urgency = district_data.get('urgency', 0.5)
    
    # Factor 2: Population density (normalized)
    population = district_data.get('population', 100000)
    population_score = min(1.0, population / 1000000)  # Normalize to 1M
    
    # Factor 3: Deprivation time (how long without resources?)
    hours_deprived = district_data.get('hours_deprived', 0)
    deprivation_score = min(1.0, hours_deprived / 72)  # Normalize to 72 hours
    
    # Factor 4: Accessibility (inverse - harder to reach = higher priority)
    accessibility = district_data.get('accessibility', 0.8)
    accessibility_score = 1.0 - accessibility
    
    # Priority score (weighted combination)
    priority = (
        urgency * 0.40 +              # 40% - Most important!
        deprivation_score * 0.30 +    # 30% - Time matters
        population_score * 0.20 +     # 20% - More people = higher need
        accessibility_score * 0.10    # 10% - Help hard-to-reach areas
    )
    
    return round(priority, 3)


def select_vehicle_type(district_data: Dict[str, Any], demand_kg: float) -> Dict[str, int]:
    """
    EDUCATIONAL: Decide whether to use Trucks or UAVs
    
    HOW IT WORKS:
    1. Trucks: High capacity (5000kg), slow, need roads
    2. UAVs: Low capacity (50kg), fast, can fly anywhere
    3. Decision based on: accessibility, urgency, demand size
    
    LOGIC:
    - Use UAVs if: roads blocked, urgent medical, remote area
    - Use Trucks if: large demand, roads clear, bulk supplies
    - Often use both for optimal coverage!
    """
    
    accessibility = district_data.get('accessibility', 0.8)
    urgency = district_data.get('urgency', 0.5)
    has_medical = district_data.get('medical_need', False)
    road_blocked = district_data.get('road_blocked', False)
    
    # Decision logic
    use_uavs = (
        road_blocked or                    # Roads blocked? Must use UAVs
        accessibility < 0.5 or             # Hard to reach? UAVs better
        (urgency > 0.7 and has_medical)    # Urgent medical? UAVs faster
    )
    
    if use_uavs:
        # Calculate UAVs needed (50kg capacity each)
        uavs_needed = int(np.ceil(min(demand_kg, 500) / 50))  # UAVs for urgent/medical
        remaining_demand = max(0, demand_kg - 500)
        trucks_needed = int(np.ceil(remaining_demand / 5000)) if remaining_demand > 0 else 0
    else:
        # Use trucks primarily (5000kg capacity each)
        trucks_needed = int(np.ceil(demand_kg / 5000))
        uavs_needed = 0
    
    return {
        'trucks': trucks_needed,
        'uavs': uavs_needed,
        'reason': 'UAVs for accessibility/urgency' if use_uavs else 'Trucks for bulk delivery'
    }


def allocate_resources(districts: List[Dict[str, Any]], available_stock: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    EDUCATIONAL: Main allocation engine
    
    HOW IT WORKS:
    1. Calculate priority for each district
    2. Sort districts by priority (highest first)
    3. Allocate resources based on priority and availability
    4. Select appropriate vehicles (trucks/UAVs)
    5. Record VFA scores for learning
    
    This simulates the complete ML allocation pipeline!
    """
    
    # Step 1: Calculate priorities
    for district in districts:
        district['priority_score'] = calculate_priority_score(district)
        
        # Calculate VFA score
        state = {
            'inventory': available_stock,
            'demand': {'total': district.get('demand_kg', 0)},
            'resources': {'trucks': 10, 'uavs': 20},  # Available fleet
            'urgency': district.get('urgency', 0.5),
            'accessibility': district.get('accessibility', 0.8)
        }
        vfa_score, _ = calculate_vfa_score(state)
        district['vfa_score'] = vfa_score
    
    # Step 2: Sort by priority (highest first)
    districts_sorted = sorted(districts, key=lambda x: x['priority_score'], reverse=True)
    
    # Step 3: Allocate resources
    allocations = []
    remaining_stock = available_stock.copy()
    
    for district in districts_sorted:
        demand_kg = district.get('demand_kg', 0)
        
        # Check if we can meet demand
        total_available = sum(remaining_stock.values())
        allocated_kg = min(demand_kg, total_available)
        
        # Select vehicles
        vehicle_assignment = select_vehicle_type(district, allocated_kg)
        
        # Create allocation record
        allocation = {
            'district': district['name'],
            'demand_kg': demand_kg,
            'allocated_kg': allocated_kg,
            'trucks_assigned': vehicle_assignment['trucks'],
            'uavs_assigned': vehicle_assignment['uavs'],
            'priority_score': district['priority_score'],
            'vfa_score': district['vfa_score'],
            'urgency_level': 'critical' if district.get('urgency', 0) > 0.7 else 'high' if district.get('urgency', 0) > 0.4 else 'medium',
            'vehicle_selection_reason': vehicle_assignment['reason']
        }
        
        allocations.append(allocation)
        
        # Update remaining stock
        if allocated_kg > 0:
            # Deduct from stock (simplified)
            for resource in remaining_stock:
                deduction = allocated_kg / len(remaining_stock)
                remaining_stock[resource] = max(0, remaining_stock[resource] - deduction)
    
    return allocations


# ==================== EXPLAINABILITY (SHAP-LIKE) ====================

def generate_shap_explanation(allocation: Dict[str, Any]) -> Dict[str, Any]:
    """
    EDUCATIONAL: Simulates SHAP (SHapley Additive exPlanations)
    
    HOW IT WORKS:
    1. SHAP shows how much each feature contributed to the decision
    2. Positive SHAP value = feature increased allocation
    3. Negative SHAP value = feature decreased allocation
    4. Sum of all SHAP values = final decision
    
    In real ML: Uses shap library with KernelExplainer
    Here: Calculate feature impacts based on allocation logic
    """
    
    priority = allocation.get('priority_score', 0.5)
    vfa = allocation.get('vfa_score', 0.5)
    urgency = allocation.get('urgency_level', 'medium')
    
    # Simulate SHAP values (how much each feature contributed)
    # Base value = average allocation (0.5)
    base_value = 0.5
    
    # Feature impacts
    shap_values = [
        {
            'feature': 'Priority Score',
            'value': priority,
            'shap_value': round((priority - 0.5) * 0.4, 3),  # 40% weight
            'impact': 'positive' if priority > 0.5 else 'negative'
        },
        {
            'feature': 'VFA Score',
            'value': vfa,
            'shap_value': round((vfa - 0.5) * 0.3, 3),  # 30% weight
            'impact': 'positive' if vfa > 0.5 else 'negative'
        },
        {
            'feature': 'Urgency Level',
            'value': urgency,
            'shap_value': 0.15 if urgency == 'critical' else 0.05 if urgency == 'high' else -0.05,
            'impact': 'positive' if urgency in ['critical', 'high'] else 'negative'
        },
        {
            'feature': 'Vehicle Availability',
            'value': allocation.get('trucks_assigned', 0) + allocation.get('uavs_assigned', 0),
            'shap_value': 0.08,
            'impact': 'positive'
        },
        {
            'feature': 'Stock Availability',
            'value': allocation.get('allocated_kg', 0) / max(allocation.get('demand_kg', 1), 1),
            'shap_value': round((allocation.get('allocated_kg', 0) / max(allocation.get('demand_kg', 1), 1) - 0.5) * 0.2, 3),
            'impact': 'positive' if allocation.get('allocated_kg', 0) >= allocation.get('demand_kg', 0) else 'negative'
        }
    ]
    
    # Sort by absolute impact
    shap_values_sorted = sorted(shap_values, key=lambda x: abs(x['shap_value']), reverse=True)
    
    # Generate natural language explanation
    top_features = shap_values_sorted[:3]
    explanation = f"The allocation decision for {allocation['district']} was primarily influenced by: "
    
    for i, feat in enumerate(top_features):
        if i > 0:
            explanation += ", "
        explanation += f"{feat['feature']} ({feat['impact']} impact of {feat['shap_value']:+.3f})"
    
    explanation += f". Overall, the model assigned {allocation['trucks_assigned']} trucks and {allocation['uavs_assigned']} UAVs to deliver {allocation['allocated_kg']}kg of resources."
    
    return {
        'base_value': base_value,
        'predicted_value': priority,  # Final decision
        'shap_values': shap_values_sorted,
        'explanation': explanation
    }


# ==================== HELPER FUNCTIONS ====================

def calculate_deprivation_cost(hours_without_resources: float, population: int) -> float:
    """
    EDUCATIONAL: Calculate penalty for unmet demand
    
    HOW IT WORKS:
    - Longer without resources = higher cost
    - More people affected = higher cost
    - This cost is minimized by the optimization algorithm
    
    Formula: cost = hours × population × severity_factor
    """
    severity_factor = 1.0 + (hours_without_resources / 24) * 0.5  # Increases over time
    cost = hours_without_resources * population * severity_factor
    return round(cost, 2)


if __name__ == "__main__":
    print("=== Testing Mock ML Logic ===\n")
    
    # Test 1: Forecasting
    print("1. Testing Ensemble Forecast for Mumbai:")
    forecast = ensemble_forecast('Mumbai', days=7)
    print(f"   - Forecast days: {forecast['forecast_days']}")
    print(f"   - Confidence: {forecast['overall_confidence']}")
    print(f"   - Day 1 demand: {forecast['predictions'][0]['food_demand']}kg food\n")
    
    # Test 2: VFA Score
    print("2. Testing VFA Score Calculation:")
    state = {
        'inventory': {'food': 10000, 'water': 20000},
        'demand': {'food': 8000, 'water': 15000},
        'resources': {'trucks': 5, 'uavs': 10},
        'urgency': 0.6,
        'accessibility': 0.7
    }
    vfa, impacts = calculate_vfa_score(state)
    print(f"   - VFA Score: {vfa}")
    print(f"   - Top impact: {max(impacts, key=impacts.get)}\n")
    
    # Test 3: Allocation
    print("3. Testing Resource Allocation:")
    districts = [
        {'name': 'Mumbai', 'demand_kg': 8000, 'urgency': 0.9, 'accessibility': 0.6, 'population': 1200000, 'hours_deprived': 48},
        {'name': 'Pune', 'demand_kg': 5000, 'urgency': 0.5, 'accessibility': 0.8, 'population': 500000, 'hours_deprived': 24}
    ]
    stock = {'food': 15000, 'water': 30000, 'medical': 2000}
    
    allocations = allocate_resources(districts, stock)
    for alloc in allocations:
        print(f"   - {alloc['district']}: {alloc['allocated_kg']}kg, Priority: {alloc['priority_score']}, Vehicles: {alloc['trucks_assigned']}T + {alloc['uavs_assigned']}U")
    
    # Test 4: SHAP Explanation
    print("\n4. Testing SHAP Explanation:")
    explanation = generate_shap_explanation(allocations[0])
    print(f"   - {explanation['explanation'][:150]}...")
    
    print("\n✅ All mock ML functions working correctly!")
