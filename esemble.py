# backend/ml_models/ensemble.py

class DemandEnsemble:

    def __init__(self, arima, garch, tft):
        self.arima = arima
        self.garch = garch
        self.tft = tft

        self.weights = {
            "arima": 0.3,
            "garch": 0.2,
            "tft": 0.5
        }

    def predict(self, steps=7):

        arima_pred = self.arima.forecast(steps)
        garch_pred = self.garch.predict_volatility(steps)
        tft_pred = self.tft.predict()

        final_prediction = (
            self.weights["arima"] * arima_pred +
            self.weights["garch"] * garch_pred +
            self.weights["tft"] * tft_pred
        )

        return final_prediction