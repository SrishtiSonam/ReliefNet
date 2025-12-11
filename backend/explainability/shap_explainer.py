"""
SHAP (SHapley Additive exPlanations) explainer for VFA decisions
Provides feature importance for allocation decisions
"""
import shap
import numpy as np
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')


def create_shap_explainer(vfa_model, background_data: np.ndarray = None):
    """
    Create SHAP explainer for VFA model
    
    Args:
        vfa_model: Trained VFA model (NN-VFA or DL-VFA)
        background_data: Background dataset for SHAP (optional)
    
    Returns:
        SHAP explainer object
    """
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import SHAP_CONFIG
    
    # Create prediction function for SHAP
    def predict_fn(X):
        """Prediction function for SHAP"""
        import torch
        vfa_model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            predictions = vfa_model(X_tensor).numpy().flatten()
        return predictions
    
    # Create background data if not provided
    if background_data is None:
        # Generate random background samples
        num_samples = SHAP_CONFIG['num_samples']
        background_data = np.random.rand(num_samples, 20).astype(np.float32)
    
    # Create SHAP explainer (using KernelExplainer for model-agnostic explanation)
    explainer = shap.KernelExplainer(predict_fn, background_data)
    
    return explainer


def explain_allocation_decision(state_features: np.ndarray,
                                vfa_model,
                                feature_names: List[str] = None) -> Dict[str, Any]:
    """
    Generate SHAP explanation for an allocation decision
    
    Args:
        state_features: State feature vector (20 dimensions)
        vfa_model: Trained VFA model
        feature_names: Optional list of feature names
    
    Returns:
        Dictionary with SHAP values and explanation
    """
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import SHAP_CONFIG
    
    if feature_names is None:
        feature_names = [
            'Food Inventory', 'Water Inventory', 'Medicine Inventory',
            'Shelter Inventory', 'Blankets Inventory',
            'Food Demand', 'Water Demand', 'Medicine Demand', 'Shelter Demand',
            'Hour of Day', 'Day of Week', 'Days Since Disaster',
            'Flood Risk', 'Road Accessibility',
            'Trucks Available', 'UAVs Available',
            'Population Density', 'Distance to Warehouse',
            'Deprivation Time', 'Priority Score'
        ]
    
    # Create explainer with small background
    background_data = np.random.rand(50, 20).astype(np.float32)
    explainer = create_shap_explainer(vfa_model, background_data)
    
    # Calculate SHAP values
    shap_values = explainer.shap_values(state_features.reshape(1, -1))
    
    # Get base value (expected value)
    base_value = explainer.expected_value
    
    # Create feature importance list
    feature_importance = []
    for i, (name, shap_val, feature_val) in enumerate(zip(
        feature_names, shap_values[0], state_features
    )):
        feature_importance.append({
            'name': name,
            'value': float(feature_val),
            'shap_value': float(shap_val),
            'impact': 'positive' if shap_val > 0 else 'negative',
            'abs_impact': abs(float(shap_val))
        })
    
    # Sort by absolute impact
    feature_importance.sort(key=lambda x: x['abs_impact'], reverse=True)
    
    # Get top features
    top_features = feature_importance[:SHAP_CONFIG['max_features']]
    
    # Generate natural language explanation
    explanation_text = generate_explanation_text(top_features, base_value)
    
    return {
        'base_value': float(base_value),
        'predicted_value': float(base_value + sum(shap_values[0])),
        'feature_importance': feature_importance,
        'top_features': top_features,
        'explanation': explanation_text
    }


def generate_explanation_text(top_features: List[Dict], base_value: float) -> str:
    """
    Generate natural language explanation from SHAP values
    
    Args:
        top_features: List of top feature importance dictionaries
        base_value: Base value from SHAP
    
    Returns:
        Human-readable explanation string
    """
    if not top_features:
        return "No significant features identified."
    
    # Start with most important feature
    top_feature = top_features[0]
    
    explanation = f"The allocation decision was primarily influenced by {top_feature['name']} "
    explanation += f"(value: {top_feature['value']:.2f}), which had a "
    explanation += f"{'positive' if top_feature['shap_value'] > 0 else 'negative'} impact "
    explanation += f"of {abs(top_feature['shap_value']):.3f} on the value estimate. "
    
    # Add secondary factors
    if len(top_features) > 1:
        explanation += f"Other important factors include {top_features[1]['name']} "
        explanation += f"and {top_features[2]['name'] if len(top_features) > 2 else 'resource availability'}. "
    
    # Add context
    explanation += f"The base expected value is {base_value:.3f}, and these features "
    explanation += "collectively determine the optimal allocation strategy to minimize "
    explanation += "deprivation time while balancing transportation costs and resource availability."
    
    return explanation


def batch_explain_allocations(states_features: List[np.ndarray],
                              vfa_model) -> List[Dict[str, Any]]:
    """
    Generate explanations for multiple allocation decisions
    
    Args:
        states_features: List of state feature vectors
        vfa_model: Trained VFA model
    
    Returns:
        List of explanation dictionaries
    """
    explanations = []
    
    for state_features in states_features:
        explanation = explain_allocation_decision(state_features, vfa_model)
        explanations.append(explanation)
    
    return explanations
