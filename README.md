# ReliefNet - Disaster Management Platform with ML

> A disaster management system for India with real-time tracking, AI-powered resource allocation, and demand forecasting

This started as a project to solve the resource allocation problem during disasters in India. After working with 15 different datasets from Kaggle and implementing several ML models, it's turned into something pretty comprehensive.

## Quick Start

If you just want to get this running:

### Backend Setup

```powershell
cd C:\Users\Srish\Desktop\ReliefNet

# Initialize data files
python init_backend.py

# Setup virtual environment
cd backend
py -3.11 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Start server
python main.py
```

Backend will be at `http://localhost:8000` and API docs at `http://localhost:8000/docs`

### Frontend Setup

```powershell
cd C:\Users\Srish\Desktop\ReliefNet\frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## What This Does

The platform has three main interfaces:

1. **State Dashboard** - For state-level disaster management authorities (SDMA)
2. **District Dashboard** - For district-level operations (DDMA)
3. **Public Portal** - For citizens to request relief and find shelters

### The ML Side

I've implemented several ML models here (not just placeholders):

- **ARIMA + GARCH** for demand forecasting with surge detection
- **Temporal Fusion Transformer (TFT)** for multi-horizon predictions with attention mechanisms
- **Value Function Approximation** using neural networks for state evaluation
- **OR-Tools** for vehicle routing optimization
- **SHAP** for explaining why the model makes certain decisions

The TFT model is particularly interesting - it uses attention mechanisms to show which features are driving predictions, making it way more interpretable than standard LSTMs.

## Why I Built This

India faces recurring natural disasters - floods, cyclones, earthquakes. The traditional approach to resource allocation is mostly reactive and manual. I wanted to see if ML could help with:

- Predicting demand surges before they happen
- Optimizing routes for trucks and UAVs
- Explaining allocation decisions to officials
- Coordinating between state, district, and local teams

The core problem is **stochastic dynamic resource allocation** - basically, you don't know what demand will be, roads get blocked, vehicles break down, and you need to minimize both suffering and costs while being able to explain your decisions.

## Data Sources

I'm using 15 real datasets from Kaggle (about 140MB total):

| Dataset | Size | What It's For |
|---------|------|---------------|
| disasterIND.csv | 368 KB | Historical disasters from EM-DAT (1900-2023) |
| Warehouse_Data.csv | 227 KB | Warehouse locations and inventory |
| flood_risk_dataset_india.csv | 1.8 MB | District-level flood risk scores |
| emergency_service_routing_with_timestamps.csv | 87 MB | Emergency vehicle routing data |
| logistics_dataset.csv | 374 KB | Supply chain logistics |
| Delivery_Logistics.csv | 3.7 MB | Delivery routes and times |
| Transport_Data.csv | 216 KB | Vehicle fleet info |
| Hospital_Data.csv | 167 KB | Hospital locations |
| Hospitals In India.csv | 241 KB | Comprehensive hospital database |
| Shelter_Data.csv | 166 KB | Emergency shelter locations |
| India_Floods_Inventory.csv | 236 KB | Flood event inventory |
| Ind_adm2_Points.csv | 44.8 MB | District boundaries |

Plus a few generated time series for filling gaps.

I chose CSV/JSON storage instead of a database to keep setup simple. You can migrate to PostgreSQL later if needed.

## Technical Stack

**Backend:**
- FastAPI (chose this over Flask for speed and auto-docs)
- PyTorch for neural networks
- OR-Tools for optimization
- Statsmodels for ARIMA
- SHAP for explainability

**Frontend:**
- React 18 with Vite
- Leaflet for maps (free, no API keys needed)
- Recharts for visualizations

**Why these choices?**

- FastAPI: 3x faster than Flask, automatic API documentation
- PyTorch: More intuitive than TensorFlow for research-style code
- OR-Tools: Free alternative to Gurobi/CPLEX (which cost thousands)
- Leaflet: Works offline, important for disaster zones

## ML Models Explained

### Forecasting

I'm using an ensemble of three approaches:

**ARIMA (AutoRegressive Integrated Moving Average)**
- Classic time series model
- Good for capturing trends and seasonality
- Order (2,1,2) with seasonal (1,1,1,7) for weekly patterns

**GARCH (Volatility Modeling)**
- Predicts when demand will spike
- Models "surge clustering" - surges tend to follow surges
- Helps with uncertainty quantification

**TFT (Temporal Fusion Transformer)**
- State-of-the-art deep learning
- Uses attention to show which features matter
- Predicts 1-30 days ahead simultaneously
- Provides uncertainty intervals (10th, 50th, 90th percentiles)

The ensemble weights are 30% ARIMA, 20% GARCH, 50% TFT. I found this combination works better than any single model.

### Value Function Approximation (VFA)

This estimates how "good" a particular state is (inventory levels, demand, time, etc).

**NN-VFA**: 3-layer network (128→64→32 neurons)
- Fast, good for real-time decisions
- Uses ReLU activations and Xavier initialization

**DL-VFA**: 4-layer network (256→128→64→32)
- More accurate but slower
- Has batch normalization and dropout for better generalization

The state representation has 20 features covering inventory, demand, time, risk, resources, geography, and urgency.

### Optimization

**Vehicle Routing Problem (VRP)**
- Uses OR-Tools with Guided Local Search
- Capacity: 5000 kg per truck
- 30 second time limit for solutions

**UAV Allocation**
- Priority scoring based on accessibility and urgency
- Capacity: 50 kg per UAV
- Range: 100 km

### Explainability

**SHAP (SHapley Additive exPlanations)**
- Shows which features influenced each decision
- Model-agnostic, works with any ML model
- Generates natural language explanations

**Surrogate Decision Trees**
- Approximates the neural network with an interpretable tree
- Max depth 5 for readability
- Helps officials understand the logic

## API Endpoints

The main endpoints are:

**Forecasting:**
```
GET /api/forecast?district=Mumbai&days=7
```

**Optimization:**
```
POST /api/optimize
{
  "demand_points": [
    {
      "zone_id": "ZONE1",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "total_demand_kg": 3000,
      "accessibility": 0.8,
      "urgency": 0.7
    }
  ]
}
```

**Explainability:**
```
GET /api/explain/shap?district_id=MH01
GET /api/explain/tree?district_id=MH01
```

**TFT Predictions:**
```
GET /api/tft/predict?district=Mumbai&horizon=30
GET /api/tft/attention?district=Mumbai
```

Full API docs are at `http://localhost:8000/docs` when running.

