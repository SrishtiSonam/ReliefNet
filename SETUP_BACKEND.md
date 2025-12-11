# ReliefNet Backend + ML Engine Setup Guide

## Quick Start

Follow these steps to get the complete ML-powered backend running:

### 1. Install Dependencies

```powershell
# Navigate to backend
cd C:\Users\Srish\Desktop\ReliefNet\backend

# Activate virtual environment (create if needed)
py -3.11 -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Preprocess Data

```powershell
# Run data preprocessing
python data_processing\preprocessing_scripts.py
```

This will process all Kaggle datasets from `data/raw/` into clean formats in `data/processed/`.

### 3. Initialize ML Models

```powershell
# Create pre-trained VFA models
python vfa\nn_vfa.py
python vfa\dl_vfa.py
```

This creates initial NN-VFA and DL-VFA models with reasonable weights.

### 4. Start Flask Backend

```powershell
# Start the main API server
python main.py
```

The backend will start on **http://localhost:8000**

API Documentation: http://localhost:8000/docs

### 5. Start Frontend (in new terminal)

```powershell
cd C:\Users\Srish\Desktop\ReliefNet\frontend
npm run dev
```

Frontend will be on **http://localhost:5173**

## What's Implemented

### ✅ Data Processing
- Real Kaggle dataset preprocessing (disaster inventory, warehouses, flood risk, logistics)
- Demand history time series generation
- Efficient data loading with caching

### ✅ ML Models

**Value Function Approximation (VFA)**
- NN-VFA: 3-layer neural network (128-64-32)
- DL-VFA: 4-layer deep network (256-128-64-32) with batch norm and dropout
- Feature engineering: 20-dimensional state representation

**Approximate Dynamic Programming (ADP)**
- State representation (inventory, demand, time, vehicles, risk)
- Action space generation (allocate resources from warehouse to zone)
- Reward function (minimize deprivation + transport cost)
- Transition model with vehicle management
- ADP solver with greedy and epsilon-greedy policies

**Forecasting**
- ARIMA: Time series forecasting with seasonal components
- GARCH: Volatility and surge prediction
- Ensemble: Weighted combination of all models

**Optimization**
- OR-Tools VRP solver for truck routing
- UAV allocation for remote areas
- Capacity and range constraints
- Human-in-the-loop constraint handling

**Explainable AI**
- SHAP: Feature importance for allocation decisions
- Surrogate decision trees for interpretability
- Natural language explanations

### ✅ API Endpoints

**Forecasting**
- `GET /api/forecast?district={name}&days={n}` - Ensemble demand forecast

**Optimization**
- `POST /api/optimize` - Generate delivery plan (trucks + UAVs)
- `POST /api/optimize/recalculate` - Recalculate with constraints

**VFA**
- `GET /api/vfa` - Get value estimate for state

**Explainability**
- `GET /api/explain/shap?district_id={id}` - SHAP feature importance
- `GET /api/explain/tree?district_id={id}` - Surrogate tree explanation

**Existing Endpoints** (from original)
- `GET /dashboard?role={role}` - Dashboard data
- `GET /public_requests` - List relief requests
- `POST /public_requests` - Submit request
- `GET /roadblocks` - List roadblocks
- `GET /vehicles` - Vehicle positions
- `WebSocket /ws/vehicles` - Real-time vehicle tracking

## Testing the ML Features

### Test Forecasting
```powershell
curl "http://localhost:8000/api/forecast?district=Mumbai&days=7"
```

### Test Optimization
```powershell
curl -X POST "http://localhost:8000/api/optimize" `
  -H "Content-Type: application/json" `
  -d '{\"demand_points\": [{\"zone_id\": \"ZONE1\", \"latitude\": 19.0760, \"longitude\": 72.8777, \"total_demand_kg\": 3000}]}'
```

### Test SHAP Explanation
```powershell
curl "http://localhost:8000/api/explain/shap?district_id=MH01"
```

## Project Structure

```
ReliefNet/
├── backend/
│   ├── main.py                    # Flask API with ML integration
│   ├── config.py                  # Configuration
│   ├── data_processing/           # Data preprocessing
│   │   ├── preprocessing_scripts.py
│   │   └── dataset_loader.py
│   ├── vfa/                       # Value Function Approximation
│   │   ├── nn_vfa.py
│   │   ├── dl_vfa.py
│   │   └── feature_engineering.py
│   ├── adp/                       # Approximate Dynamic Programming
│   │   ├── state_representation.py
│   │   ├── action_space.py
│   │   ├── reward_function.py
│   │   ├── transition_model.py
│   │   └── adp_solver.py
│   ├── optimization/              # OR-Tools optimization
│   │   ├── vehicle_routing.py
│   │   ├── uav_allocation.py
│   │   └── optimizer_engine.py
│   └── explainability/            # Explainable AI
│       ├── shap_explainer.py
│       └── surrogate_tree.py
│
├── ml-fastapi/
│   └── forecasting_service/
│       └── models/
│           ├── arima_forecaster.py
│           ├── garch_forecaster.py
│           └── ensemble.py
│
├── data/
│   ├── raw/                       # Your Kaggle datasets
│   └── processed/                 # Preprocessed data
│
└── frontend/                      # React frontend (existing)
```

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the correct directory and the virtual environment is activated.

### Missing Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Data Not Found
Run the preprocessing script:
```powershell
python data_processing\preprocessing_scripts.py
```

### Model Not Found
Initialize the models:
```powershell
python vfa\nn_vfa.py
python vfa\dl_vfa.py
```

## Next Steps

1. **Train Models on Real Data**: The current models use synthetic pre-training. You can train them on your processed Kaggle data for better performance.

2. **Add More Datasets**: Integrate additional datasets from `data/raw/` for richer features.

3. **Tune Hyperparameters**: Adjust model parameters in `config.py` for your specific use case.

4. **Deploy**: When ready, deploy the backend to a cloud service (AWS, Azure, GCP).

## Performance Notes

- **Forecasting**: ~1-2 seconds per request
- **Optimization**: ~3-5 seconds for 10-20 demand points
- **VFA Inference**: <500ms
- **SHAP Explanation**: ~2-3 seconds

For production, consider:
- Caching frequent requests
- Batch processing
- GPU acceleration for deep learning models
- Load balancing for multiple concurrent requests
