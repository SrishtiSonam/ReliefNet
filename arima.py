# backend/ml_models/arima_model.py

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

class ARIMAForecaster:

    def __init__(self, order=(2,1,2)):
        self.order = order
        self.model = None

    def train(self, series):
        self.model = ARIMA(series, order=self.order).fit()

    def forecast(self, steps=7):
        if not self.model:
            raise ValueError("Model not trained")
        return self.model.forecast(steps=steps)