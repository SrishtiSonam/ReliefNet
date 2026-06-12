# ReliefNet — AI-Powered Disaster Relief Logistics Platform

> Full-stack platform combining reinforcement learning, constrained optimization, GIS routing, and explainable AI for post-disaster resource allocation — built on real India flood datasets.

ReliefNet optimizes the dispatch of trucks and UAVs from pre-positioned warehouses to disaster-affected districts. It merges stochastic infrastructure simulation, RL-based planning, fairness-constrained MILP, and a human-in-the-loop override workflow into a single operational platform.

---

## Architecture Overview

### Method 1 — AI-Based Stochastic Dynamic Resource Allocation
Intelligent allocation and routing of relief resources using:
- **PPO** (Stable-Baselines3) for single-agent warehouse dispatching
- **MAPPO** (custom PyTorch CTDE) for multi-agent fleet coordination
- **MILP** (PuLP) for fairness-constrained allocation
- **NetworkX** for risk-aware road graph routing
- Truck + UAV hybrid logistics with last-mile drone delivery

### Method 2 — Operational Awareness & Human Coordination
Real-time coordination and public engagement through:
- Citizen emergency request portal
- Responder triage dashboard
- Human-in-the-Loop (HITL) AI override workflow
- SHAP-based explainable AI reasoning
- District and warehouse monitoring dashboards

---

## 8-Phase Workflow

| Phase | Name | What Happens |
|---|---|---|
| 1 | Multi-Source Disaster Intelligence | GIS, population, warehouse, weather, citizen request data |
| 2 | Demand Forecasting | XGBoost predicts district-level relief demand |
| 3 | Infrastructure & Risk Simulation | Stochastic flood propagation, road collapse, damage accumulation |
| 4 | RL Decision Engine | PPO/MAPPO agents dispatch trucks and UAVs |
| 5 | Fairness-Constrained Optimization | PuLP MILP minimizes shortage, transport cost, and Gini inequality |
| 6 | GIS-Based Adaptive Routing | NetworkX computes safe routes on dynamically degraded road graph |
| 7 | Explainable AI & HITL | SHAP explanations + human override and re-optimization |
| 8 | Dashboards & Public Portal | Operator dashboards, citizen request portal, request triage |

---

## AI & ML Stack

| Component | Technology | Status |
|---|---|---|
| RL Agent (Single) | PPO via Stable-Baselines3 | Implemented |
| RL Agent (Multi) | MAPPO — custom PyTorch CTDE | Implemented (training loop stub) |
| Optimization | PuLP MILP solver | Implemented |
| Demand Forecasting | XGBoost (trained model saved) | Implemented |
| Explainability | SHAP (`TreeExplainer`) | Implemented |
| Disaster Simulation | Custom stochastic engine | Implemented |
| Fairness Metrics | Gini coefficient, max-min fairness | Implemented |
| RL Environment | Custom Gymnasium `DisasterReliefEnv` | Implemented |
| GIS Routing | NetworkX shortest path + hazard weights | Implemented |

---

## Tech Stack

### Backend

| Package | Version | Role |
|---|---|---|
| **FastAPI** | ≥0.110 | Async REST API framework |
| **Uvicorn** | ≥0.29 | ASGI server |
| **Starlette** | ≥0.36 | ASGI toolkit (used directly for responses) |
| **Pydantic v2** | ≥2.6 | Request/response schema validation |
| **pydantic-settings** | ≥2.2 | `.env`-based `Settings` class |
| **Motor** | ≥3.3 | Async MongoDB driver |
| **PyMongo** | ≥4.6 | Sync MongoDB utilities (index creation, seeding) |
| **python-jose[cryptography]** | ≥3.3 | JWT encoding and decoding |
| **passlib[bcrypt]** | ≥1.7 | Password hashing |
| **python-multipart** | ≥0.0.9 | OAuth2 form body parsing |
| **python-dotenv** | ≥1.0 | `.env` file loading |

**API modules (v1):** `auth` · `allocation` · `disasters` · `districts` · `explainability` · `forecasting` · `requests` · `simulation` · `warehouses`

**Roles:** `CITIZEN` · `RESPONDER` · `STATE_AUTHORITY` · `CENTRAL_AUTHORITY`

---

### Frontend

