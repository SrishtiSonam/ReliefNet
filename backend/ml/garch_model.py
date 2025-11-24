from arch import arch_model
import numpy as np

class GarchVolatilityModel:
    def __init__(self, p=1, q=1):
        self.p = p
        self.q = q
        self.res = None

    def train(self, returns):
        """
        Train GARCH model on returns (or residuals).
        """
        # Simple scaling to avoid convergence issues with small numbers
        scale = 100.0
        scaled_returns = np.array(returns) * scale
        
        am = arch_model(scaled_returns, vol='Garch', p=self.p, q=self.q)
        self.res = am.fit(disp='off')
        return self.res.summary()

    def predict_volatility(self, horizon=5):
        if not self.res:
            raise ValueError("Model not trained.")
        forecasts = self.res.forecast(horizon=horizon)
        # Scale back
        return (np.sqrt(forecasts.variance.values[-1, :]) / 100.0).tolist()

if __name__ == "__main__":
    returns = np.random.normal(0, 1, 1000)
    garch = GarchVolatilityModel()
    garch.train(returns)
    print("Volatility Forecast:", garch.predict_volatility(3))
