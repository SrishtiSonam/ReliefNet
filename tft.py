# backend/ml_models/tft_model.py

import pytorch_lightning as pl
from pytorch_forecasting import TemporalFusionTransformer

class TFTModel:

    def __init__(self, dataset):
        self.dataset = dataset
        self.model = None

    def train(self):
        self.model = TemporalFusionTransformer.from_dataset(
            self.dataset,
            learning_rate=0.001,
            hidden_size=16,
            attention_head_size=4,
            dropout=0.1
        )

        trainer = pl.Trainer(max_epochs=10)
        trainer.fit(self.model)