import numpy as np
import torch
from backend.ml.vfa_nn import VFALearner

class ADPTrainer:
    def __init__(self, state_dim=10):
        self.vfa = VFALearner(state_dim)
        self.gamma = 0.95

    def train_episode(self, trajectory):
        """
        trajectory: list of (state, reward, next_state)
        """
        total_loss = 0
        for state, reward, next_state in reversed(trajectory):
            # Convert to tensors
            s = torch.FloatTensor(state).unsqueeze(0)
            ns = torch.FloatTensor(next_state).unsqueeze(0)
            r = torch.FloatTensor([reward]).unsqueeze(0)

            # Bellman update target
            next_val = self.vfa.estimate_value(ns)
            target = r + self.gamma * next_val
            target_tensor = torch.FloatTensor([target]).unsqueeze(0)

            loss = self.vfa.update(s, target_tensor)
            total_loss += loss
        return total_loss / len(trajectory)
