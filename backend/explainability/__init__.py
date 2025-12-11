# Explainability Module
from .shap_explainer import (
    create_shap_explainer, explain_allocation_decision,
    generate_explanation_text, batch_explain_allocations
)
from .surrogate_tree import (
    train_surrogate_tree, explain_with_tree,
    visualize_tree, get_feature_importance_from_tree
)

__all__ = [
    'create_shap_explainer', 'explain_allocation_decision',
    'generate_explanation_text', 'batch_explain_allocations',
    'train_surrogate_tree', 'explain_with_tree',
    'visualize_tree', 'get_feature_importance_from_tree'
]
