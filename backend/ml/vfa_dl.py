import torch
import torch.nn as nn

class LinearVFA(nn.Module):
    def __init__(self, feature_dim):
        super(LinearVFA, self).__init__()
        self.linear = nn.Linear(feature_dim, 1, bias=True)

    def forward(self, features):
        return self.linear(features)

class LinearVFALearner:
    def __init__(self, feature_dim):
        self.model = LinearVFA(feature_dim)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)
        self.criterion = nn.MSELoss()

    def update(self, features, target):
        self.model.train()
        self.optimizer.zero_grad()
        pred = self.model(features)
        loss = self.criterion(pred, target)
        loss.backward()
        self.optimizer.step()
        return loss.item()
