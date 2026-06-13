# ReliefNet — AI-Powered Disaster Relief Web Platform

> A full-stack web platform for real-time disaster relief coordination — interactive maps, AI-generated allocation plans, human override workflows, and a citizen emergency portal.

ReliefNet gives operators, responders, and citizens a single web interface to monitor disaster events, manage warehouse inventory, review AI resource allocation decisions, and submit emergency requests — all backed by a REST API with role-based access control.

---

## What the Website Does

- **Operators & authorities** monitor affected districts and warehouse stock in real time via live dashboards and an interactive GIS map.
- **Responders** review AI-generated truck/UAV dispatch plans, inspect SHAP-explained reasoning, and apply manual overrides before approving.
- **Citizens** submit emergency requests (food, water, medical, rescue) through a public portal and track their status.
- **State/Central authorities** run disaster simulations, trigger AI optimization, and audit all allocation decisions.

---

## Pages

| Page | Description | Access |
|---|---|---|
| **Login** | JWT-based sign-in | All |
| **Dashboard** | System-wide KPIs, alerts, and health overview | Responder+ |
| **District Monitor** | Per-district demand, risk score, shortage metrics | Responder+ |
| **Warehouse Monitor** | Inventory levels, operational status, vehicle capacity | Responder+ |
| **Simulation** | Configure and step through a disaster simulation | State / Central |
| **Allocation View** | Review AI-generated truck and UAV dispatch plan | Responder+ |
| **Human Override Dashboard** | SHAP explanations + operator override controls | Responder+ |
| **Public Portal** | Citizen emergency request submission and tracking | Citizen |
| **Requests View** | Triage and assign inbound citizen requests | Responder+ |
| **Settings** | User preferences | All |

---

## Roles

| Role | Access |
|---|---|
| `CITIZEN` | Public portal — submit and track emergency requests |
| `RESPONDER` | Request triage, delivery updates, HITL overrides |
| `STATE_AUTHORITY` | District coordination, roadblock reporting |
| `CENTRAL_AUTHORITY` | Full dashboard, AI plans, analytics, audit trail |

JWT tokens are issued on login and attached automatically to every API call via the Axios interceptor.

---

## Frontend

### Tech Stack

| Package | Version | Role |
|---|---|---|
| **React** | 19.x | UI framework |
| **TypeScript** | ~6.0 | Static typing |
| **Vite** | 8.x | Dev server and bundler |
| **Tailwind CSS** | v4.3 | Utility-first styling |
| **Zustand** | 5.x | Global state (`authStore`, `districtStore`) |
| **TanStack Query** | 5.x | Server state, caching, background refetch |
| **React Router DOM** | 7.x | Client-side routing with role guards |
| **Axios** | 1.x | HTTP client with JWT interceptor |
| **Recharts** | 3.x | Charts and data visualizations |
| **Leaflet + React-Leaflet** | 1.9 / 5.x | Interactive GIS map (OpenStreetMap tiles) |
| **Lucide React** | 1.x | Icon library |
| **clsx + tailwind-merge** | — | Conditional class name utilities |

### Key Components

| Component | What it does |
|---|---|
| `ReliefMap` | Interactive map overlaying districts, warehouses, and delivery routes |
| `RLSimulationDashboard` | Simulation step controls and agent dispatch output |
| `HumanOverrideDashboard` | SHAP feature explanations and operator override form |
| `StatCard` | Reusable KPI tile used across dashboard pages |
| `MainLayout` | Sidebar navigation, role-aware route guards, global header |

### Structure

```text
reliefnet/frontend/src/
├── pages/             # One file per page (Dashboard, Login, PublicPortal, ...)
├── components/
│   ├── layout/        # MainLayout, sidebar, nav
│   ├── map/           # ReliefMap (Leaflet)
│   ├── rl/            # RLSimulationDashboard, HumanOverrideDashboard
│   └── cards/         # StatCard
├── api/               # allocationApi, districtApi, simulationApi, ...
└── store/             # authStore, districtStore (Zustand)
```

---

## Backend

### Tech Stack

| Package | Version | Role |
|---|---|---|
| **FastAPI** | ≥0.110 | Async REST API framework |
| **Uvicorn** | ≥0.29 | ASGI server |
| **Pydantic v2** | ≥2.6 | Request/response schema validation |
| **pydantic-settings** | ≥2.2 | `.env`-based settings |
| **Motor** | ≥3.3 | Async MongoDB driver |
| **PyMongo** | ≥4.6 | Sync MongoDB utilities |
| **python-jose[cryptography]** | ≥3.3 | JWT encoding / decoding |
| **passlib[bcrypt]** | ≥1.7 | Password hashing |
| **python-multipart** | ≥0.0.9 | OAuth2 form body parsing |
| **python-dotenv** | ≥1.0 | `.env` file loading |

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Authenticate and receive JWT |
| GET | `/api/v1/districts/` | List all districts |
| GET | `/api/v1/warehouses/` | List warehouses with inventory |
| GET | `/api/v1/disasters/` | Query disaster events |
| POST | `/api/v1/simulation/run` | Run a disaster simulation step |
| POST | `/api/v1/allocation/optimize` | Run AI resource allocation |
| GET | `/api/v1/forecast/` | District demand forecast |
| GET | `/api/v1/explain/` | SHAP explanations for current allocation |
| GET / POST | `/api/v1/requests/` | Citizen emergency requests |
| GET | `/health` | Health check |

