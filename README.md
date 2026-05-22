# 🌍 ReliefNet — Unified AI Disaster Intelligence & Humanitarian Logistics Platform

> Production-grade AI platform combining stochastic resource allocation, reinforcement learning, real-time human coordination, and offline-first mobile capabilities for disaster response.

ReliefNet merges reinforcement learning, constrained optimization, surge-aware forecasting, GIS-based routing, and explainable human-in-the-loop coordination into a resilient disaster response framework capable of operating under infrastructure collapse, uncertain demand, and rapidly evolving emergencies — including in field conditions with no internet connectivity.

---

## ✨ Dual Methodology Architecture

### Method 1 — AI-Based Stochastic Dynamic Resource Allocation
Focuses on intelligent allocation and routing of disaster relief resources using:
- Approximate Dynamic Programming
- Reinforcement Learning (PPO & MAPPO)
- Mixed Integer Linear Programming (MILP)
- Multi-Agent Coordination
- Truck + UAV Hybrid Logistics

**Core objectives:**
- Minimize deprivation cost
- Optimize allocation fairness
- Adapt to dynamic road failures
- Coordinate heterogeneous fleets
- Reduce delivery latency

### Method 2 — Integrated Disaster Awareness & Human Coordination Platform
Focuses on operational transparency, collaboration, and public engagement through:
- Citizen emergency portals
- Live responder dashboards
- Human-in-the-loop AI overrides
- Explainable AI reasoning
- Public shelter and alert systems
- Infrastructure monitoring
- **Offline-first mobile app for field responders**

---

## 🚀 8-Phase Unified Workflow

| Phase | Name | What Happens |
|---|---|---|
| 1 | Multi-Source Disaster Intelligence | Gathers GIS, population, warehouse, weather, and live citizen data |
| 2 | Surge-Aware Demand Forecasting | ARIMA, GARCH, Transformer, XGBoost predict demand spikes |
| 3 | Infrastructure & Risk Simulation | Models flood propagation, road collapse, connectivity failure |
| 4 | RL-Based Multi-Agent Decision Engine | PPO/MAPPO agents dispatch trucks, UAVs, and inventory |
| 5 | Fairness-Constrained Optimization | PuLP MILP ensures equitable distribution, Gini minimization |
| 6 | GIS-Based Adaptive Routing | NetworkX + hazard scores compute safe truck/UAV routes |
| 7 | Explainable AI & HITL Coordination | SHAP explanations + human override workflows |
| 8 | Public & Authority Portals | Central, state, and citizen dashboards + field responder mobile app |

---

## 📱 Offline-First Mobile App for Field Responders

Field responders operate in the most infrastructure-deprived environments — no internet, no cell signal, unreliable GPS. The ReliefNet mobile app is built offline-first: every critical workflow functions without a network connection and syncs automatically when connectivity is restored.

### Core Principles

- **Offline by default** — all core screens render from local storage; network is an enhancement, not a requirement
- **Conflict-aware sync** — last-write-wins with server-authoritative conflict resolution and manual override prompts
- **Minimal data footprint** — pre-cached district maps, assignment data, and supply manifests are compressed and bounded in size
- **Battery-conscious** — sync intervals back off exponentially; background work is deferred when battery is below 20%

### Key Screens & Workflows

| Screen | Offline Capable | Description |
|---|---|---|
| Assignment Dashboard | ✅ | Current vehicle assignments, delivery targets, priority scores |
| GIS Route Map | ✅ | Pre-cached OpenStreetMap tiles for assigned districts |
| Supply Manifest | ✅ | Inventory loaded, delivered, and remaining per vehicle |
| Emergency Requests | ✅ | Queued citizen requests with severity and location |
| Delivery Confirmation | ✅ | Mark deliveries complete; syncs to server on reconnect |
| HITL Override | ⚠️ Partial | Log override intent offline; submission requires connectivity |
| Live Vehicle Tracking | ❌ | Requires WebSocket; shows last-known position when offline |

### Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | React Native (Expo) | Cross-platform iOS + Android |
| Local DB | WatermelonDB | High-performance offline SQLite with sync |
| Sync Engine | WatermelonDB Sync Protocol | Delta sync with conflict resolution |
| Map Tiles | react-native-maps + MapLibre | Offline tile caching per district |
| State | Zustand | Shared app state |
| Background Sync | Expo BackgroundFetch | Periodic sync when app is backgrounded |
| Push Notifications | Expo Notifications | Assignment and alert delivery |
| Auth | JWT (same as backend) | Token stored in SecureStore |
| Connectivity Detection | NetInfo | Switches online/offline mode automatically |

### Offline Data Architecture

