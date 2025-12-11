"""
Configuration management for ReliefNet backend
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8000
ML_SERVICE_URL = "http://localhost:8001"

# ML Model Paths
NN_VFA_MODEL_PATH = MODELS_DIR / "nn_vfa.pth"
DL_VFA_MODEL_PATH = MODELS_DIR / "dl_vfa.pth"
ARIMA_MODEL_PATH = MODELS_DIR / "arima_model.pkl"
GARCH_MODEL_PATH = MODELS_DIR / "garch_model.pkl"
TRANSFORMER_MODEL_PATH = MODELS_DIR / "transformer_forecaster.pth"

# Data File Paths
DEMAND_HISTORY_PATH = PROCESSED_DATA_DIR / "demand_history.csv"
WAREHOUSES_PATH = PROCESSED_DATA_DIR / "warehouses.csv"
ROAD_NETWORK_PATH = PROCESSED_DATA_DIR / "road_network.json"
FLOOD_RISK_PATH = PROCESSED_DATA_DIR / "flood_risk_scores.csv"
DISTRICT_METADATA_PATH = PROCESSED_DATA_DIR / "district_metadata.csv"
HISTORICAL_DISASTERS_PATH = PROCESSED_DATA_DIR / "historical_disasters.csv"
DELIVERY_PATTERNS_PATH = PROCESSED_DATA_DIR / "delivery_patterns.csv"

# Raw Data Paths
RAW_DISASTER_PATH = RAW_DATA_DIR / "disasterIND.csv"
RAW_WAREHOUSE_PATH = RAW_DATA_DIR / "Warehouse_Data.csv"
RAW_FLOOD_RISK_PATH = RAW_DATA_DIR / "flood_risk_dataset_india.csv"
RAW_FLOODS_INVENTORY_PATH = RAW_DATA_DIR / "India_Floods_Inventory.csv"
RAW_EMERGENCY_ROUTING_PATH = RAW_DATA_DIR / "emergency_service_routing_with_timestamps.csv"
RAW_DELIVERY_LOGISTICS_PATH = RAW_DATA_DIR / "Delivery_Logistics.csv"
RAW_HOSPITAL_PATH = RAW_DATA_DIR / "Hospital_Data.csv"
RAW_DISTRICT_POINTS_PATH = RAW_DATA_DIR / "Ind_adm2_Points.csv"
RAW_TRANSPORT_PATH = RAW_DATA_DIR / "Transport_Data.csv"
RAW_SHELTER_PATH = RAW_DATA_DIR / "Shelter_Data.csv"

# Model Hyperparameters
VFA_CONFIG = {
    "nn_vfa": {
        "input_dim": 20,  # State features
        "hidden_dims": [128, 64, 32],
        "output_dim": 1,  # Value estimate
        "learning_rate": 0.001,
        "batch_size": 64,
    },
    "dl_vfa": {
        "input_dim": 20,
        "hidden_dims": [256, 128, 64, 32],
        "output_dim": 1,
        "learning_rate": 0.0005,
        "batch_size": 128,
        "dropout": 0.2,
    }
}

FORECASTING_CONFIG = {
    "arima": {
        "order": (2, 1, 2),  # (p, d, q)
        "seasonal_order": (1, 1, 1, 7),  # (P, D, Q, s)
    },
    "garch": {
        "p": 1,
        "q": 1,
    },
    "transformer": {
        "d_model": 64,
        "nhead": 4,
        "num_layers": 3,
        "dim_feedforward": 256,
        "dropout": 0.1,
        "seq_length": 30,  # 30 days history
        "pred_length": 7,  # 7 days forecast
    },
    "ensemble": {
        "weights": {
            "arima": 0.3,
            "garch": 0.2,
            "transformer": 0.5,
        }
    }
}

ADP_CONFIG = {
    "discount_factor": 0.95,
    "max_iterations": 100,
    "convergence_threshold": 0.01,
    "deprivation_penalty": 1000,  # High penalty for unmet demand
    "transport_cost_per_km": 50,  # INR per km
}

OPTIMIZATION_CONFIG = {
    "truck_capacity_kg": 5000,
    "uav_capacity_kg": 50,
    "truck_range_km": 500,
    "uav_range_km": 100,
    "truck_speed_kmh": 40,
    "uav_speed_kmh": 60,
    "max_vehicles": 50,
    "time_limit_seconds": 30,  # OR-Tools time limit
}

SHAP_CONFIG = {
    "num_samples": 100,  # Number of samples for SHAP
    "max_features": 10,  # Top features to display
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