Interactive API docs available at `http://localhost:8000/docs` (Swagger UI).

### Structure

```text
reliefnet/backend/app/
├── api/v1/            # Route handlers (auth, allocation, districts, ...)
├── core/
│   ├── auth/          # JWT handler, role guards
│   ├── explainability/# SHAP service
│   ├── hitl/          # Human override workflow
│   ├── optimization/  # MILP allocation service
│   └── simulation/    # Flood model, shortage estimator
├── db/
│   ├── mongo.py
│   └── repositories/  # Per-collection data access
├── models/            # Pydantic schemas
└── main.py
```

---

## AI / ML Stack

The website's simulation, allocation, forecasting, and explainability features are powered by the following ML services:

| Package | Role |
|---|---|
| **Stable-Baselines3** | PPO single-agent RL — warehouse dispatch planning |
| **PyTorch** | Custom MAPPO actor-critic networks (CTDE architecture) |
| **Gymnasium** | Custom `DisasterReliefEnv` RL environment |
| **PuLP (CBC solver)** | MILP for fairness-constrained resource allocation |
| **NetworkX** | Road network graph, shortest-path routing with hazard weights |
| **XGBoost** | District-level demand forecasting (model saved as `demand_forecaster.json`) |
| **SHAP** | `TreeExplainer` for per-feature allocation transparency |
| **scikit-learn** | Preprocessing and feature pipelines |
| **NumPy / Pandas** | Array operations, CSV ingestion, feature engineering |

### Custom Implementations

- `DisasterSimulator` — stochastic flood graph-diffusion + probabilistic road collapse per step
- `MAPPOAgentFramework` — centralized training / decentralized execution (CTDE) built from scratch in PyTorch
- `LogisticsOptimizer` — MILP that jointly minimizes shortage + transport cost + Gini unfairness
- `FairnessMetrics` — Gini coefficient and max-min fairness calculations
- `DisasterReliefEnv` — Gymnasium environment wrapping the simulator for RL training

### ML Training Pipeline

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

### ML Structure

```text
reliefnet/ml_services/
├── environments/      # DisasterReliefEnv (Gymnasium)
├── rl_agents/         # ppo_agent.py, mappo_agent.py
├── optimization/      # logistics_optimizer.py (MILP), route_planner.py
├── simulation/        # disaster_simulator.py
├── explainability/    # shap_explainer.py, rl_explainer.py
├── forecasting/       # xgboost_service.py, service.py
├── fairness/          # fairness_metrics.py
├── models/            # demand_forecaster.json (saved XGBoost model)
└── training_pipeline.py
```

---

## Datasets

All datasets are India-specific and power the demand forecasting, risk simulation, and GIS routing shown in the website.

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

## Research Foundation

20 reference papers are included in `Research Papers/`, covering:

- Stochastic post-disaster inventory allocation using trucks and UAVs
- Multi-agent PPO (MAPPO) with centralized training / decentralized execution
- Fairness-constrained MILP (Gini minimization, max-min fairness)
- SHAP explainability for allocation transparency
- Real-time citizen coordination and human-in-the-loop override workflows
- India-specific flood modelling (EM-DAT, IndoFloods, state hazard atlases)

---

## Setup

### Docker (recommended)

Spins up frontend, backend, and MongoDB together:

```bash
cp .env.example .env
# Set JWT_SECRET_KEY to a random string in .env

docker-compose up --build
```

| Service | URL |
|---|---|
| Website | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

Seed initial data:

```bash
docker-compose exec backend python seed.py
```

---

### Manual Setup

**Prerequisites:** Python 3.10+, Node.js 18+, MongoDB (local or Atlas)

#### Backend

```bash
cd reliefnet/backend
python -m venv env
.\env\Scripts\activate        # Windows
# source env/bin/activate     # macOS / Linux

pip install -r requirements.txt

# Create .env in reliefnet/backend/ (see .env.example)
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd reliefnet/frontend
npm install
npm run dev
```

Dev server starts at `http://localhost:5173`.

---

## Environment Variables

```env
# Backend
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=reliefnet
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO

# Frontend (Vite build-time)
VITE_API_URL=http://localhost:8000/api/v1
```

---

## License

MIT License
