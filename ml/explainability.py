"""
ml/explainability.py
Reusable explainability utilities using SHAP and LightGBM feature importance.
"""

import pandas as pd
import shap
from typing import Dict, Any

def get_tree_explainer_shap_values(model, X_target: pd.DataFrame) -> Dict[str, float]:
    """
    Given a tree-based model (e.g. LightGBM) and a single row dataframe X_target,
    compute the SHAP values and return them as a dictionary mapped to feature names.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_target)
    
    # LightGBM binary classifier with TreeExplainer might return a list of ndarrays
    if isinstance(shap_values, list):
        # We take index 1 for the positive class
        shap_vals = shap_values[1][0]
    else:
        # Otherwise it's a single array (e.g., regression or some single-output models)
        if len(shap_values.shape) > 1:
            shap_vals = shap_values[0]
        else:
            shap_vals = shap_values
            
    features = X_target.columns.tolist()
    feature_importance = dict(zip(features, shap_vals))
    return feature_importance

def get_top_driving_features(feature_importance: Dict[str, float], top_k: int = 3) -> Dict[str, float]:
    """
    Given a dictionary of feature importances (e.g. from SHAP), return the top_k
    features driving the prediction (sorted by absolute impact).
    """
    return dict(sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:top_k])
