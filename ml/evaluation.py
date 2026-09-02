"""
ML Evaluation utilities for SupplyChain Sentinel AI.
Provides time-based train/val/test splitting, leakage verification,
baseline models, and metric evaluations (MAPE, RMSE, Precision, Recall, AUC).
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


def time_based_split(
    df: pd.DataFrame,
    time_column: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Strict time-based split into train, validation, and test sets.
    Preserves chronological order without shuffling.
    """
    df_sorted = df.sort_values(by=time_column).reset_index(drop=True)
    n = len(df_sorted)
    
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df_sorted.iloc[:train_end].copy()
    val_df = df_sorted.iloc[train_end:val_end].copy()
    test_df = df_sorted.iloc[val_end:].copy()
    
    return train_df, val_df, test_df


def check_data_leakage(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    time_column: str
) -> bool:
    """
    Verifies that no record in train_df has a timestamp greater than or equal to the earliest timestamp in test_df.
    Returns True if temporal integrity is preserved (no leakage).
    """
    if train_df.empty or test_df.empty:
        return True
    
    max_train_time = pd.to_datetime(train_df[time_column]).max()
    min_test_time = pd.to_datetime(test_df[time_column]).min()
    
    return max_train_time < min_test_time


def evaluate_forecasting_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculates MAE, RMSE, and MAPE metrics for regression/forecasting models.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    # Avoid division by zero in MAPE
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if np.any(mask) else 0.0
    
    return {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "mape": round(float(mape), 4)
    }


def naive_forecasting_baseline(y_train: np.ndarray, y_test: np.ndarray) -> np.ndarray:
    """
    Naive forecasting baseline: predicts the last observed value in y_train for all test steps.
    """
    last_value = y_train[-1] if len(y_train) > 0 else 0.0
    return np.full_like(y_test, fill_value=last_value, dtype=float)


def evaluate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray = None
) -> Dict[str, float]:
    """
    Calculates Accuracy, Precision, Recall, F1, and ROC-AUC metrics for binary classification models.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4)
    }
    
    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            auc = roc_auc_score(y_true, y_prob)
            metrics["roc_auc"] = round(float(auc), 4)
        except Exception:
            metrics["roc_auc"] = 0.5
            
    return metrics


def majority_class_baseline(y_train: np.ndarray, y_test: np.ndarray) -> np.ndarray:
    """
    Majority class baseline: predicts the most frequent class in y_train for all test samples.
    """
    if len(y_train) == 0:
        return np.zeros_like(y_test)
    
    vals, counts = np.unique(y_train, return_counts=True)
    majority_val = vals[np.argmax(counts)]
    return np.full_like(y_test, fill_value=majority_val)
