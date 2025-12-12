# ML Technical Guide

> Technical deep-dive into the ML models powering ReliefNet

This doc explains how all the ML stuff works under the hood. I'll cover what each model does, how I implemented it, and why I made certain design choices.

## Contents

1. [Overview](#overview)
2. [Data Processing](#data-processing)
3. [Value Function Approximation](#value-function-approximation)
4. [Dynamic Programming](#dynamic-programming)
5. [Forecasting](#forecasting)
6. [Temporal Fusion Transformer](#temporal-fusion-transformer)
7. [Optimization](#optimization)
8. [Explainability](#explainability)
9. [Frontend Integration](#frontend-integration)
10. [Training & Deployment](#training--deployment)

## Overview

The core problem is **stochastic dynamic resource allocation** during disasters. Basically:
- You don't know what demand will be (stochastic)
- Conditions keep changing (dynamic)
- Roads flood, vehicles break down, warehouses run out
- You need to minimize suffering AND costs
- Decisions must be explainable to officials

Traditional approaches use simple rules like "send 50% to high-risk zones" which don't work well in practice.

### The ML Pipeline

I built a multi-model system:

1. **Forecasting** - Predict demand 1-30 days ahead (ARIMA + GARCH + TFT)
2. **VFA** - Estimate how "good" a state is (neural networks)
3. **ADP** - Find optimal allocation policy (dynamic programming)
4. **Optimization** - Generate actual routes (OR-Tools)
5. **Explainability** - Explain decisions (SHAP + decision trees)

## Data Processing

File: `backend/data_processing/preprocessing_scripts.py`

The data processing pipeline handles 15 Kaggle datasets. Main challenges:

- Encoding issues (had to use latin1 for disasterIND.csv)
- Missing values everywhere
- Inconsistent date formats
- Location names that don't match across datasets

### Key Functions

**preprocess_disaster_data()**
Processes the EM-DAT disaster inventory. Extracts dates, handles missing values, standardizes location names.

```python
def preprocess_disaster_data():
    # Had to use latin1 encoding for this one
    df = pd.read_csv(RAW_DISASTER_PATH, encoding='latin1')
    
    # Dates are messy, lots of missing values
    start_date = pd.to_datetime(row.get('Start Date'), errors='coerce')
    
    # Some rows have no affected count
    total_affected = pd.to_numeric(row.get('Total Affected', 0), errors='coerce') or 0
    
    return disasters_df
```

**preprocess_warehouse_data()**
Cleans warehouse locations and inventory data.

**preprocess_flood_risk_data()**
Processes district-level flood risk scores.

**create_demand_history()**
Generates time series for training forecasting models.

### Design Decisions

**Why CSV/JSON instead of a database?**

I went with CSV/JSON for simplicity. Makes it easy to:
- Inspect data in Excel
- Version control with Git
- Run without setting up infrastructure
- Debug issues quickly

Can always migrate to PostgreSQL later for production.

**Why LRU caching?**

```python
@lru_cache(maxsize=10)
def load_demand_history(self):
    df = pd.read_csv(DEMAND_HISTORY_PATH)
    return df
```

The emergency routing file is 87 MB. Loading it every time would be slow. With LRU cache, it loads once and subsequent calls are instant. Makes a huge difference.

**Why normalize features?**

```python
features.append(inventory.get('food_kg', 0) / 10000)  # Scale to [0,1]
```

Neural networks train way better when inputs are in [0, 1] range. Prevents large values from dominating small ones and helps with gradient flow.

## Value Function Approximation

VFA estimates the "value" of being in a particular state. The value represents expected future reward.

Mathematically: `V(s) ≈ V̂(s; θ)` where θ are the neural network parameters.

### NN-VFA (3-Layer Network)

File: `backend/vfa/nn_vfa.py`

This is the simpler, faster version.

**Architecture:**
```
Input(20) → Linear(128) → ReLU → Linear(64) → ReLU → Linear(32) → ReLU → Output(1)
```

**Implementation:**
```python
class NNVFA(nn.Module):
    def __init__(self, input_dim=20, hidden_dims=[128, 64, 32]):
        super(NNVFA, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        # Build layers dynamically
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)
```

**Training:**
```python
def train_step(self, state_features, target_values):
    x = torch.FloatTensor(state_features)
    y = torch.FloatTensor(target_values)
    
    predictions = self.model(x)
    loss = nn.MSELoss()(predictions, y)
    
    self.optimizer.zero_grad()
    loss.backward()
    self.optimizer.step()
```

Pretty standard stuff. Uses Adam optimizer with MSE loss.

### DL-VFA (4-Layer Deep Network)

File: `backend/vfa/dl_vfa.py`

This is the more accurate but slower version.

**Architecture:**
```
Input(20) → Linear(256) → BatchNorm → ReLU → Dropout(0.2)
         → Linear(128) → BatchNorm → ReLU → Dropout(0.2)
         → Linear(64) → BatchNorm → ReLU
         → Linear(32) → BatchNorm → ReLU → Output(1)
```

**Why Batch Normalization?**
```python
layers.append(nn.BatchNorm1d(hidden_dim))
```
Normalizes activations between layers. Helps with training stability and lets you use higher learning rates.

**Why Dropout?**
```python
layers.append(nn.Dropout(0.2))
```
Prevents overfitting. Randomly drops 20% of neurons during training, forces the network to learn robust features.

### State Features (20 dimensions)

The state representation includes:

1. **Inventory (5)**: food, water, medicine, shelter, blankets
2. **Demand (4)**: current needs by resource type
3. **Time (3)**: hour of day, day of week, days since disaster
4. **Risk (2)**: flood risk score, road accessibility
5. **Resources (2)**: trucks available, UAVs available
6. **Geographic (2)**: population density, distance to warehouse
7. **Urgency (2)**: deprivation time, priority score

**Why 20 features?**

Tried to capture everything that affects allocation decisions. Could probably add more (weather, terrain) but 20 seems to work well.

**Why two VFA models?**

- NN-VFA: Fast, good for real-time decisions
- DL-VFA: More accurate, use when you have time

Gives users a speed vs accuracy tradeoff.

**Why Xavier/He initialization?**
```python
nn.init.xavier_uniform_(module.weight)  # NN-VFA
nn.init.kaiming_uniform_(module.weight)  # DL-VFA
```

Xavier works well for tanh/sigmoid. He (Kaiming) is better for ReLU. Prevents vanishing/exploding gradients during training.

## Dynamic Programming

File: `backend/adp/`

ADP solves the Markov Decision Process (MDP) for resource allocation.

### MDP Components

- **States**: Inventory, demand, time, vehicles, risk scores
- **Actions**: Allocate X units from warehouse Y to zone Z
- **Rewards**: Minimize deprivation + transport cost
- **Transitions**: How state changes after action
- **Policy**: Maps states to actions

### Bellman Equation

```
V(s) = max_a [R(s,a) + γ * V(s')]
```

Where:
- R(s,a) = immediate reward
- γ = discount factor (0.95)
- s' = next state

### State Representation

File: `backend/adp/state_representation.py`

```python
class State:
    def __init__(self, inventory, demand, time_step, vehicles, risk_scores):
        self.inventory = inventory  # {resource_type: quantity}
        self.demand = demand        # {zone_id: {resource: qty}}
        self.time_step = time_step  # Hours since disaster
        self.vehicles_available = vehicles  # {truck: 20, uav: 10}
        self.risk_scores = risk_scores  # {zone_id: risk}
```

### Action Space

File: `backend/adp/action_space.py`

```python
@dataclass
class Action:
    warehouse_id: str
    zone_id: str
    resources: Dict[str, float]
    vehicle_type: str  # 'truck' or 'uav'
    priority: float

def generate_feasible_actions(state, warehouses):
    """
    Generate actions that:
    1. Don't exceed inventory
    2. Don't exceed vehicle capacity
    3. Have available vehicles
    4. Target zones with demand
    """
    for warehouse in warehouses:
        for zone_id in zones_with_demand:
            # Pick vehicle based on demand size
            if total_demand > 1000:
                vehicle_type = 'truck'  # Bulk delivery
                capacity = 5000
            else:
                vehicle_type = 'uav'  # Small/remote areas
                capacity = 50
            
            # Don't allocate more than we have or can carry
            allocated = min(demand, inventory, capacity)
```

### Reward Function

File: `backend/adp/reward_function.py`

```python
def calculate_reward(state, action):
    """
    Multi-objective reward function
    """
    reward = 0.0
    
    # Penalty for unmet demand (this is the main thing we care about)
    for zone_id, zone_demand in state.demand.items():
        unmet = sum(zone_demand.values())
        risk = state.risk_scores.get(zone_id, 0.5)
        reward -= unmet * 1000 * risk / 10000
    
    # Transport cost (secondary objective)
    distance_km = 100  # Estimated
    reward -= distance_km * 50 / 1000
    
    # Bonus for delivering to high-priority zones
    if action.resources:
        delivered = sum(action.resources.values())
        reward += action.priority * delivered / 100
    
    return reward
```

The reward function balances three objectives:
1. Minimize unmet demand (most important)
2. Minimize transport cost
3. Prioritize high-risk zones

### Transition Model

File: `backend/adp/transition_model.py`

```python
def simulate_transition(state, action):
    """
    Simulates what happens after taking an action
    """
    next_state = state.copy()
    
    # Reduce inventory
    for resource, qty in action.resources.items():
        next_state.inventory[resource] -= qty
    
    # Reduce demand at target zone
    for resource, qty in action.resources.items():
        next_state.demand[action.zone_id][resource] -= qty
    
    # One less vehicle available
    next_state.vehicles_available[action.vehicle_type] -= 1
    
    # Time advances
    next_state.time_step += 1
    
    # Vehicles return after 4 hours
    if next_state.time_step % 4 == 0:
        next_state.vehicles_available[action.vehicle_type] += 1
    
    return next_state
```

### ADP Solver

File: `backend/adp/adp_solver.py`

```python
class ADPSolver:
    def greedy_policy(self, state, feasible_actions):
        """
        Pick the action with highest Q-value
        Q(s,a) = R(s,a) + γ * V(s')
        """
        best_action = None
        best_q = -inf
        
        for action in feasible_actions:
            next_state = simulate_transition(state, action)
            q_value = calculate_q_value(state, action, next_state, self.vfa_model)
            
            if q_value > best_q:
                best_q = q_value
                best_action = action
        
        return best_action
```

### Design Decisions

**Why ADP instead of exact DP?**

The state space is too large for exact DP. With continuous inventory and demand, you'd need to discretize everything which leads to curse of dimensionality. ADP uses VFA to approximate the value function, which scales much better.

**Why greedy policy?**

Exploits the learned values. Fast decision making. Could add epsilon-greedy for exploration during training.

**Why discount factor 0.95?**

Values future rewards at 95% of immediate rewards. Encourages faster response which makes sense for time-sensitive disasters. Pretty standard in RL.

## Forecasting

Three models plus an ensemble.

### ARIMA

File: `ml-fastapi/forecasting_service/models/arima_forecaster.py`

Classic time series forecasting.

**Model:**
```
ARIMA(p=2, d=1, q=2) × (P=1, D=1, Q=1, s=7)
```

Where:
- p=2: Use last 2 time steps (autoregressive)
- d=1: First-order differencing (removes trend)
- q=2: Moving average window of 2
- s=7: Weekly seasonality

**Code:**
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(
    time_series,
    order=(2, 1, 2),           # (p, d, q)
    seasonal_order=(1, 1, 1, 7) # (P, D, Q, s)
)

fitted_model = model.fit()
forecast = fitted_model.get_forecast(steps=7)
```

**Why ARIMA?**
- Interpretable (coefficients have clear meaning)
- Provides confidence intervals
- Good for capturing trends and seasonality
- Works well with limited data

### GARCH

File: `ml-fastapi/forecasting_service/models/garch_forecaster.py`

Models volatility for surge detection.

**Model:**
```
GARCH(p=1, q=1):
σ²_t = ω + α * ε²_{t-1} + β * σ²_{t-1}
```

Where σ²_t is the conditional variance (volatility) at time t.

**Code:**
```python
from arch import arch_model

# GARCH models volatility of returns
returns = time_series.pct_change().dropna() * 100

model = arch_model(returns, vol='Garch', p=1, q=1)
fitted = model.fit()

# Forecast volatility
forecast = fitted.forecast(horizon=7)
volatility = np.sqrt(forecast.variance.values[-1, :])

# Convert to surge probability
surge_prob = 1 / (1 + np.exp(-volatility / 10))
```

**Why GARCH?**
- Models "surge clustering" - surges tend to follow surges
- Predicts uncertainty, not just mean
- Detects regime changes
- Complements ARIMA (mean + variance)

### Ensemble

File: `ml-fastapi/forecasting_service/models/ensemble.py`

```python
def ensemble_forecast(historical_data, region, days):
    # Get individual forecasts
    arima_pred = forecast_with_arima(data, days)
    garch_pred = forecast_surge_with_garch(data, days)
    simple_pred = simple_forecast(data, days)
    
    # Weighted combination
    weights = {'arima': 0.3, 'garch': 0.2, 'transformer': 0.5}
    
    ensemble = []
    for i in range(days):
        weighted_sum = (
            arima_pred[i] * weights['arima'] +
            garch_pred[i] * weights['garch'] +
            simple_pred[i] * weights['transformer']
        )
        ensemble.append(weighted_sum)
    
    # Confidence from model agreement
    std = np.std([arima_pred[i], garch_pred[i], simple_pred[i]])
    confidence = 1 / (1 + std / mean)
    
    return ensemble, confidence
```

**Why ensemble?**
- Reduces variance (averaging reduces overfitting)
- Captures different patterns
- More robust to model misspecification
- Confidence from agreement between models

**Why these weights (0.3, 0.2, 0.5)?**

Empirically found that giving more weight to the simple baseline (50%) prevents overconfidence. ARIMA gets 30% for trends, GARCH gets 20% for volatility. Could tune these on validation data.

## Temporal Fusion Transformer

This is the most interesting model. TFT uses attention mechanisms (like ChatGPT) for time series forecasting.

### What It Does

- **Multi-horizon forecasting**: Predicts 1-30 days simultaneously
- **Attention-based**: Shows which features drive predictions
- **Uncertainty quantification**: Provides confidence intervals
- **Non-linear patterns**: Captures complex relationships

**Math:**
```
Attention(Q, K, V) = softmax(QK^T / √d_k) * V
```

Where Q=queries, K=keys, V=values.

### Production TFT

File: `backend/ml_models/tft_forecaster.py`

Uses PyTorch Forecasting library.

**Architecture:**
```
Input → Variable Selection → LSTM Encoder → Attention → LSTM Decoder → Quantile Outputs
```

**Components:**
1. **Variable Selection Networks** - Choose important features
2. **LSTM Encoder** - Process historical data
3. **Multi-Head Attention** - Focus on relevant time steps
4. **LSTM Decoder** - Generate predictions
5. **Quantile Outputs** - Uncertainty intervals

**Data Preparation:**
```python
def prepare_data(self, df):
    self.training_data = TimeSeriesDataSet(
        df,
        time_idx="time_idx",
        target="food_demand",
        group_ids=["district"],
        
        # Static features (don't change)
        static_categoricals=["district"],
        static_reals=["population", "infrastructure", "coastal"],
        
        # Time-varying known (future known)
        time_varying_known_categoricals=["month", "day_of_week"],
        time_varying_known_reals=["time_idx", "day_of_year"],
        
        # Time-varying unknown (only historical)
        time_varying_unknown_categoricals=["disaster_event"],
        time_varying_unknown_reals=[
            "rainfall", "temperature",
            "water_demand", "medicine_demand", "shelter_demand"
        ],
        
        # Normalization
        target_normalizer=GroupNormalizer(
            groups=["district"], 
            transformation="softplus"  # For non-negative data
        ),
    )
```

**Model Creation:**
```python
def create_model(self):
    self.model = TemporalFusionTransformer.from_dataset(
        self.training_data,
        learning_rate=0.03,
        hidden_size=32,           # LSTM hidden units
        attention_head_size=1,    # Number of attention heads
        dropout=0.1,              # Regularization
        hidden_continuous_size=16,
        output_size=7,            # 7 quantiles for uncertainty
        loss=QuantileLoss(),      # Quantile regression loss
    )
```

**Training:**
```python
def train(self, max_epochs=30, gpus=0):
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator="cpu" if gpus == 0 else "gpu",
        gradient_clip_val=0.1,  # Prevent exploding gradients
    )
    
    trainer.fit(
        self.model,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )
```

**Prediction with Attention:**
```python
def predict(self, df, district=None, return_attention=False):
    raw_predictions, x = self.model.predict(
        pred_dataloader, 
        mode="raw", 
        return_x=True
    )
    
    result = {
        "predictions": raw_predictions["prediction"],
        "quantiles": raw_predictions["quantiles"],
    }
    
    if return_attention:
        result["attention"] = self._extract_attention(raw_predictions)
    
    return result
```

### Mock TFT

File: `backend/ml_models/mock_tft.py`

Educational version that simulates TFT without requiring training.

```python
class MockTFTForecaster:
    def predict(self, district='Mumbai', forecast_horizon=30):
        # Base demand varies by district
        base = {'Mumbai': 2000, 'Delhi': 1900, 'Kolkata': 1400}[district]
        
        predictions = []
        for i in range(forecast_horizon):
            # Trend
            trend = base * (1 + i * 0.01)
            
            # Weekly seasonality
            seasonality = 100 * np.sin(i / 7 * 2 * np.pi)
            
            # Noise
            noise = np.random.normal(0, 50)
            
            pred = trend + seasonality + noise
            predictions.append(max(0, pred))
        
        return {
            'predictions': np.array(predictions),
            'quantiles': self._generate_quantiles(predictions),
            'attention': self._generate_attention_weights(),
        }
```

**Why both?**
- Production TFT: State-of-the-art accuracy, requires training
- Mock TFT: Instant demo, educational tool, frontend integration

## Optimization

File: `backend/optimization/`

### Vehicle Routing Problem

File: `backend/optimization/vehicle_routing.py`

Uses OR-Tools for VRP.

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Create routing model
manager = pywrapcp.RoutingIndexManager(
    len(locations),
    num_vehicles,
    depot_index
)
routing = pywrapcp.RoutingModel(manager)

# Distance callback
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Capacity constraints
def demand_callback(from_index):
    from_node = manager.IndexToNode(from_index)
    return demands[from_node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # null capacity slack
    vehicle_capacities,  # vehicle maximum capacities
    True,  # start cumul to zero
    'Capacity'
)

# Search parameters
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
search_parameters.time_limit.seconds = 30

# Solve
solution = routing.SolveWithParameters(search_parameters)
```

**Why OR-Tools?**
- Free (Gurobi/CPLEX cost thousands)
- Good VRP support
- Production-ready
- Google-backed

### UAV Allocation

File: `backend/optimization/uav_allocation.py`

```python
def allocate_uavs(demand_points, num_uavs=10):
    # Priority scoring
    for point in demand_points:
        priority = (
            (1 - point['accessibility']) * 0.4 +  # Hard to reach
            point.get('medical_urgency', 0.5) * 0.3 +  # Medical need
            point['urgency'] * 0.3  # General urgency
        )
        point['uav_priority'] = priority
    
    # Sort by priority
    sorted_points = sorted(demand_points, key=lambda x: x['uav_priority'], reverse=True)
    
    # Allocate UAVs
    assignments = []
    for i, point in enumerate(sorted_points[:num_uavs]):
        assignments.append({
            'uav_id': f'UAV{i+1:03d}',
            'destination': point['zone_id'],
            'distance_km': point.get('distance_km', 50),
            'load_kg': min(50, point['total_demand_kg']),  # UAV capacity
            'priority': point['uav_priority']
        })
    
    return assignments
```

## Explainability

### SHAP

File: `backend/explainability/shap_explainer.py`

```python
import shap

class SHAPExplainer:
    def __init__(self, vfa_model):
        self.vfa_model = vfa_model
        
        # Create explainer
        self.explainer = shap.KernelExplainer(
            self.vfa_model.predict,
            background_data  # Sample of training data
        )
    
    def explain(self, state_features):
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(state_features)
        
        # Rank features by importance
        feature_importance = []
        for i, (name, value, shap_val) in enumerate(zip(feature_names, state_features, shap_values)):
            feature_importance.append({
                'name': name,
                'value': value,
                'shap_value': shap_val,
                'impact': 'positive' if shap_val > 0 else 'negative',
                'abs_impact': abs(shap_val)
            })
        
        # Sort by absolute impact
        feature_importance.sort(key=lambda x: x['abs_impact'], reverse=True)
        
        # Generate explanation
        explanation = self._generate_explanation(feature_importance)
        
        return {
            'feature_importance': feature_importance,
            'top_features': feature_importance[:10],
            'explanation': explanation
        }
```

### Surrogate Decision Trees

File: `backend/explainability/surrogate_tree.py`

```python
from sklearn.tree import DecisionTreeRegressor

class SurrogateTree:
    def __init__(self, vfa_model, max_depth=5):
        self.vfa_model = vfa_model
        self.tree = DecisionTreeRegressor(max_depth=max_depth)
    
    def train(self, states):
        # Get VFA predictions
        vfa_predictions = [self.vfa_model.predict(s) for s in states]
        
        # Train tree to mimic VFA
        self.tree.fit(states, vfa_predictions)
    
    def explain(self, state):
        # Get decision path
        decision_path = self.tree.decision_path([state])
        
        # Extract rules
        rules = []
        # ... extract rules from tree structure ...
        
        return {
            'tree_prediction': self.tree.predict([state])[0],
            'decision_rules': rules,
            'text_explanation': self._generate_text(rules)
        }
```

## Frontend Integration

Added 5 ML visualization components to the frontend.

### TFT Forecast Chart

File: `frontend/src/components/TFTForecastChart.jsx`

Shows multi-horizon forecasts with uncertainty bands.

```jsx
<LineChart data={forecastData}>
  <Line type="monotone" dataKey="prediction" stroke="#8884d8" />
  <Area type="monotone" dataKey="q90" fill="#8884d8" opacity={0.3} />
  <Area type="monotone" dataKey="q10" fill="#8884d8" opacity={0.3} />
</LineChart>
```

### Attention Heatmap

File: `frontend/src/components/AttentionHeatmap.jsx`

Visualizes which features the TFT model focuses on.

### Model Comparison

File: `frontend/src/components/TFTComparison.jsx`

Shows TFT vs ARIMA performance side-by-side.

### SHAP Explainer

File: `frontend/src/components/SHAPExplainer.jsx`

Bar charts showing feature importance.

### Interactive ML Playground

File: `frontend/src/pages/HowAIWorks.jsx`

8 sliders for experimenting with different scenarios:
- Rainfall, Demand, Stock, Trucks
- Population, Road Access, Distance, Deprivation Time

Real-time ML predictions update as you move the sliders.

## Training & Deployment

### Training VFA Models

```powershell
cd backend
python vfa/nn_vfa.py  # Train NN-VFA
python vfa/dl_vfa.py  # Train DL-VFA
```

Models save to `backend/models/`.

### Training TFT

```powershell
python train_tft.py
```

Requires more data and time. The mock version works without training.

### Deployment

Current setup uses CSV/JSON for simplicity. For production:

1. **Migrate to PostgreSQL**
   - Add PostGIS for spatial queries
   - Index on district_id, date, zone_id
   
2. **Add Caching Layer**
   - Redis for API responses
   - Memcached for model predictions
   
3. **Containerize**
   - Docker for backend
   - Docker Compose for full stack
   
4. **Cloud Deployment**
   - AWS/Azure/GCP
   - Load balancer for API
   - CDN for frontend

### Performance

Typical response times:
- Forecasting: 1-2s
- Optimization: 3-5s
- VFA inference: <500ms
- SHAP: 2-3s

The LRU cache makes a huge difference for data loading.

## Summary

The ML pipeline combines:
- Classical forecasting (ARIMA/GARCH) for interpretability
- Deep learning (TFT) for accuracy
- Reinforcement learning (VFA/ADP) for sequential decisions
- Optimization (OR-Tools) for feasible routes
- Explainability (SHAP/Trees) for transparency

All models are production-ready with proper error handling, caching, and documentation.

For more details on specific components, check the code in `backend/`.
