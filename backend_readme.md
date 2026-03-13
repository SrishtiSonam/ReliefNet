# ReliefNet FastAPI Backend Documentation — v3.0

This document provides a comprehensive reference for the **ReliefNet Backend** at `backend/app/`.

---

## 1. Backend Overview

The backend is built on **FastAPI (Python 3.10+)** and serves as the high-performance computation hub. It handles:

- All ML, RL, and OR computation (asynchronous `BackgroundTasks`)
- Direct MongoDB read/write via `motor` async driver
- JWT-authenticated API endpoints for the Express Gateway to trigger and poll

---

## 2. Folder Structure

```text
backend/app/
├── auth/            # JWT authentication and security
├── data/            # Data ingestion, demand estimation, scenario generation
├── ml/              # All ML, RL, and research modules (see §4 for full reference)
├── models/          # Pydantic validation schemas
├── routers/         # FastAPI endpoint definitions
├── utils/           # logger.py, geo.py (Haversine)
├── database.py      # Async Motor MongoDB connection
└── main.py          # FastAPI entrypoint + CORS config

backend/tests/
└── test_ml_core.py  # 17 Pytest unit tests
```

---

## 3. ML Module Full Reference (`backend/app/ml/`)

### Core Framework

| File | Class / Functions | Purpose |
|------|-------------------|---------|
| `base_agent.py` | `BaseAgent` (ABC) | Defines `get_action()`, `evaluate()`, `train()`, `evaluate_summary()` contract |
| `config.py` | `SimulationConfig` | Single frozen dataclass for all 60+ hyperparameters across agents and research modules |
| `mdp.py` | `DistrictState`, `MDPState`, `MDPTransition`, `ScenarioGenerator` | Core MDP — state, transition, cost computation (supports optional road failure mask) |
| `deprivation.py` | `deprivation_cost()`, `marginal_deprivation_cost()`, `expected_deprivation_cost()` | Exponential deprivation cost model (Holguin-Veras et al., 2013) |

### Forecasting

| File | Class | Purpose |
|------|-------|---------|
| `demand_model.py` | `DemandForecaster` | Random Forest Regressor trained on historical district flood data |
| `flood_predictor.py` | `FloodPredictor` | PyTorch LSTM — predicts 3-7 day DFSI (District Flood Severity Index) sequences |

### Decision Agents

| File | Method Key | Algorithm |
|------|------------|-----------|
| `rule_based.py` | `rule_based` | Static urgency-score heuristic |
| `dl_vfa.py` | `dl_vfa` | Decomposed Linear Value Function Approximation |
| `nn_vfa.py` | `nn_vfa` | Neural Network Value Function Approximation |
| `ppo.py` | `ppo` | PPO with Dirichlet continuous action distribution (Actor-Critic) |
| `mip_solver.py` | `mip` | Exact PuLP + CBC MIP solver with warm-starting |
| `perfect_info.py` | `perfect_info` | Deterministic LP lower bound (oracle benchmark) |

### Research Improvements (v3.0)

| File | Method Key | Research Contribution |
|------|------------|-----------------------|
| `equity.py` | — | `gini_coefficient()`, `max_min_fairness_gap()`, `equity_penalty()` |
| `constrained_ppo.py` | `constrained_ppo` | PPO + dual Lagrangian equity constraint (auto-tunes λ for Gini + Max-Min fairness) |
| `marl_env.py` | — | `MARLEnvironment` — partial-observation multi-agent env with stochastic comms drops |
| `mappo.py` | `mappo` | Multi-Agent PPO (CTDE): per-warehouse local actor, shared centralised critic |
| `road_network.py` | — | `RoadNetwork` — sigmoid DFSI-driven edge failure probability model |
| `attention_ppo.py` | `attention_ppo` | Transformer self-attention actor; `explain_last_action()` returns per-district weights |
| `explainability.py` | — | `build_decision_explanation()` → JSON for React GIS overlay; `decision_confidence()` |
| `gnn_warm_start.py` | — | 2-layer GCN (`GNNWarmStartPredictor`) — predicts MIP warm-starts from district graph |
| `gymnasium_env.py` | — | `FloodReliefEnv(gymnasium.Env)` — standard RL benchmark environment wrapper |

### Evaluation & Multi-depot

| File | Class | Purpose |
|------|-------|---------|
| `benchmark.py` | `BenchmarkRunner` | Evaluates all 9 agents under identical seeds; computes `gap_to_perfect_pct` |
| `multi_depot.py` | — | Multi-depot warehouse coordination with DB/dev source tracking |
| `multi_commodity.py` | — | Multi-commodity greedy allocation fallback |

---

## 4. `SimulationConfig` — Hyperparameter Reference

`backend/app/ml/config.py` — a frozen dataclass that is the single source of truth for all hyperparameters.

```python
from app.ml.config import SimulationConfig

cfg = SimulationConfig(
    # Vehicle capacities
    truck_cap=5000.0, uav_cap=200.0,

    # MDP
    n_periods=30, discount=0.9,

    # PPO
    ppo_lr=0.0001, ppo_clip_eps=0.2, ppo_gamma=0.99,

    # Improvement 1 — Equity
    equity_lambda_gini=0.3,    # Gini weight in Lagrangian penalty
    equity_lambda_maxmin=0.1,  # Max-Min fairness weight

    # Improvement 2 — MAPPO
    marl_n_agents=3,           # Number of warehouse agents
    marl_comm_drop_prob=0.2,   # Comms blackout probability per step

    # Improvement 3 — Road Failures
    road_use_failures=False,   # Set True to enable stochastic failures
    road_failure_k=3.0,        # Sigmoid steepness

    # Improvement 4 — Attention PPO
    attn_d_model=32,           # District embedding dimension
    attn_n_heads=1,            # Self-attention heads

    # Improvement 5 — GNN Warm-Start
    gnn_use_warm_start=False,  # Set True to use GNN for MIP warm-starting
    gnn_hidden_dim=16,         # GCN hidden dimension
    gnn_n_layers=2,            # GCN layers

    # MIP
    mip_time_limit_sec=30, mip_max_trucks=10, mip_max_uavs=20,
)
```

---

## 5. Running the Backend

### With Docker (Recommended)

```bash
cd ReliefNet
docker-compose up --build
```

### Locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Swagger UI:** http://localhost:8000/docs

---

## 6. Running Tests

```bash
cd backend
pytest tests/test_ml_core.py -v
```

The suite includes **17 tests** — 9 original core tests + 8 new tests for all research improvements.

---

## 7. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/token` | Get JWT Bearer token |
| `GET` | `/api/districts` | List all districts |
| `GET` | `/api/flood-events` | List flood events |
| `POST` | `/api/simulation/run` | Run simulation (specify `method` in body) |
| `GET` | `/api/simulation/{id}` | Poll results — includes `gini`, `attention_weights`, `gap_to_perfect_pct` |
| `POST` | `/api/data/load-all` | Trigger CSV → MongoDB ingestion |

**Available `method` values for simulation:**
`ppo`, `constrained_ppo`, `mappo`, `attention_ppo`, `dl_vfa`, `nn_vfa`, `mip`, `rule_based`

---

## 8. Interaction Flow

```
routers/simulation.py
  → instantiate DemandForecaster, FloodPredictor
  → build MDPState + ScenarioGenerator
  → instantiate agent (e.g. ConstrainedPPOAgent)
  → optionally build RoadNetwork from DFSI scores
  → agent.train() [if RL]
  → agent.evaluate() → returns cost + equity + attention metrics
  → save results to MongoDB
```
