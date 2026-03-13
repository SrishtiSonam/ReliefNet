"""
flood_predictor.py
LSTM-based flood severity (DFSI) forecaster.

Input:  sequence of shape (seq_len, n_features)
        Features: [t1d, t2d, t3d, t4d, t5d, current_dfsi]
Output: predicted DFSI values for the next `forecast_horizon` days (default 5)

The DemandForecaster in demand_model.py optionally accepts a FloodPredictor
instance.  When provided, the predicted DFSI replaces the historical average.
"""

from __future__ import annotations

import numpy as np
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not installed — FloodPredictor unavailable.")


# ── LSTM model definition ──────────────────────────────────────────────────────

if TORCH_AVAILABLE:

    class _LSTMModel(nn.Module):
        """Internal LSTM network for DFSI sequence prediction."""

        def __init__(self,
                     n_features:       int = 6,
                     hidden_size:      int = 64,
                     num_layers:       int = 2,
                     forecast_horizon: int = 5,
                     dropout:          float = 0.2):
            super().__init__()
            self.lstm = nn.LSTM(
                input_size=n_features,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0,
            )
            self.fc = nn.Linear(hidden_size, forecast_horizon)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            out, _ = self.lstm(x)          # (batch, seq_len, hidden)
            return self.fc(out[:, -1, :])  # (batch, forecast_horizon)

else:
    _LSTMModel = None  # type: ignore


# ── FloodPredictor public class ────────────────────────────────────────────────

class FloodPredictor:
    """
    PyTorch LSTM that predicts DFSI (flood severity) `forecast_horizon` days ahead.

    Parameters
    ----------
    n_features       : Number of input features per time step (default 6:
                       [t1d, t2d, t3d, t4d, t5d, current_dfsi]).
    hidden_size      : LSTM hidden units.
    num_layers       : Stacked LSTM layers.
    forecast_horizon : Days ahead to forecast (default 5).
    lr               : Adam learning rate.
    """

    def __init__(
        self,
        n_features:       int   = 6,
        hidden_size:      int   = 64,
        num_layers:       int   = 2,
        forecast_horizon: int   = 5,
        lr:               float = 1e-3,
    ):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for FloodPredictor.")

        self.n_features       = n_features
        self.hidden_size      = hidden_size
        self.num_layers       = num_layers
        self.forecast_horizon = forecast_horizon
        self.lr               = lr

        self.model     = _LSTMModel(n_features, hidden_size, num_layers,
                                    forecast_horizon)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn   = nn.MSELoss()
        self._trained  = False

    # ── Training ───────────────────────────────────────────────────────────────

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
    ) -> None:
        """
        Train the LSTM predictor.

        Parameters
        ----------
        X : shape (n_samples, seq_len, n_features)   — input sequences.
        y : shape (n_samples, forecast_horizon)       — target DFSI values.
        epochs     : Training epochs.
        batch_size : Mini-batch size.
        """
        import torch

        X_t = torch.FloatTensor(X)
        y_t = torch.FloatTensor(y)

        dataset    = torch.utils.data.TensorDataset(X_t, y_t)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                                  shuffle=True)

        self.model.train()
        for epoch in range(epochs):
            ep_loss = 0.0
            for xb, yb in dataloader:
                self.optimizer.zero_grad()
                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                ep_loss += loss.item()
            if (epoch + 1) % 10 == 0:
                logger.info(f"FloodPredictor epoch {epoch+1}/{epochs} "
                            f"loss={ep_loss / len(dataloader):.4f}")

        self._trained = True
        logger.info("FloodPredictor training complete.")

    # ── Inference ──────────────────────────────────────────────────────────────

    def predict(self, sequence: np.ndarray) -> np.ndarray:
        """
        Predict DFSI for the next `forecast_horizon` days.

        Parameters
        ----------
        sequence : shape (seq_len, n_features) or (1, seq_len, n_features).

        Returns
        -------
        np.ndarray of shape (forecast_horizon,) with predicted DFSI values.
        """
        import torch

        if sequence.ndim == 2:
            sequence = sequence[np.newaxis, ...]       # Add batch dim

        self.model.eval()
        with torch.no_grad():
            x   = torch.FloatTensor(sequence)
            out = self.model(x).squeeze(0).numpy()
        return np.clip(out, 0.0, 1.0)   # DFSI in [0, 1]

    # ── Serialisation ──────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """Save model weights and config to `path` via torch.save."""
        import torch
        torch.save(
            {
                "model_state":      self.model.state_dict(),
                "n_features":       self.n_features,
                "hidden_size":      self.hidden_size,
                "num_layers":       self.num_layers,
                "forecast_horizon": self.forecast_horizon,
                "lr":               self.lr,
            },
            path,
        )
        logger.info(f"FloodPredictor saved to {path}")

    @classmethod
    def load(cls, path: str) -> "FloodPredictor":
        """Load a previously saved FloodPredictor from `path`."""
        import torch
        checkpoint = torch.load(path, map_location="cpu")
        instance = cls(
            n_features       = checkpoint["n_features"],
            hidden_size      = checkpoint["hidden_size"],
            num_layers       = checkpoint["num_layers"],
            forecast_horizon = checkpoint["forecast_horizon"],
            lr               = checkpoint["lr"],
        )
        instance.model.load_state_dict(checkpoint["model_state"])
        instance._trained = True
        logger.info(f"FloodPredictor loaded from {path}")
        return instance
