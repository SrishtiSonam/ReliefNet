import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import logging
from train_dl_vfa import generate_synthetic_training_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_nn_vfa(epochs=100):
    """Train NN-VFA (MLP) model"""
    
    logger.info("Generating synthetic training data...")
    df = generate_synthetic_training_data(n_samples=8000)  # More data for NN
    
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
    
    logger.info("Training MLP model...")
    
    # Train MLP (small network for local CPU)
    model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        alpha=0.001,
        max_iter=epochs,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10
    )
    
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
    logger.info(f"Final loss: {model.loss_:.4f}")
    
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
            'test_r2': test_r2,
            'final_loss': model.loss_
        }
    }
    
    joblib.dump(model_data, 'models/nn_vfa.pkl')
    logger.info("Model saved to models/nn_vfa.pkl")
    
    return model_data

if __name__ == "__main__":
    import sys
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    train_nn_vfa(epochs=epochs)