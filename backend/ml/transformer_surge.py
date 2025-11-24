import torch
import torch.nn as nn
import numpy as np

class SurgeTransformer(nn.Module):
    def __init__(self, input_dim=1, d_model=64, nhead=4, num_layers=2, output_dim=1):
        super(SurgeTransformer, self).__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, 100, d_model)) # Max seq len 100
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.decoder = nn.Linear(d_model, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        seq_len = x.size(1)
        x = self.embedding(x) + self.pos_encoder[:, :seq_len, :]
        x = self.transformer_encoder(x)
        # Take the last time step for prediction
        x = x[:, -1, :]
        out = self.decoder(x)
        return self.sigmoid(out)

class SurgeDetector:
    def __init__(self):
        self.model = SurgeTransformer()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()

    def train_step(self, x_batch, y_batch):
        # x_batch: (batch, seq, 1), y_batch: (batch, 1)
        self.model.train()
        self.optimizer.zero_grad()
        output = self.model(x_batch)
        loss = self.criterion(output, y_batch)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def predict_surge_prob(self, sequence):
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(sequence).unsqueeze(0).unsqueeze(-1) # (1, seq, 1)
            prob = self.model(x)
        return prob.item()

if __name__ == "__main__":
    detector = SurgeDetector()
    dummy_input = np.random.rand(10, 1)
    print("Surge Probability:", detector.predict_surge_prob(dummy_input))