## Frontend Features

### State Dashboard
- Interactive map with district boundaries
- Real-time vehicle tracking
- 7-day demand forecasts with confidence intervals
- TFT predictions with attention heatmaps
- Resource allocation interface
- Warehouse stock management
- SHAP explanations for decisions

### District Dashboard
- Local map with warehouses and roadblocks
- Public request viewer
- Roadblock reporting
- Local inventory tracking
- Mission planning

### Public Portal
- Shelter locator
- Relief request submission
- Request status tracking
- Safety guidelines
- Emergency contacts

### Interactive ML Playground

There's an educational page (`/how-ai-works`) with 8 sliders where you can experiment with different scenarios:

1. Rainfall (0-100mm)
2. Demand (1000-10000kg)
3. Stock (2000-15000kg)
4. Trucks Available (1-10)
5. Population Density (1000-15000)
6. Road Accessibility (0-100%)
7. Distance to Warehouse (10-200km)
8. Deprivation Time (0-72 hours)

It shows real-time ML predictions and explains how each feature impacts the decision. Pretty useful for understanding what the models are doing.

## Project Structure

```
ReliefNet/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── config.py                  # Configuration
│   ├── vfa/                       # Value function approximation
│   ├── adp/                       # Dynamic programming
│   ├── optimization/              # OR-Tools routing
│   ├── explainability/            # SHAP and trees
│   ├── ml_models/                 # TFT and forecasting
│   └── data_processing/           # Data loaders
│
├── data/
│   ├── raw/                       # 15 Kaggle datasets
│   └── processed/                 # Cleaned CSVs
│
├── frontend/                      # React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
└── docs/                          # Documentation
```

