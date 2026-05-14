# 🧠 ReliefNet — AI/ML Architecture Documentation

This document provides a comprehensive overview of the AI and Machine Learning components within the ReliefNet platform. The system uses a multi-model approach combining Reinforcement Learning (MAPPO/PPO), Constrained Optimization, Explainable AI (XAI), and Gradient Boosting.

---

## 📂 Directory Structure

```text
reliefnet/ml_services/
├── environments/
│   └── disaster_env.py         # Custom OpenAI Gym environment
├── explainability/
│   ├── shap_explainer.py       # XGBoost model transparency
│   └── rl_explainer.py         # RL decision explainability
├── fairness/
│   └── fairness_metrics.py     # Equity and Gini constraints
├── forecasting/
│   └── xgboost_service.py      # Demand prediction logic
├── models/                     # Trained weights & parameters
├── optimization/
│   ├── route_planner.py        # Risk-aware pathfinding
│   └── logistics_optimizer.py  # PuLP MILP solver
├── rl_agents/
│   ├── ppo_agent.py            # Stable-Baselines3 PPO agent
│   └── mappo_agent.py          # CTDE Multi-agent framework
├── simulation/
│   └── disaster_simulator.py   # Stochastic disaster engine
└── training_pipeline.py        # Orchestrates model training
```

---

## 🛠️ Core AI Components and Function Details

### 1. Reinforcement Learning Environment (`environments/disaster_env.py`)
- **Class**: `DisasterReliefEnv`
- **Purpose**: A fully OpenAI Gymnasium-compatible environment that models stochastic disaster dynamics.
- **Functions Used**:
    - `__init__(...)`: Initializes state/action dimensions. Calculates observation bounds based on districts, warehouses, fleets, and flood severity.
    - `reset(...)`: Re-initializes the episode with stochastic starting states (random initial shortages, road connectivities, flood severities).
    - `step(action)`: Takes an allocation action array. Updates shortages, dynamically degrades roads based on flood severity, and returns the next state, calculated reward, termination flag, and metrics info.
    - `render()`: Standard Gym method for visualizing the environment step.
    - `close()`: Cleans up environment resources.

### 2. Multi-Agent & PPO RL Agents (`rl_agents/ppo_agent.py`, `rl_agents/mappo_agent.py`)
- **Classes**: `DisasterPPOAgent`, `ActorNetwork`, `CentralizedCriticNetwork`, `MAPPOAgentFramework`
- **Purpose**: Deep reinforcement learning models that optimize routing under continuous environments.
- **Functions Used (`ppo_agent.py`)**:
    - `__init__(env, model_path)`: Loads an existing Stable-Baselines3 PPO model or initializes a fresh `MlpPolicy` model.
    - `train(total_timesteps, save_dir)`: Runs PPO training loops with checkpoint callbacks.
    - `predict_allocation(state, deterministic)`: Infers an allocation distribution given the current state and returns structured allocation actions with a confidence estimate.
- **Functions Used (`mappo_agent.py`)**:
    - `ActorNetwork.forward(obs)`: Decentralized execution model predicting bounded actions for a specific agent using Sigmoid.
    - `CentralizedCriticNetwork.forward(global_state)`: Centralized training value estimation.
    - `MAPPOAgentFramework.get_actions(observations)`: Infers actions for all agents concurrently (CTDE).
    - `MAPPOAgentFramework.update(rollouts)`: Processes rollouts to update both the centralized critic and the decentralized actors.

### 3. Disaster Simulation Engine (`simulation/disaster_simulator.py`)
- **Class**: `DisasterSimulator`
- **Purpose**: Stochastic simulation engine modeling flood propagation, damage, and cascading failures.
- **Functions Used**:
    - `__init__(districts, base_graph, severity_multiplier)`: Initializes graph properties, demand, and damage vectors.
    - `initialize_disaster(epicenters, initial_severity)`: Sparks a disaster event at specific nodes.
    - `step()`: Advances simulation by one temporal period. Simulates flood spread to neighboring nodes and accumulates infrastructure damage.
    - `_update_graph_edge_weights()`: Probabilistically removes network edges based on node damage, simulating bridge/road collapses. Increases traversal weights for surviving edges.
    - `get_routing_graph(vehicle_type)`: Returns the current network graph based on vehicle constraints (UAVs ignore collapsed roads).

### 4. Real Logistics Optimization (`optimization/logistics_optimizer.py`)
- **Class**: `LogisticsOptimizer`
- **Purpose**: Resolves constrained mathematical optimization problems using `PuLP` Mixed Integer Linear Programming (MILP).
- **Functions Used**:
    - `__init__(districts, warehouses, graph)`: Caches spatial data.
    - `apply_infrastructure_constraints(max_warehouses, excluded_warehouses)`: Dynamically purges destroyed nodes from the active pool and applies hard bounds on active hubs to strictly enforce localized operational failures before optimization.
    - `optimize_allocation(demands, inventory, ...)`: Constructs an LP problem to minimize shortages (alpha), transport costs (beta), and max-shortage/fairness (gamma). Enforces flow conservation, warehouse bounds, and vehicle capacity constraints. Outputs final discrete allocations.

### 5. Fairness Metrics (`fairness/fairness_metrics.py`)
- **Class**: `FairnessMetrics`
- **Purpose**: Statistical evaluation tools to penalize inequality in ML objectives.
- **Functions Used**:
    - `gini_coefficient(shortages)`: Computes economic Gini coefficient of deprivation across districts.
    - `max_min_fairness(shortages)`: Returns the maximum individual shortage (used to maximize the minimum welfare).
    - `calculate_fairness_penalty(shortages)`: Aggregates variance, Gini, and Max-Min into a unified penalty scaler for RL reward functions.
    - `evaluate_allocation_bias(shortages, vulnerability_scores)`: Computes correlation between vulnerability and shortages to flag AI bias against severe regions.

### 6. Explainable AI for RL (`explainability/rl_explainer.py`)
- **Class**: `RLExplainer`
- **Purpose**: Breaks down neural network and agent decisions into human-readable insights.
- **Functions Used**:
    - `__init__(agent_model, env)`: Binds the explainer to a live RL agent and its parent environment.
    - `generate_shap_explanations(background_states, current_state)`: Triggers `KernelExplainer` to interpret action weights.
    - `generate_reasoning(state, action, district_idx)`: Programmatically analyzes the state vector (shortage, road connection, flood) and maps it to a human-readable list of reasons and a confidence heuristic.
    - `generate_attention_weights(state)`: Mocks/extracts attention weightings corresponding to the severity combinations of specific districts.

---

## 🚄 Human-in-the-Loop & Execution Strategy

### HITL Workflow
1. **AI Recommends**: PPO agent / MILP solver generates baseline allocations.
2. **Human Overrides**: Using the `HumanOverrideDashboard`, a coordinator locks constraints (e.g., overriding truck usage).
3. **Re-optimization**: The system (`allocation.py`) digests the override and retriggers `LogisticsOptimizer` or inference, adjusting all other variables around the human's hard constraints.

### Execution Strategy
- **Static-Dynamic**: District vulnerability is statically pre-processed.
- **Dynamic Inference**: When a simulation starts, `disaster_simulator.py` continuously updates states. `ppo_agent.py` acts on those real-time states continuously until deprivation is zero or max steps are reached.