| Package | Version | Role |
|---|---|---|
| **React** | 19.x | UI framework |
| **TypeScript** | ~6.0 | Static typing |
| **Vite** | 8.x | Dev server and bundler |
| **Tailwind CSS** | v4.3 | Utility-first styling |
| **Zustand** | 5.x | Global state (`authStore`, `districtStore`) |
| **TanStack Query** | 5.x | Server state, caching, background refetch |
| **React Router DOM** | 7.x | Client-side routing |
| **Axios** | 1.x | HTTP client with JWT interceptor |
| **Recharts** | 3.x | Charts and analytics visualizations |
| **Leaflet + React-Leaflet** | 1.9 / 5.x | Interactive GIS maps (OpenStreetMap tiles) |
| **Lucide React** | 1.x | Icon library |
| **clsx + tailwind-merge** | — | Conditional class name utilities |

**Pages:** `Dashboard` · `DistrictMonitor` · `WarehouseMonitor` · `SimulationPage` · `AllocationView` · `PublicPortal` · `RequestsView` · `Settings` · `Login`

**Key components:** `RLSimulationDashboard` · `HumanOverrideDashboard` · `ReliefMap` · `MainLayout` · `StatCard`

---

### AI / ML

| Package | Role |
|---|---|
| **Stable-Baselines3** | PPO single-agent RL training and inference |
| **PyTorch** | Custom MAPPO actor-critic networks (CTDE architecture) |
| **Gymnasium** | Custom `DisasterReliefEnv` RL environment |
| **PuLP (CBC solver)** | MILP for fairness-constrained resource allocation |
| **NetworkX** | Road network graph, shortest-path routing with hazard weights |
| **XGBoost** | Demand forecasting (trained model persisted as `demand_forecaster.json`) |
| **SHAP** | `TreeExplainer` for per-feature allocation transparency |
| **scikit-learn** | Preprocessing and feature pipelines |
| **NumPy** | Array operations throughout ML stack |
| **Pandas** | Data manipulation, CSV ingestion, feature engineering |

**Custom implementations:**
- `DisasterSimulator` — stochastic flood graph-diffusion + probabilistic road collapse per step
- `MAPPOAgentFramework` — centralized training / decentralized execution (CTDE) from scratch in PyTorch
- `LogisticsOptimizer` — MILP that jointly minimizes shortage + transport cost + Gini unfairness
- `FairnessMetrics` — Gini coefficient and max-min fairness calculations
- `DisasterReliefEnv` — Gymnasium environment wrapping the simulator for RL training

---

### Infrastructure & Tooling

| Tool | Role |
|---|---|
| **Docker** | Containerised backend, frontend, and MongoDB |
| **Docker Compose** | Multi-service orchestration |
| **nginx** | Static file serving + SPA fallback routing for frontend |
| **Jupyter Notebook** | EDA, data pipeline, model training entrypoint (`reliefnet_notebook.ipynb`) |
| **ESLint** | Frontend linting (react-hooks + react-refresh plugins) |
| **Git** | Version control |

---

### Datasets

| Dataset | Format | Content |
|---|---|---|
| EM-DAT Database | XLSX | Historical global disaster events — deaths, affected, damage (USD) |
| IndoFloods — flood events | CSV | India flood events with discharge, severity, duration |
| IndoFloods — catchment characteristics | CSV | Drainage area, slope, land use per catchment |
| IndoFloods — precipitation variables | CSV | Rainfall metrics per event |
| IndoFloods — metadata | CSV | Station and basin metadata |
| India District Dataset | CSV | District-level demographics and geographic features |
| India Flood Inventory v3 | CSV | Georeferenced flood polygons across India |
| flood_risk_dataset_india | CSV | District-level flood risk scores |
| DFSI | CSV | District Flood Severity Index |
| District_FloodedArea | CSV | Flooded area per district per event |
| District_FloodImpact | CSV | Impact metrics per district per event |
| Kerala district-wise details | CSV | District-level flood details, Kerala |
| Kerala warnings (actual vs. predicted) | CSV | Forecast validation data |
| Post Offices | CSV | Geographic distribution of India post offices |
| State Hazard Atlases | PDF | Flood zone maps — AP, Bihar, UP, Odisha, West Bengal, Kerala, Assam |
| Processed exports | CSV | `reliefnet_district_features.csv`, `reliefnet_road_network.csv` (generated by notebook) |

---

### Not Implemented

The following appear in older documentation but are **not present** in the codebase:

