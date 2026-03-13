# ReliefNet — Backend Full Flow & File Guide

## Top-Level Structure

```
backend/
├── .env                  ← Secret keys & DB URI (loaded by config.py)
├── Dockerfile            ← Container definition to run the app
├── requirements.txt      ← All Python dependencies
├── tests/                ← Unit tests
├── datasets/             ← Raw CSV/JSON data (INDOFLOODS, district data)
└── app/                  ← All application code lives here
```

---

## Application Entry Point

### `app/main.py`
The heart of the server. FastAPI app starts here.

- Creates the `FastAPI` app instance
- Registers **CORS** middleware (so React frontend on `:3000` can call the API)
- Mounts all routers under their URL prefixes:

| Router | URL Prefix |
|---|---|
| districts | `/api/districts` |
| flood_events | `/api/flood-events` |
| simulation | `/api/simulation` |
| allocation | `/api/allocation` |
| data_ingestion | `/api/data` |
| ML extensions | `/api/ml` |
| Auth | `/api/auth` |

- On **startup** → connects to MongoDB
- On **shutdown** → disconnects from MongoDB

---

## Core Config & Database

### `app/config.py`
Reads `.env` using Pydantic. Exposes a single `settings` object:
- `MONGO_URI` — MongoDB address
- `MONGO_DB` — Database name (`flood_relief_india`)
- `SECRET_KEY` — Used for JWT signing

### `app/database.py`
Manages the async MongoDB connection (`motor` driver):
- `connect_db()` — called on startup, creates the global `db` object
- `disconnect_db()` — called on shutdown
- `get_db()` — called by routers to get a reference to the DB

---

## Auth Layer

### `app/auth/jwt_handler.py`
All authentication logic:
- `hash_password()` / `verify_password()` — bcrypt password hashing
- `create_access_token()` — 8-hour JWT with `sub`, `email`, `role`
- `create_refresh_token()` — 7-day refresh token
- `decode_token()` — verifies + decodes a JWT
- `get_current_user()` — FastAPI dependency, injects logged-in user into any route
- `require_admin()` / `require_manager_or_above()` — role-based access control

### `app/routers/auth.py`
HTTP routes for auth: `/login`, `/register`, `/refresh`, `/me`. Uses `jwt_handler.py` to do the work.

---

## Routers (API Endpoints)

| File | URL | What it does |
|---|---|---|
| `routers/districts.py` | `/api/districts` | CRUD for Indian districts (name, coords, population) |
| `routers/flood_events.py` | `/api/flood-events` | Log & query flood events |
| `routers/allocation.py` | `/api/allocation` | Trigger a one-shot MIP/rule-based allocation |
| `routers/data_ingestion.py` | `/api/data` | Upload or refresh datasets |
| `routers/simulation.py` | `/api/simulation` | Run full multi-period RL/MDP simulation |
| `routers/ml_extensions.py` | `/api/ml` | Demand forecast, flood prediction, benchmarks, explainability, MARL |

---

## Data Models (Pydantic Schemas)

Define the shape of data in requests/responses and in MongoDB:

| File | Defines |
|---|---|
| `models/district.py` | `District` schema |
| `models/flood_event.py` | `FloodEvent` schema |
| `models/simulation.py` | `SimulationConfig` (API input) + `SimulationRun` |
| `models/allocation.py` | `AllocationRequest` + `AllocationResult` |
| `models/warehouse.py` | `Warehouse` (depot location, capacity) |

---

## Data Layer (`app/data/`)

| File | What it does |
|---|---|
| `loader.py` | Loads CSVs from `datasets/` (INDOFLOODS, district metadata) |
| `demand_estimator.py` | Estimates demand for a district from flood severity + population |
| `cost_calculator.py` | Computes UAV & truck transport costs from distance |
| `scenario_gen.py` | Builds a `ScenarioGenerator` from real data statistics |
| `preprocessor.py` | Cleans/normalises raw data before use |

---

## ML Engine (`app/ml/`)

### Core MDP Framework

| File | Role |
|---|---|
| `config.py` | All hyperparameters in one frozen `SimulationConfig` dataclass |
| `mdp.py` | Core MDP: `DistrictState`, `MDPState`, `MDPTransition`, `ScenarioGenerator` |
| `deprivation.py` | Deprivation cost functions Φ(δ) — quantifies how bad a shortage is |

### Solver / Agent Algorithms

Each agent implements `.train(scen_gen, init_state, episodes)` + `.evaluate(...)`:

