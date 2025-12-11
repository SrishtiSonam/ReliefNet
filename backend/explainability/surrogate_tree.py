"""
Surrogate decision tree for interpretable approximation of VFA
Creates a simple decision tree that mimics VFA decisions
"""
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.tree import plot_tree
import numpy as np
from typing import Dict, List, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64


def train_surrogate_tree(vfa_model, training_states: np.ndarray = None,
                        max_depth: int = 5) -> DecisionTreeRegressor:
    """
    Train a decision tree to approximate VFA model
    
    Args:
        vfa_model: Trained VFA model
        training_states: State features for training (optional)
        max_depth: Maximum tree depth
    
    Returns:
        Trained DecisionTreeRegressor
    """
    # Generate training data if not provided
    if training_states is None:
        num_samples = 1000
        training_states = np.random.rand(num_samples, 20).astype(np.float32)
    
    # Get VFA predictions for training data
    import torch
    vfa_model.eval()
    with torch.no_grad():
        X_tensor = torch.FloatTensor(training_states)
        vfa_predictions = vfa_model(X_tensor).numpy().flatten()
    
    # Train decision tree
    tree = DecisionTreeRegressor(
        max_depth=max_depth,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42
    )
    
    tree.fit(training_states, vfa_predictions)
    
    return tree


def explain_with_tree(state_features: np.ndarray,
                     vfa_model,
                     feature_names: List[str] = None) -> Dict[str, Any]:
    """
    Generate tree-based explanation for a decision
    
    Args:
        state_features: State feature vector
        vfa_model: Trained VFA model
        feature_names: Optional feature names
    
    Returns:
        Dictionary with tree explanation
    """
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
    
    # Train surrogate tree
    tree = train_surrogate_tree(vfa_model)
    
    # Get prediction
    tree_prediction = tree.predict(state_features.reshape(1, -1))[0]
    
    # Get decision path
    decision_path = tree.decision_path(state_features.reshape(1, -1))
    node_indicator = decision_path.toarray()[0]
    
    # Extract rules
    rules = []
    feature_indices = tree.tree_.feature
    thresholds = tree.tree_.threshold
    
    for node_id in range(len(node_indicator)):
        if node_indicator[node_id]:
            if feature_indices[node_id] != -2:  # Not a leaf
                feature_name = feature_names[feature_indices[node_id]]
                threshold = thresholds[node_id]
                feature_value = state_features[feature_indices[node_id]]
                
                if feature_value <= threshold:
                    comparison = '<='
                else:
                    comparison = '>'
                
                rules.append({
                    'feature': feature_name,
                    'threshold': float(threshold),
                    'comparison': comparison,
                    'value': float(feature_value)
                })
    
    # Generate text explanation
    text_rules = export_text(tree, feature_names=feature_names, max_depth=3)
    
    return {
        'tree_prediction': float(tree_prediction),
        'decision_rules': rules,
        'text_explanation': text_rules,
        'tree_depth': tree.get_depth(),
        'num_leaves': tree.get_n_leaves()
    }


def visualize_tree(vfa_model, feature_names: List[str] = None,
                  max_depth: int = 3) -> str:
    """
    Create visualization of surrogate decision tree
    
    Args:
        vfa_model: Trained VFA model
        feature_names: Optional feature names
        max_depth: Maximum depth to visualize
    
    Returns:
        Base64 encoded PNG image
    """
    if feature_names is None:
        feature_names = [
            'Food Inv', 'Water Inv', 'Med Inv', 'Shelter Inv', 'Blanket Inv',
            'Food Dem', 'Water Dem', 'Med Dem', 'Shelter Dem',
            'Hour', 'Day', 'Days Since',
            'Flood Risk', 'Access',
            'Trucks', 'UAVs',
            'Pop Density', 'Distance',
            'Depriv Time', 'Priority'
        ]
    
    # Train tree
    tree = train_surrogate_tree(vfa_model, max_depth=max_depth)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(
        tree,
        feature_names=feature_names,
        filled=True,
        rounded=True,
        ax=ax,
        fontsize=8
    )
    plt.title('Surrogate Decision Tree for VFA', fontsize=14)
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def get_feature_importance_from_tree(vfa_model,
                                    feature_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get feature importance from surrogate tree
    
    Args:
        vfa_model: Trained VFA model
        feature_names: Optional feature names
    
    Returns:
        List of feature importance dictionaries
    """
    if feature_names is None:
        feature_names = [f'Feature_{i}' for i in range(20)]
    
    # Train tree
    tree = train_surrogate_tree(vfa_model)
    
    # Get feature importance
    importances = tree.feature_importances_
    
    # Create list
    feature_importance = []
    for name, importance in zip(feature_names, importances):
        if importance > 0:
            feature_importance.append({
                'name': name,
                'importance': float(importance)
            })
    
    # Sort by importance
    feature_importance.sort(key=lambda x: x['importance'], reverse=True)
    
    return feature_importance