```text
On Login / Shift Start:
  ↓ Download & cache to WatermelonDB
  - Active assignments for this responder
  - Supply manifest for assigned vehicle
  - Citizen emergency requests (district-filtered)
  - Map tiles for assigned districts (bounded radius)
  - Shelter locations and alert templates

During Field Operation (no network):
  - Read / write entirely from local WatermelonDB
  - All mutations queued in local change log
  - Timestamps and responder ID stamped locally

On Reconnect:
  - WatermelonDB sync runs delta push + pull
  - Server resolves conflicts (last-write-wins by default)
  - Responder notified of any overwritten local changes
  - New assignments and updated routes pulled immediately
```

### Sync Flow

```text
App detects connectivity (NetInfo)
   ↓
WatermelonDB Sync → POST /sync/push   (local changes → server)
                  ← GET  /sync/pull   (server changes → local)
   ↓
Conflict resolution:
  - Non-conflicting: merged silently
  - Conflicting: server wins + UI toast shown to responder
   ↓
Background sync scheduled (Expo BackgroundFetch, 5-min intervals)
   ↓
Exponential backoff if sync fails (1m → 2m → 4m → max 30m)
```

### Offline Map Caching

Pre-cached OpenStreetMap tiles are downloaded at login scoped to the responder's assigned district(s). The tile cache is bounded at 200 MB per device. MapLibre renders fully offline from the local tile store. Hazard overlays (flood zones, blocked roads) are stored as GeoJSON alongside tiles and refreshed on sync.

```text
At shift start:
  → Fetch district GeoJSON bounding box
  → Download tiles for zoom levels 10–16
  → Store in MapLibre offline tile cache
  → Download hazard overlays as GeoJSON
  → Ready for offline navigation
```

### Project Structure (Mobile)

```text
reliefnet/
└── mobile/
    ├── app/
    │   ├── screens/
    │   │   ├── AssignmentDashboard/
    │   │   ├── RouteMap/
    │   │   ├── SupplyManifest/
    │   │   ├── EmergencyRequests/
    │   │   ├── DeliveryConfirmation/
    │   │   └── HITLOverride/
    │   ├── components/
    │   │   ├── OfflineBanner/         ← shows when offline
    │   │   ├── SyncStatusIndicator/
    │   │   └── HazardOverlay/
    │   ├── db/
    │   │   ├── schema.js              ← WatermelonDB schema
    │   │   ├── models/                ← Assignment, Request, Delivery
    │   │   └── sync.js                ← push/pull sync logic
    │   ├── store/
    │   │   └── useAppStore.js         ← Zustand global state
    │   ├── hooks/
    │   │   ├── useConnectivity.js     ← NetInfo wrapper
    │   │   └── useSync.js             ← manual + auto sync
    │   ├── maps/
    │   │   ├── OfflineTileManager.js  ← tile download + cache mgmt
    │   │   └── HazardLayer.js         ← GeoJSON overlay renderer
    │   └── notifications/
    │       └── push.js                ← Expo Notifications setup
    ├── app.config.js
    ├── package.json
    └── README.md
```

### Backend Sync API (FastAPI additions)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/sync/push` | Receive batched local mutations from device |
| GET | `/sync/pull` | Return delta of server changes since last sync timestamp |
| GET | `/sync/tiles/:district` | Stream pre-tiled GeoJSON for offline map caching |
| GET | `/sync/manifest/:vehicleId` | Download supply manifest for offline use |

### Installation & Setup (Mobile)

#### Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g expo`
- Android Studio or Xcode for device emulation

```bash
cd mobile
npm install
expo start
```

For device testing:
```bash
expo run:android   # or
expo run:ios
```

### Environment Variables (Mobile)

```env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_WS_URL=ws://localhost:8000/ws
EXPO_PUBLIC_TILE_CACHE_MB=200
EXPO_PUBLIC_SYNC_INTERVAL_SEC=300
```

---

## 🤖 AI & ML Stack

| Component | Technology | Purpose |
|---|---|---|
| RL Agent (Single) | PPO via Stable-Baselines3 | Single-vehicle dispatching |
| RL Agent (Multi) | MAPPO via Stable-Baselines3 | Multi-agent fleet coordination |
| Optimization | PuLP MILP Solver | Fairness-constrained resource allocation |
| Demand Forecasting | ARIMA, GARCH, XGBoost, Transformers | Surge prediction |
| Explainability | SHAP | Allocation transparency |
| Infrastructure | Gymnasium | RL environment simulation |
| Deep Learning | PyTorch | Neural value function approximation |
| GIS Routing | NetworkX | Road network graph algorithms |

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** — high-performance async REST API
- **MongoDB** — flexible document store for disaster events and logistics data
- **Motor** — async MongoDB driver for FastAPI
- **Pydantic** — data validation and schema enforcement
- **JWT Authentication** — stateless auth for responders and authorities

