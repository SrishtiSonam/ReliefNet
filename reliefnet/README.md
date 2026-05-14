# 🌐 ReliefNet — AI-Powered Disaster Management Platform

ReliefNet is a production-grade, full-stack AI platform designed to optimize post-disaster logistics and resource allocation. It leverages geospatial data, reinforcement learning, constrained optimization, and graph theory to ensure that relief materials reach the most vulnerable populations via the safest routes, while maximizing fairness.

---

## ✨ Key Features

-   **🤖 Reinforcement Learning (MAPPO & PPO)**: Advanced agents that learn to dispatch trucks and UAVs dynamically over multi-period simulations.
-   **⚖️ Constrained Fairness Optimization**: Integrates Gini coefficients and max-min fairness into a PuLP MILP solver to ensure remote districts are not neglected.
-   **🗺️ Risk-Aware GIS Routing & Dynamic Road Collapse**: Intelligent pathfinding that automatically redirects deliveries as flood severity probabilistically collapses infrastructure in real-time.
-   **🛸 Multi-Modal Logistics**: Seamlessly coordinates between **Trucks** and **UAVs (Drones)** for "Last-Mile" delivery in isolated zones.
-   **🌍 Interactive Public Portal**: A citizen-facing gateway for reporting emergencies, submitting critical resource requests, and viewing active shelter maps.
-   **🚨 Responder Triage Dashboard**: A centralized command feed for monitoring, dispatching, and resolving live citizen requests in real-time.
-   **🏗️ Dynamic Infrastructure Constraints**: Stress-test supply chains by manually simulating localized hub destruction (`excluded_warehouses`) and capping active warehouse networks.
-   **🧑‍💻 Human-in-the-Loop (HITL)**: Operators can override AI decisions via a custom dashboard, instantly triggering re-optimization under manual constraints.
-   **⚙️ Platform Administration**: Dedicated Settings module for configuring AI behavior, UI appearance, and backend MongoDB synchronization.
-   **🔍 Explainable AI (XAI)**: Transparent reasoning for every allocation decision using SHAP values and heuristic text generation.

---

## 🏗️ Technology Stack

-   **Backend**: FastAPI, MongoDB (Motor), Pydantic, JWT Auth.
-   **Frontend**: React, Vite, Tailwind CSS, Zustand, Framer Motion, Recharts.
-   **GIS**: Leaflet, React-Leaflet, OpenStreetMap.
-   **AI/ML**: Stable-Baselines3 (PPO), Gymnasium, PuLP, Shap, NetworkX, XGBoost, PyTorch.

---

## 📂 Project Structure

```text
reliefnet/
├── backend/            # FastAPI Application (HITL Endpoints)
├── frontend/           # React + Vite Application (RL & Override Dashboards)
├── ml_services/        # AI/ML Models & Environments
│   ├── environments/   # Custom Gymnasium Disaster Env
│   ├── rl_agents/      # PPO and MAPPO Architectures
│   ├── optimization/   # PuLP Logistics Optimizer
│   ├── simulation/     # Stochastic Disaster Engine
│   ├── fairness/       # Gini & Max-Min Fairness Metrics
│   ├── explainability/ # SHAP and Attention Visualization
│   └── forecasting/    # XGBoost Demand Prediction
├── data/
│   └── exports/        # Processed CSVs for ML Training
└── reliefnet_notebook.ipynb
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB instance (Local or Atlas)

### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
pip install gymnasium stable-baselines3 pulp shap networkx torch
uvicorn app.main:app --reload
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Run AI Training
Ensure you have run the Jupyter Notebook first to generate the data exports.
```bash
python -m ml_services.training_pipeline
```

---

## 🧪 Simulation Flow

1.  **Configure**: Input disaster type, epicenter coordinates, and severity.
2.  **Simulate**: The `DisasterSimulator` propagates floods and calculates dynamic road failures over time.
3.  **Optimize**: Trigger the RL Agent or PuLP Optimizer to match shortages with warehouse stock via the safest AI-calculated routes, adhering to strict fairness constraints.
4.  **Review (HITL)**: Human operators review the transparent AI reasoning, apply overrides if necessary, and re-optimize.
5.  **Execute**: View the final dispatch plan with delivery modes (Truck/UAV) on the live dashboard.

---

## 🛡️ License
This project is licensed under the MIT License.