| File | Algorithm |
|---|---|
| `base_agent.py` | Abstract base class all agents inherit from |
| `rule_based.py` | Simple proportional heuristic (no learning) |
| `nn_vfa.py` | Neural Network Value Function Approximation |
| `dl_vfa.py` | Deep Learning VFA (larger network, Adam optimizer) |
| `ppo.py` | Proximal Policy Optimization (standard RL) |
| `constrained_ppo.py` | PPO with equity/fairness constraints |
| `attention_ppo.py` | PPO with self-attention over districts (explainable) |
| `mappo.py` | Multi-Agent PPO — cooperative warehouse agents |
| `perfect_info.py` | Oracle solver (knows future demand) — benchmark upper bound |
| `mip_solver.py` | PuLP Mixed Integer Programming solver |
| `multi_commodity.py` | MIP extended to food/water/medicine/shelter separately |
| `multi_depot.py` | Allocates from multiple warehouses simultaneously |

### Supporting ML Modules

| File | Role |
|---|---|
| `demand_model.py` | Random Forest predicting district demand from flood features |
| `flood_predictor.py` | LSTM forecasting flood intensity 3–7 days ahead |
| `gymnasium_env.py` | Wraps the MDP as a standard Gym environment for RL training |
| `marl_env.py` | Multi-agent Gym environment for MAPPO |
| `road_network.py` | Graph of road connections; simulates road failures during floods |
| `gnn_warm_start.py` | GNN that gives MIP solver a warm-start solution |
| `equity.py` | Gini coefficient + max-min gap metrics for fairness |
| `explainability.py` | Extracts attention weights to explain which districts got priority |
| `benchmark.py` | Runs all agents head-to-head and returns comparison metrics |

---

## Utils (`app/utils/`)

| File | Role |
|---|---|
| `logger.py` | Centralised structured logging via `get_logger(__name__)` |
| `geo.py` | Geospatial helpers (distance calculations between coordinates) |

---

## Full Request Flow — "Run a Simulation"

End-to-end flow when the frontend triggers a simulation:

```
Frontend (React)
    │  POST /api/simulation/run  { districts, method="ppo", n_periods=30 }
    ▼
routers/simulation.py  →  validates SimulationConfig (Pydantic)
    │  Saves a pending record to MongoDB
    │  Fires a BackgroundTask (response returns immediately)
    ▼
_run_simulation_task()
    ├─ data/demand_estimator.py   →  estimates demand per district
    ├─ data/cost_calculator.py    →  computes truck/UAV costs
    ├─ ml/mdp.py                  →  builds DistrictState + MDPState (initial state)
    ├─ data/scenario_gen.py       →  creates ScenarioGenerator (stochastic paths)
    │
    └─ selects agent by method:
         "ppo"        → ml/ppo.py           PPOAgent.train() → .evaluate()
         "dl_vfa"     → ml/dl_vfa.py        DLVFA.train()    → .evaluate()
         "nn_vfa"     → ml/nn_vfa.py        NNVFA.train()    → .evaluate()
         "rule_based" → ml/rule_based.py    (no training)    → .evaluate()
              │
              │  Each agent internally uses:
              │    ml/mdp.py        → MDPTransition.transition()   (step the world)
              │    ml/mdp.py        → MDPTransition.compute_cost() (deprivation + transport)
              │    ml/deprivation.py→ Φ(δ) deprivation cost functions
              ▼
    Results written back to MongoDB
    ▼
Frontend polls  GET /api/simulation/{id}  →  gets status + results
```

---

## Architecture Overview

```
.env / config.py
      │
      ▼
  database.py  ──────────────────────────────────────┐
      │                                               │
  main.py  (FastAPI app)                           MongoDB
      │                                               ▲
  ┌───┴──────────────────────────────────────┐        │
  │             Routers layer                │────────┘
  │  auth · districts · flood_events         │
  │  simulation · allocation · ml_extensions │
  └───┬──────────────────────────────────────┘
      │
  ┌───┴──────────────────────────────────────┐
  │              Data layer                  │
  │  loader · demand_estimator · cost_calc   │
  │  scenario_gen · preprocessor             │
  └───┬──────────────────────────────────────┘
      │
  ┌───┴──────────────────────────────────────┐
  │            ML Engine  (app/ml/)          │
  │  mdp ← deprivation ← config             │
  │  Agents: ppo · dl_vfa · nn_vfa · mappo  │
  │  Solvers: mip · multi_commodity          │
  │           multi_depot · perfect_info     │
  │  Support: flood_predictor · demand_model │
  │           gnn_warm_start · road_network  │
  │           equity · explainability        │
  └──────────────────────────────────────────┘
```

---

*Generated: 2026-03-13 | ReliefNet v2.0*
