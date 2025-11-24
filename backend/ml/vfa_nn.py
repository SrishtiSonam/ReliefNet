import torch
import torch.nn as nn

class ValueFunctionNN(nn.Module):
    def __init__(self, state_dim, hidden_dim=64):
        super(ValueFunctionNN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1) # Outputs Value V(s)
        )

    def forward(self, state):
        return self.net(state)

class VFALearner:
    def __init__(self, state_dim):
        self.model = ValueFunctionNN(state_dim)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.MSELoss()

    def update(self, state, target_value):
        self.model.train()
        self.optimizer.zero_grad()
        pred = self.model(state)
        loss = self.criterion(pred, target_value)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def estimate_value(self, state):
        self.model.eval()
        with torch.no_grad():
            return self.model(state).item()