- ARIMA / GARCH forecasting — only XGBoost is implemented; `forecasting/service.py` is a placeholder stub
- MAPPO training loop — `update()` method is a documented stub; only inference (`get_actions`) is functional
- Mobile app (React Native / Expo / WatermelonDB) — no `mobile/` directory exists
- Framer Motion — listed in inner README but not in `package.json`
- Prometheus / monitoring — no metrics instrumentation
- Test suite — no `pytest` or Vitest test files

---

## Project Structure

```text
ReliefNet/
├── reliefnet/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/            # REST endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── allocation.py
│   │   │   │   ├── disasters.py
│   │   │   │   ├── districts.py
│   │   │   │   ├── explainability.py
│   │   │   │   ├── forecasting.py
│   │   │   │   ├── requests.py
│   │   │   │   ├── simulation.py
│   │   │   │   └── warehouses.py
│   │   │   ├── core/
│   │   │   │   ├── auth/          # JWT handler, role guards
│   │   │   │   ├── explainability/# SHAP service
│   │   │   │   ├── hitl/          # Override workflow
│   │   │   │   ├── optimization/  # MILP service
│   │   │   │   └── simulation/    # Flood model, shortage estimator
│   │   │   ├── db/
│   │   │   │   ├── mongo.py
│   │   │   │   └── repositories/  # allocation, disaster, district, warehouse, ...
│   │   │   ├── models/            # Pydantic schemas
│   │   │   └── main.py
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   └── src/
│   │       ├── pages/             # Dashboard, DistrictMonitor, WarehouseMonitor,
│   │       │                      # SimulationPage, AllocationView, PublicPortal,
│   │       │                      # RequestsView, Settings, Login
│   │       ├── components/
│   │       │   ├── layout/        # MainLayout
│   │       │   ├── map/           # ReliefMap (Leaflet)
│   │       │   ├── rl/            # RLSimulationDashboard, HumanOverrideDashboard
│   │       │   └── cards/         # StatCard
│   │       ├── api/               # allocationApi, districtApi, simulationApi, ...
│   │       └── store/             # authStore, districtStore (Zustand)
│   │
│   ├── ml_services/
│   │   ├── environments/          # DisasterReliefEnv (Gymnasium)
│   │   ├── rl_agents/             # ppo_agent.py, mappo_agent.py
│   │   ├── optimization/          # logistics_optimizer.py (MILP), route_planner.py
│   │   ├── simulation/            # disaster_simulator.py
│   │   ├── explainability/        # shap_explainer.py, rl_explainer.py
│   │   ├── forecasting/           # xgboost_service.py, service.py
│   │   ├── fairness/              # fairness_metrics.py
│   │   ├── models/                # demand_forecaster.json (saved XGBoost)
│   │   └── training_pipeline.py
│   │
│   ├── data/exports/              # reliefnet_district_features.csv, reliefnet_road_network.csv
│   ├── scratch/                   # generate_synthetic_data.py
│   └── reliefnet_notebook.ipynb   # EDA, training, data pipeline
│
├── datasets/                      # Raw India flood datasets (CSVs, PDFs)
│   ├── EM-DAT Database.xlsx
│   ├── India_Flood_Inventory_v3.csv
│   ├── flood_risk_dataset_india.csv
│   ├── India_District_Dataset.csv
│   └── Flood PDF/                 # State hazard atlases
│
├── Research Papers/               # 20 academic papers on disaster logistics & RL
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Key Data Models (MongoDB)

```python
# DisasterEvent (from EM-DAT)
{
  "dis_no": str,
  "disaster_type": str,           # flood | earthquake | cyclone
  "district": str,
  "district_lgd_code": str,
  "total_deaths": float,
  "total_affected": float,
  "latitude": float, "longitude": float,
  "season": str,                  # Monsoon | Post-Monsoon | Winter | Pre-Monsoon
  "recency_weight": float
}

# Warehouse
{
  "location": { "lat": float, "lng": float },
  "district": str,
  "inventory": [{ "item": str, "quantity": int }],
  "accessibility_score": float,
  "is_operational": bool
}

# Citizen Emergency Request
{
  "location": { "lat": float, "lng": float },
  "needs": ["food", "water", "medical", "rescue"],
  "severity": "low | medium | critical",
  "status": "pending | assigned | resolved"
}

