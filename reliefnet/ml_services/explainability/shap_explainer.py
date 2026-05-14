# reliefnet/ml_services/explainability/shap_explainer.py
import shap
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any

class ReliefSHAPExplainer:
    """
    Explainability service using SHAP (SHapley Additive exPlanations).
    Helps disaster coordinators understand which features contributed most 
    to a specific risk or demand forecast.
    """
    def __init__(self, model: Any, background_data: pd.DataFrame):
        # TreeExplainer is efficient for XGBoost/RandomForest models
        self.explainer = shap.TreeExplainer(model)
        self.background_data = background_data

    def explain_instance(self, instance: pd.DataFrame):
        """Generates SHAP values for a single district/prediction."""
        shap_values = self.explainer.shap_values(instance)
        
        # Breakdown of feature contributions
        feature_importance = dict(zip(instance.columns, shap_values[0]))
        
        # Sort by magnitude
        sorted_importance = dict(sorted(feature_importance.items(), key=lambda item: abs(item[1]), reverse=True))
        
        return {
            "shap_values": sorted_importance,
            "base_value": self.explainer.expected_value,
            "prediction": self.explainer.model.predict(instance)[0]
        }

    def plot_summary(self, data: pd.DataFrame, output_path: str = "reports/shap_summary.png"):
        """Generates a summary plot of feature importance across the dataset."""
        shap_values = self.explainer.shap_values(data)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, data, show=False)
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"✅ SHAP summary plot saved to {output_path}")

# Note: In a real implementation, this would be initialized with a trained XGBoost model.