## Configuration

You can tweak settings in `backend/config.py`:

**VFA Settings:**
```python
VFA_CONFIG = {
    "nn_vfa": {
        "input_dim": 20,
        "hidden_dims": [128, 64, 32],
        "learning_rate": 0.001,
    },
    "dl_vfa": {
        "hidden_dims": [256, 128, 64, 32],
        "dropout": 0.2,
    }
}
```

**Forecasting:**
```python
FORECASTING_CONFIG = {
    "arima": {
        "order": (2, 1, 2),
        "seasonal_order": (1, 1, 1, 7),
    },
    "ensemble": {
        "weights": {"arima": 0.3, "garch": 0.2, "transformer": 0.5}
    }
}
```

**Optimization:**
```python
OPTIMIZATION_CONFIG = {
    "truck_capacity_kg": 5000,
    "uav_capacity_kg": 50,
    "time_limit_seconds": 30,
}
```

## Testing

### Quick API Tests

```powershell
# Test forecasting
curl "http://localhost:8000/api/forecast?district=Mumbai&days=7"

# Test optimization
curl -X POST "http://localhost:8000/api/optimize" -H "Content-Type: application/json" -d '{\"demand_points\": [{\"zone_id\": \"ZONE1\", \"latitude\": 19.0760, \"longitude\": 72.8777, \"total_demand_kg\": 3000, \"accessibility\": 0.8, \"urgency\": 0.7}]}'

# Test SHAP
curl "http://localhost:8000/api/explain/shap?district_id=MH01"
```

### Frontend Testing

1. Go to `http://localhost:5173`
2. Try the State Dashboard
3. Click on a district
4. Test "View Surge Forecast" - should show charts
5. Test "Optimize Allocation" - should show routes
6. Test "Explain Decision" - should show SHAP features

## Troubleshooting

**Import errors?**
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Data files missing?**
```powershell
python init_backend.py
```

**Port 8000 already in use?**
Change the port in `backend/main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

**Frontend not connecting?**
Check that backend is running on port 8000 and CORS is enabled in `main.py`.

## Performance

Typical response times:

- Forecasting: 1-2 seconds
- Optimization: 3-5 seconds
- VFA inference: <500ms
- SHAP explanation: 2-3 seconds
- Data loading: <100ms (with caching)

The LRU cache makes a huge difference - the 87MB routing file loads once and then subsequent calls are instant.

## What's Next

**Short term:**
- Train on real data (currently using sample data)
- Tune hyperparameters in config.py
- Add more features to state representation
- Custom constraints for optimization

**Long term:**
- Migrate to PostgreSQL with PostGIS
- Add authentication (JWT with RBAC)
- Real-time GPS integration
- Cloud deployment (Docker + AWS/Azure)
- Monitoring with Prometheus/Grafana

## Additional Documentation

- **ML Technical Guide**: `ml.md` - Deep dive into all ML models (2160 lines)
- **Setup Guide**: `SETUP_BACKEND.md` - Detailed setup instructions
- **Quick Reference**: `QUICK_REFERENCE.md` - API quick reference

## Tech Stack Summary

**Languages**: Python 3.11, JavaScript (React)
**ML**: PyTorch, Statsmodels, SHAP, OR-Tools, PyTorch Forecasting
**Backend**: FastAPI, Pandas, NumPy
**Frontend**: React 18, Vite, Leaflet, Recharts
**Data**: 15 Kaggle datasets (~140 MB, 500k+ records)

**Models**: 7 total (NN-VFA, DL-VFA, ARIMA, GARCH, TFT, SHAP, Surrogate Trees)
**Code**: 30+ files, ~5000 lines
**Documentation**: 2000+ lines across multiple files

---

Built for disaster resilience in India. The goal was to combine classical ML (ARIMA/GARCH) with modern deep learning (TFT) and optimization (OR-Tools) into something actually useful for disaster response.

For detailed ML implementation, check out `ml.md` which covers VFA, ADP, TFT, forecasting, optimization, and explainability in depth.