### Frontend
- **React** — component-based UI
- **Vite** — fast dev and build tooling
- **Tailwind CSS** — utility-first styling
- **Zustand** — lightweight global state
- **Framer Motion** — animations and dashboard transitions
- **Recharts** — analytics charts and forecast visualizations

### Mobile (Field Responders)
- **React Native (Expo)** — cross-platform iOS + Android
- **WatermelonDB** — offline-first local database with sync
- **MapLibre + react-native-maps** — offline tile rendering
- **Expo BackgroundFetch** — background sync scheduling
- **NetInfo** — connectivity detection

### GIS & Visualization
- **Leaflet + React-Leaflet** — interactive disaster maps (web)
- **MapLibre** — offline tile rendering (mobile)
- **OpenStreetMap** — base map tile layer
- **NetworkX** — road network graph and routing algorithms

### Deployment
- **Docker** — containerized services
- **Kubernetes** — orchestration and horizontal scaling
- **CI/CD Pipelines** — automated build and deploy

---

## 📂 Project Structure

```text
reliefnet/
├── backend/
│   ├── api/
│   │   ├── disasters/
│   │   ├── vehicles/
│   │   ├── warehouses/
│   │   ├── routing/
│   │   ├── alerts/
│   │   └── sync/                      ← NEW: mobile sync endpoints
│   ├── auth/
│   ├── hitl/
│   ├── simulation/
│   ├── websocket/
│   └── main.py
│
├── frontend/
│   ├── dashboards/
│   │   ├── CentralAuthorityDashboard/
│   │   ├── StateAuthorityDashboard/
│   │   └── ResponderDashboard/
│   ├── citizen_portal/
│   ├── authority_portal/
│   ├── maps/
│   └── analytics/
│
├── mobile/                            ← NEW: offline-first field app
│   ├── app/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── db/
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── maps/
│   │   └── notifications/
│   ├── app.config.js
│   └── package.json
│
├── ml_services/
│   ├── environments/
│   ├── rl_agents/
│   ├── optimization/
│   ├── forecasting/
│   ├── routing/
│   ├── simulation/
│   └── explainability/
│
├── gis/
├── datasets/
├── notebooks/
├── deployment/
│   ├── Dockerfile
│   ├── kubernetes/
│   └── nginx/
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 🗄️ Key Data Models (MongoDB)

```python
# Disaster Event
{
  "_id": ObjectId,
  "type": "flood | earthquake | cyclone",
  "severity": 1-5,
  "epicenter": { "lat": float, "lng": float },
  "affected_districts": [str],
  "started_at": datetime,
  "status": "active | contained | resolved"
}

# Vehicle
{
  "_id": ObjectId,
  "type": "truck | uav",
  "capacity": float,
  "current_location": { "lat": float, "lng": float },
  "status": "idle | dispatched | en_route | delivered",
  "assigned_warehouse": str,
  "payload": [{ "item": str, "quantity": int }]
}

# Warehouse
{
  "_id": ObjectId,
  "location": { "lat": float, "lng": float },
  "district": str,
  "inventory": [{ "item": str, "quantity": int }],
  "accessibility_score": float,
  "is_operational": bool
}

# Citizen Emergency Request
{
  "_id": ObjectId,
  "reporter_id": str,
  "location": { "lat": float, "lng": float },
  "needs": ["food", "water", "medical", "rescue"],
  "severity": "low | medium | critical",
  "status": "pending | assigned | resolved",
  "submitted_at": datetime
}

# Mobile Sync Record (NEW)
{
  "_id": ObjectId,
  "responder_id": str,
  "device_id": str,
  "last_pulled_at": datetime,
  "last_pushed_at": datetime,
  "pending_mutations": int,
  "sync_status": "synced | pending | conflict"
}
```

---

## 🔐 Authentication Flow (JWT)

```text
Responder / Authority / Citizen registers
   ↓
POST /auth/login → { username, password }
   ↓
Password verified → JWT issued (access + refresh)
   ↓
All API requests: Authorization: Bearer <token>
   ↓
Role-based access: CITIZEN | RESPONDER | STATE_AUTHORITY | CENTRAL_AUTHORITY
```

**Mobile:** JWT stored in Expo SecureStore. Refresh tokens used to maintain sessions across shifts without re-login.

**Roles & Access:**

| Role | Access |
|---|---|
| CITIZEN | Emergency requests, shelter maps, alerts |
| RESPONDER | Vehicle tracking, delivery updates, HITL overrides, **mobile field app** |
| STATE_AUTHORITY | Roadblock reporting, district coordination |
| CENTRAL_AUTHORITY | Full dashboard, AI plans, analytics, audit |

---

## 🧪 End-to-End Simulation Flow

```text
Step 1: Configure Disaster
        → type, severity, epicenter, weather

