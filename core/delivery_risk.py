import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any
import lightgbm as lgb

from ml.explainability import get_tree_explainer_shap_values, get_top_driving_features

from ml.evaluation import (
    time_based_split,
    check_no_date_leakage,
    classification_metrics,
    majority_class_baseline,
    compare_to_baseline,
)

# ---------------------------------------------------------------------------
# 1. Feature Engineering
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build features for delivery risk prediction.
    Input df must have columns: carrier_id, origin, destination, distance_km, 
    scheduled_date, is_late, weather_condition, traffic_delay_hrs.
    """
    df = df.copy()
    df["scheduled_date"] = pd.to_datetime(df["scheduled_date"])
    df = df.sort_values("scheduled_date").reset_index(drop=True)

    # Time features
    df["day_of_week"] = df["scheduled_date"].dt.dayofweek
    df["month"] = df["scheduled_date"].dt.month

    # Categorical encoding
    for col in ["carrier_id", "origin", "destination", "weather_condition"]:
        if col in df.columns:
            df[f"{col}_encoded"] = df[col].astype("category").cat.codes

    return df

# ---------------------------------------------------------------------------
# 2. Train / Evaluate
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    "distance_km", 
    "traffic_delay_hrs",
    "day_of_week", 
    "month",
    "carrier_id_encoded", 
    "origin_encoded", 
    "destination_encoded", 
    "weather_condition_encoded",
]
TARGET_COL = "is_late"

def train_delivery_risk_model(
    df: pd.DataFrame,
) -> Tuple[lgb.LGBMClassifier, Dict[str, float], Dict[str, float]]:
    """
    Train a LightGBM delivery risk classifier.
    Applies time-based split, leakage check, trains on train+val,
    evaluates on test, and compares against majority baseline.

    Args:
        df: Raw deliveries DataFrame

    Returns:
        (model, test_metrics, baseline_metrics)
    """
    featured_df = build_features(df)

    # Time-based split
    train_df, val_df, test_df = time_based_split(featured_df, date_col="scheduled_date")

    # Leakage check
    check_no_date_leakage(train_df, val_df, test_df, date_col="scheduled_date")
    
    # Combine train + val for final training
    train_full = pd.concat([train_df, val_df], ignore_index=True)

    # Keep only available features (if some are missing in real DB vs CSV)
    actual_features = [f for f in FEATURE_COLS if f in featured_df.columns]

    X_train = train_full[actual_features]
    y_train = train_full[TARGET_COL].values
    X_test = test_df[actual_features]
    y_test = test_df[TARGET_COL].values

    # Train LightGBM
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.1,
        num_leaves=15,
        random_state=42,
        verbose=-1,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    test_metrics = classification_metrics(y_test, y_pred, y_prob)

    # Naive baseline: predict majority class
    y_baseline = majority_class_baseline(y_test)
    baseline_metrics = classification_metrics(y_test, y_baseline, None)

    return model, test_metrics, baseline_metrics


# ---------------------------------------------------------------------------
# 3. Predict & Explain (SHAP)
# ---------------------------------------------------------------------------

def predict_delivery_risk(
    model: lgb.LGBMClassifier,
    df: pd.DataFrame,
    delivery_id: str,
) -> Dict[str, Any]:
    """
    Predict risk for a specific delivery and provide SHAP explainability.
    
    Args:
        model: Trained LGBMClassifier.
        df: Full deliveries DataFrame.
        delivery_id: The ID of the delivery to predict.
        
    Returns:
        Dict with keys: delivery_id, risk_score (float), risk_label (str), top_features (dict)
    """
    featured_df = build_features(df)
    target_row = featured_df[featured_df["delivery_id"] == delivery_id]
    
    if target_row.empty:
        raise ValueError(f"No data found for delivery_id='{delivery_id}'")
        
    actual_features = [f for f in FEATURE_COLS if f in featured_df.columns]
    X_target = target_row[actual_features].iloc[[0]]
    
    prob = float(model.predict_proba(X_target)[0, 1])
    label = "high" if prob >= 0.5 else "low"
    
    # SHAP Explainability using ml.explainability helpers
    feature_importance = get_tree_explainer_shap_values(model, X_target)
    top_features = get_top_driving_features(feature_importance, top_k=3)
    
    return {
        "delivery_id": delivery_id,
        "risk_score": prob,
        "risk_label": label,
        "top_features": top_features
    }


# ---------------------------------------------------------------------------
# 4. Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from data_ingestion.csv_source import CSVDataSource

    source = CSVDataSource(data_dir="data")
    df = source.load_deliveries()

    print(f"Loaded {len(df)} rows of delivery data.")

    model, test_metrics, baseline_metrics = train_delivery_risk_model(df)

    print("\n=== Delivery Risk Results (Test Split) ===")
    print(f"Model   — AUC: {test_metrics.get('auc', 'N/A')}, F1: {test_metrics['f1']}, Precision: {test_metrics['precision']}, Recall: {test_metrics['recall']}")
    print(f"Baseline— AUC: {baseline_metrics.get('auc', 'N/A')}, F1: {baseline_metrics['f1']}, Precision: {baseline_metrics['precision']}, Recall: {baseline_metrics['recall']}")
    
    deltas = compare_to_baseline(test_metrics, baseline_metrics)
    print(f"Delta (positive = model is better): {deltas}")

    print("\n=== Sample Prediction (DEL_050) ===")
    pred = predict_delivery_risk(model, df, "DEL_050")
    print(f"Risk Score: {pred['risk_score']:.2f}")
    print(f"Risk Label: {pred['risk_label']}")
    print("Top Features Driving Prediction (SHAP):")
    for feat, impact in pred["top_features"].items():
        print(f"  {feat}: {impact:.4f}")
