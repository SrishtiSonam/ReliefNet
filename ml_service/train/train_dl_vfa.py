import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_training_data(n_samples=5000):
    """Generate synthetic training data for VFA"""
    
    # State features
    n_districts = 5
    data = []
    
    for i in range(n_samples):
        # District-level features
        inventories = np.random.uniform(0, 200, n_districts)
        backlogs = np.random.exponential(15, n_districts)
        deprivation_times = np.random.gamma(2, 2, n_districts)
        surge_probs = np.random.beta(1, 9, n_districts)  # Low surge probability
        
        # Aggregate features
        total_inventory = np.sum(inventories)
        total_backlog = np.sum(backlogs)
        max_deprivation = np.max(deprivation_times)
        avg_surge_prob = np.mean(surge_probs)
        
        # Additional features
        inventory_imbalance = np.std(inventories)
        critical_districts = np.sum(backlogs > 20)
        
        features = [
            total_inventory,
            total_backlog,
            max_deprivation,
            avg_surge_prob,
            inventory_imbalance,
            critical_districts,
            np.sum(inventories > 100),  # Well-stocked districts
            np.mean(deprivation_times)
        ]
        
        # Target: future cost (synthetic)
        # Cost increases with backlog, deprivation, and surge probability
        base_cost = total_backlog * 10 + max_deprivation * 50
        surge_penalty = avg_surge_prob * 200
        imbalance_penalty = inventory_imbalance * 5
        
        # Add some noise
        noise = np.random.normal(0, 50)
        target = base_cost + surge_penalty + imbalance_penalty + noise
        target = max(0, target)  # Ensure non-negative
        
        data.append(features + [target])
    
    # Create DataFrame
    feature_names = [
        'total_inventory', 'total_backlog', 'max_deprivation', 'avg_surge_prob',
        'inventory_imbalance', 'critical_districts', 'well_stocked_districts', 'mean_deprivation'
    ]
    
    df = pd.DataFrame(data, columns=feature_names + ['future_cost'])
    return df

def train_dl_vfa():
    """Train DL-VFA (Ridge regression) model"""
    
    logger.info("Generating synthetic training data...")
    df = generate_synthetic_training_data()
    
    # Features and target
    feature_cols = df.columns[:-1].tolist()
    X = df[feature_cols].values
    y = df['future_cost'].values
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    logger.info("Training Ridge regression model...")
    
    # Train Ridge regression (interpretable VFA)
    model = Ridge(alpha=1.0, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)
    
    train_mse = mean_squared_error(y_train, train_pred)
    test_mse = mean_squared_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    logger.info(f"Training MSE: {train_mse:.2f}, R²: {train_r2:.3f}")
    logger.info(f"Test MSE: {test_mse:.2f}, R²: {test_r2:.3f}")
    
    # Feature importance (coefficients)
    feature_importance = dict(zip(feature_cols, model.coef_))
    logger.info("Feature importance:")
    for feature, coef in sorted(feature_importance.items(), key=abs, reverse=True):
        logger.info(f"  {feature}: {coef:.3f}")
    
    # Save model and scaler
    os.makedirs("models", exist_ok=True)
    
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_cols,
        'metrics': {
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
    }
    
    joblib.dump(model_data, 'models/dl_vfa.pkl')
    logger.info("Model saved to models/dl_vfa.pkl")
    
    # Save training data sample
    df.head(100).to_csv('data/processed/training_sample.csv', index=False)
    logger.info("Training data sample saved")
    
    return model_data

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    train_dl_vfa()