Step 2: Predict Demand Surge
        → ARIMA/GARCH/XGBoost forecast demand by district

Step 3: Simulate Infrastructure Failure
        → road collapse probability, connectivity loss, accessibility scores

Step 4: AI Allocation Planning
        → PPO/MAPPO agents dispatch trucks + UAVs
        → PuLP MILP optimizes fairness constraints

Step 5: Human Review (HITL)
        → Operator inspects SHAP explanations
        → Modifies constraints, excludes warehouses, re-prioritizes
        → Approves or rejects AI plan

Step 6: Execute Logistics
        → Routes dispatched, live tracking via WebSocket
        → UAVs handle inaccessible last-mile delivery
        → Field responders receive assignments on mobile app
        → Deliveries confirmed via mobile even when offline
        → Audit log updated in real time on sync
```

---

## 🌐 Portal Overview

### Central Authority Dashboard
- Live vehicle and UAV tracking on GIS map
- AI allocation monitoring with SHAP explanations
- Forecast visualization (demand surge charts)
- Warehouse inventory analytics
- Full simulation control panel

### State Authority Dashboard
- District-level resource overview
- Roadblock and connectivity reporting
- Relief request management
- Coordination with central authority

### Citizen Portal
- Submit emergency requests with location
- View nearest shelters on map
- Receive real-time alerts and safety guidelines
- Track request status

### Field Responder Mobile App *(NEW)*
- Offline-first assignment and delivery management
- Pre-cached district maps with hazard overlays
- Supply manifest tracking
- Citizen emergency request queue
- Background sync with conflict resolution

---

## 🤖 Key Innovations

**AI + Optimization Hybrid** — RL agents plan, MILP optimizes, humans approve.

**Dynamic Truck-UAV Collaboration** — trucks for bulk transport, UAVs for inaccessible last-mile delivery.

**Fairness-Aware Allocation** — Max-Min fairness and Gini minimization ensure remote districts are never neglected.

**Explainable AI** — SHAP values provide transparent reasoning for every allocation decision.

**Human-in-the-Loop** — Operators can override, constrain, and re-trigger AI at any phase.

**Real-Time Infrastructure Failure Simulation** — continuously adapts to evolving road and warehouse conditions.

**Offline-First Field Operations** — field responders operate fully offline; delta sync restores shared state on reconnect.

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB
- Docker (optional)
- Expo CLI (mobile): `npm install -g expo`

### Backend

```bash
cd backend
python -m venv env
source env/bin/activate        # Windows: .\env\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### ML Services

```bash
cd ml_services
pip install -r requirements.txt
python rl_agents/PPO/train.py      # Train PPO agent
python rl_agents/MAPPO/train.py    # Train MAPPO agents
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Mobile (Field Responder App)

```bash
cd mobile
npm install
expo start
```

### Docker (All Services)

```bash
docker-compose up --build
```

---

## 🔑 Environment Variables

```env
# Backend
MONGO_URI=mongodb://localhost:27017/reliefnet
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# ML Services
RL_MODEL_PATH=./ml_services/rl_agents/
OPTIMIZATION_TIMEOUT=300

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Mobile
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_WS_URL=ws://localhost:8000/ws
EXPO_PUBLIC_TILE_CACHE_MB=200
EXPO_PUBLIC_SYNC_INTERVAL_SEC=300

# Deployment
PROMETHEUS_ENABLED=True
```

---

## 📦 Requirements

```text
# Backend
fastapi
uvicorn
motor
pymongo
pydantic
python-jose[cryptography]

# ML Services
stable-baselines3
gymnasium
pulp
shap
xgboost
torch
networkx
numpy
pandas
scikit-learn

# Mobile
react-native / expo
@nozbe/watermelondb
react-native-maps
maplibre-react-native
@react-native-community/netinfo
expo-background-fetch
expo-notifications
expo-secure-store
zustand
```

---

## 🌍 Research Foundation

Based on academic research:
**"Stochastic Dynamic Post-Disaster Inventory Allocation Using Trucks and UAVs with Integrated Awareness Platform"**

Extended with:
- MAPPO multi-agent reinforcement learning
- Neural value function approximation
- Fairness-constrained MILP
- SHAP explainability layer
- Real-time citizen coordination portals
- Offline-first mobile field operations

---

## 🛡️ License

MIT License
