"""
Deep Learning Value Function Approximation (DL-VFA)
Deeper network with batch normalization and dropout for better generalization
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import VFA_CONFIG, DL_VFA_MODEL_PATH


class DLVFA(nn.Module):
    """
    Deep Learning Value Function Approximation
    
    Architecture:
    - Input: State features (20 dimensions)
    - Hidden layers: [256, 128, 64, 32] with BatchNorm and Dropout
    - Output: Value estimate (1 dimension)
    """
    
    def __init__(self, input_dim=20, hidden_dims=[256, 128, 64, 32], 
                 output_dim=1, dropout=0.2):
        super(DLVFA, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.dropout = dropout
        
        # Build network with batch norm and dropout
        layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            
            if i < len(hidden_dims) - 1:  # No dropout on last hidden layer
                layers.append(nn.Dropout(dropout))
            
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """He initialization for ReLU networks"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_uniform_(module.weight, nonlinearity='relu')
                nn.init.constant_(module.bias, 0.0)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: State features tensor of shape (batch_size, input_dim)
        
        Returns:
            Value estimates of shape (batch_size, 1)
        """
        return self.network(x)
    
    def predict_value(self, state_features: np.ndarray) -> float:
        """
        Predict value for a single state
        
        Args:
            state_features: Numpy array of shape (input_dim,)
        
        Returns:
            Predicted value (scalar)
        """
        self.eval()
        with torch.no_grad():
            x = torch.FloatTensor(state_features).unsqueeze(0)
            value = self.forward(x).item()
        return value
    
    def save_model(self, path=None):
        """Save model weights"""
        if path is None:
            path = DL_VFA_MODEL_PATH
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'output_dim': self.output_dim,
            'dropout': self.dropout,
        }, path)
        print(f"✓ DL-VFA model saved to {path}")
    
    @classmethod
    def load_model(cls, path=None):
        """Load model weights"""
        if path is None:
            path = DL_VFA_MODEL_PATH
        
        if not Path(path).exists():
            print(f"⚠ Model not found at {path}, creating new model")
            return cls(**VFA_CONFIG['dl_vfa'])
        
        checkpoint = torch.load(path)
        model = cls(
            input_dim=checkpoint['input_dim'],
            hidden_dims=checkpoint['hidden_dims'],
            output_dim=checkpoint['output_dim'],
            dropout=checkpoint.get('dropout', 0.2)
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"✓ DL-VFA model loaded from {path}")
        return model


class DLVFATrainer:
    """Trainer for DL-VFA model with advanced features"""
    
    def __init__(self, model: DLVFA, learning_rate=0.0005):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
        self.criterion = nn.MSELoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5
        )
        self.training_history = []
    
    def train_step(self, state_features: np.ndarray, target_values: np.ndarray) -> float:
        """Single training step"""
        self.model.train()
        
        x = torch.FloatTensor(state_features)
        y = torch.FloatTensor(target_values).unsqueeze(1)
        
        predictions = self.model(x)
        loss = self.criterion(predictions, y)
        
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        
        return loss.item()
    
    def train_epoch(self, states_batch: List[np.ndarray], values_batch: List[float],
                    batch_size=128) -> float:
        """Train for one epoch"""
        states = np.array(states_batch)
        values = np.array(values_batch)
        
        total_loss = 0.0
        num_batches = 0
        
        for i in range(0, len(states), batch_size):
            batch_states = states[i:i+batch_size]
            batch_values = values[i:i+batch_size]
            
            loss = self.train_step(batch_states, batch_values)
            total_loss += loss
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0
        self.training_history.append(avg_loss)
        
        # Update learning rate
        self.scheduler.step(avg_loss)
        
        return avg_loss


def create_pretrained_dl_vfa():
    """Create a pre-trained DL-VFA model"""
    model = DLVFA(
        input_dim=VFA_CONFIG['dl_vfa']['input_dim'],
        hidden_dims=VFA_CONFIG['dl_vfa']['hidden_dims'],
        dropout=VFA_CONFIG['dl_vfa']['dropout']
    )
    
    # Create synthetic training data
    np.random.seed(42)
    num_samples = 2000  # More data for deeper network
    
    states = []
    values = []
    
    for _ in range(num_samples):
        state = np.random.rand(20).astype(np.float32)
        
        # More complex value function
        inventory_score = state[:5].mean()
        demand_score = state[5:9].mean()
        risk_score = state[12:14].mean()
        urgency_score = state[18:20].mean()
        
        value = (inventory_score - demand_score - risk_score + urgency_score * 0.5)
        value = max(0, value)
        
        states.append(state)
        values.append(value)
    
    # Train
    trainer = DLVFATrainer(model, learning_rate=0.0005)
    
    for epoch in range(100):
        loss = trainer.train_epoch(states, values, batch_size=128)
        if epoch % 20 == 0:
            print(f"  Epoch {epoch}: Loss = {loss:.4f}")
    
    model.save_model()
    
    return model


if __name__ == "__main__":
    print("Creating pre-trained DL-VFA model...")
    model = create_pretrained_dl_vfa()
    print("✓ DL-VFA model created and saved")
