"""
Neural Network Value Function Approximation (NN-VFA)
3-layer MLP for state value estimation
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import VFA_CONFIG, NN_VFA_MODEL_PATH


class NNVFA(nn.Module):
    """
    Neural Network Value Function Approximation
    
    Architecture:
    - Input: State features (20 dimensions)
    - Hidden layers: [128, 64, 32]
    - Output: Value estimate (1 dimension)
    """
    
    def __init__(self, input_dim=20, hidden_dims=[128, 64, 32], output_dim=1):
        super(NNVFA, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        
        # Build network layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Xavier initialization for better convergence"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
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
            path = NN_VFA_MODEL_PATH
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'output_dim': self.output_dim,
        }, path)
        print(f"✓ NN-VFA model saved to {path}")
    
    @classmethod
    def load_model(cls, path=None):
        """Load model weights"""
        if path is None:
            path = NN_VFA_MODEL_PATH
        
        if not Path(path).exists():
            print(f"⚠ Model not found at {path}, creating new model")
            return cls(**VFA_CONFIG['nn_vfa'])
        
        checkpoint = torch.load(path)
        model = cls(
            input_dim=checkpoint['input_dim'],
            hidden_dims=checkpoint['hidden_dims'],
            output_dim=checkpoint['output_dim']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"✓ NN-VFA model loaded from {path}")
        return model


class NNVFATrainer:
    """Trainer for NN-VFA model"""
    
    def __init__(self, model: NNVFA, learning_rate=0.001):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        self.training_history = []
    
    def train_step(self, state_features: np.ndarray, target_values: np.ndarray) -> float:
        """
        Single training step
        
        Args:
            state_features: Batch of state features (batch_size, input_dim)
            target_values: Target values (batch_size, 1)
        
        Returns:
            Loss value
        """
        self.model.train()
        
        # Convert to tensors
        x = torch.FloatTensor(state_features)
        y = torch.FloatTensor(target_values).unsqueeze(1)
        
        # Forward pass
        predictions = self.model(x)
        loss = self.criterion(predictions, y)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def train_epoch(self, states_batch: List[np.ndarray], values_batch: List[float],
                    batch_size=64) -> float:
        """
        Train for one epoch
        
        Args:
            states_batch: List of state feature arrays
            values_batch: List of target values
            batch_size: Batch size for training
        
        Returns:
            Average loss for the epoch
        """
        states = np.array(states_batch)
        values = np.array(values_batch)
        
        total_loss = 0.0
        num_batches = 0
        
        # Mini-batch training
        for i in range(0, len(states), batch_size):
            batch_states = states[i:i+batch_size]
            batch_values = values[i:i+batch_size]
            
            loss = self.train_step(batch_states, batch_values)
            total_loss += loss
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0
        self.training_history.append(avg_loss)
        
        return avg_loss


def create_pretrained_nn_vfa():
    """
    Create a pre-trained NN-VFA model with reasonable initial weights
    This is used when no training data is available yet
    """
    model = NNVFA(
        input_dim=VFA_CONFIG['nn_vfa']['input_dim'],
        hidden_dims=VFA_CONFIG['nn_vfa']['hidden_dims']
    )
    
    # Create some synthetic training data for initialization
    np.random.seed(42)
    num_samples = 1000
    
    states = []
    values = []
    
    for _ in range(num_samples):
        # Random state features
        state = np.random.rand(20).astype(np.float32)
        
        # Synthetic value based on simple heuristic
        # Higher inventory + lower demand + lower risk = higher value
        inventory_score = state[:5].mean()
        demand_score = state[5:9].mean()
        risk_score = state[12:14].mean()
        
        value = inventory_score - demand_score - risk_score
        value = max(0, value)  # Ensure non-negative
        
        states.append(state)
        values.append(value)
    
    # Train for a few epochs
    trainer = NNVFATrainer(model, learning_rate=0.001)
    
    for epoch in range(50):
        loss = trainer.train_epoch(states, values, batch_size=64)
        if epoch % 10 == 0:
            print(f"  Epoch {epoch}: Loss = {loss:.4f}")
    
    # Save model
    model.save_model()
    
    return model


if __name__ == "__main__":
    print("Creating pre-trained NN-VFA model...")
    model = create_pretrained_nn_vfa()
    print("✓ NN-VFA model created and saved")
