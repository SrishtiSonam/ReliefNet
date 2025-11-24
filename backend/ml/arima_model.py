import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

class ArimaForecaster:
    def __init__(self, order=(5,1,0)):
        self.order = order
        self.model = None
        self.model_fit = None

    def train(self, series):
        """
        Train ARIMA model on a pandas Series or list.
        """
        self.model = ARIMA(series, order=self.order)
        self.model_fit = self.model.fit()
        return self.model_fit.summary()

    def predict(self, steps=5):
        if not self.model_fit:
            raise ValueError("Model not trained yet.")
        forecast = self.model_fit.forecast(steps=steps)
        return forecast.tolist()

if __name__ == "__main__":
    # Test
    data = [x + np.random.normal(0, 1) for x in range(100)]
    forecaster = ArimaForecaster()
    forecaster.train(data)
    print("Forecast:", forecaster.predict(3))
