import shap
import numpy as np

class ShapExplainer:
    def __init__(self, model, background_data):
        """
        model: A callable prediction function or model object
        background_data: numpy array of background samples
        """
        self.explainer = shap.KernelExplainer(model, background_data)

    def explain(self, instance):
        shap_values = self.explainer.shap_values(instance)
        return shap_values

if __name__ == "__main__":
    # Mock model
    def mock_predict(x):
        return np.sum(x, axis=1)
    
    data = np.random.rand(10, 5)
    explainer = ShapExplainer(mock_predict, data)
    explanation = explainer.explain(np.random.rand(1, 5))
    print("SHAP values:", explanation)