# AllocationPlan
{
  "truck_allocations": { "(warehouse, district)": int },
  "uav_allocations":   { "(warehouse, district)": int },
  "final_shortages":   { "district": float },
  "objective_value": float,
  "status": "Optimal | Infeasible"
}
```

---

## Authentication

```text
POST /api/v1/auth/login → JWT (access + refresh)
All endpoints: Authorization: Bearer <token>
```

**Roles:**

| Role | Access |
|---|---|
| CITIZEN | Emergency requests, shelter maps, alerts |
| RESPONDER | Vehicle tracking, delivery updates, HITL overrides |
| STATE_AUTHORITY | District coordination, roadblock reporting |
| CENTRAL_AUTHORITY | Full dashboard, AI plans, analytics, audit |

---

## Simulation Flow

```text
1. Configure disaster (type, epicenter, severity)
2. DisasterSimulator propagates flood intensity + infrastructure damage per step
3. Dynamic road collapse: edges fail stochastically based on node damage
4. PPO/MAPPO agents predict dispatch actions
5. PuLP MILP refines allocation under fairness + capacity constraints
6. Operator reviews SHAP-explained plan via HITL dashboard
7. Overrides applied → re-optimization triggered
8. Final plan dispatched; citizen portal and request triage updated
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Authenticate and receive JWT |
| GET | `/api/v1/districts/` | List all districts |
| GET | `/api/v1/warehouses/` | List warehouses with inventory |
| GET | `/api/v1/disasters/` | Query disaster events |
| POST | `/api/v1/simulation/run` | Run disaster simulation step |
| POST | `/api/v1/allocation/optimize` | Run MILP allocation |
| GET | `/api/v1/forecast/` | District demand forecast |
| GET | `/api/v1/explain/` | SHAP explanations for allocation |
| GET/POST | `/api/v1/requests/` | Citizen emergency requests |
| GET | `/health` | Health check |

---

## Installation & Setup

### Docker (recommended)

```bash
cp .env.example .env
# Edit .env — set JWT_SECRET_KEY to a random string

docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| MongoDB | localhost:27017 (internal) |

To seed initial data:

```bash
docker-compose exec backend python seed.py
```

---

### Manual Setup

#### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

#### Backend

```bash
cd reliefnet/backend
python -m venv env
.\env\Scripts\activate          # Windows
# source env/bin/activate       # macOS/Linux

pip install -r requirements.txt
pip install gymnasium "stable-baselines3[extra]" shap \
            torch --index-url https://download.pytorch.org/whl/cpu

# Create a .env file in reliefnet/backend/ (see .env.example)
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd reliefnet/frontend
npm install
npm run dev
```

#### ML Training Pipeline

Run the Jupyter notebook first to generate district features and road network exports:

```bash
cd reliefnet
jupyter notebook reliefnet_notebook.ipynb
```

Then run the training pipeline:

```bash
cd reliefnet
python -m ml_services.training_pipeline
```

---

## Environment Variables

```env
# Backend (matches pydantic-settings field names in config.py)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=reliefnet
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
DATA_EXPORT_DIR=../data/exports

# Frontend (Vite build-time injection)
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Key Innovations

**RL + MILP Hybrid** — PPO/MAPPO agents plan dispatch strategies; PuLP MILP enforces capacity and fairness constraints simultaneously.

**Fairness-Aware Allocation** — Max-Min fairness and Gini minimization prevent remote or low-priority districts from being neglected under resource scarcity.

**Stochastic Infrastructure Failure** — The `DisasterSimulator` models flood propagation as a graph diffusion process; edges fail probabilistically as node damage accumulates, forcing the optimizer to reroute in real time.

**Truck + UAV Coordination** — MILP jointly optimizes truck routes on the degraded road graph and UAV flights over the unimpeded air graph for last-mile isolated zones.

**Explainable AI** — SHAP `TreeExplainer` provides feature-level contribution scores for every demand forecast, giving operators transparent reasoning before they approve or override the AI plan.

**Human-in-the-Loop** — Operators can exclude warehouses, cap vehicle counts, or override district priorities mid-simulation; the system re-runs optimization under the new constraints.

---

## Research Foundation

Based on academic research in stochastic post-disaster inventory allocation using trucks and UAVs, extended with:
- Multi-agent PPO (MAPPO) with centralized training / decentralized execution
- Fairness-constrained MILP (Gini minimization, max-min fairness)
- SHAP explainability layer for allocation transparency
- Real-time citizen coordination and HITL override workflows
- India-specific flood data (EM-DAT, IndoFloods, state hazard atlases)

20 reference papers are included in `Research Papers/`.

---

## License

MIT License
