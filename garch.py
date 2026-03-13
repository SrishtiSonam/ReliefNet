# backend/ml_models/garch_model.py

import pandas as pd
from arch import arch_model

class GARCHSurgePredictor:

    def __init__(self):
        self.model = None

    def train(self, series):
        self.model = arch_model(series, vol='Garch', p=1, q=1)
        self.results = self.model.fit(disp="off")

    def predict_volatility(self, horizon=7):
        forecast = self.results.forecast(horizon=horizon)
        return forecast.variance.values[-1]