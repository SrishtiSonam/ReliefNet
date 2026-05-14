# reliefnet/ml_services/training_pipeline.py
import pandas as pd
import os
from pathlib import Path

# Use absolute imports from the package root
from .forecasting.xgboost_service import DemandForecaster

def run_training_pipeline(export_dir: str = None, model_dir: str = None):
    """
    Trains all ReliefNet ML models using data exported from the notebook.
    """
    # Default to paths relative to this script's location (reliefnet/ml_services/training_pipeline.py)
    base_dir = Path(__file__).resolve().parents[1] 
    if export_dir is None:
        export_path = base_dir / "data" / "exports"
    else:
        export_path = Path(export_dir).resolve()
        
    if model_dir is None:
        model_path = base_dir / "ml_services" / "models"
    else:
        model_path = Path(model_dir).resolve()
    model_path.mkdir(parents=True, exist_ok=True)

    print(f"Loading training data from {export_path}...")
    
    # 1. Train Demand Forecaster
    districts_file = export_path / "reliefnet_district_features.csv"
    if districts_file.exists():
        df = pd.read_csv(districts_file)
        
        # Prepare target
        df['target_demand'] = df['vulnerability_score'] * 100 + df['population_density'] * 0.1
        df['date'] = '2024-05-12'
        
        forecaster = DemandForecaster()
        print("Training Demand Forecaster (XGBoost)...")
        forecaster.train(df)
        
        # Save model
        save_path = model_path / "demand_forecaster.json"
        forecaster.model.save_model(str(save_path))
        print(f"Model saved to {save_path}")
    else:
        print(f"Could not find {districts_file}. Run generation first.")

    print("ML Training Pipeline Complete.")

if __name__ == "__main__":
    run_training_pipeline()
