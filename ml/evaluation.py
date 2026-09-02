"""
ml/evaluation.py
Reusable evaluation utilities for all ML models in SupplyChain Sentinel AI.
Provides: time-based train/val/test splitting, leakage checks, baseline
comparison, and standard metrics. Every predictive model must use these.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
from sklearn.metrics import (
    mean_absolute_percentage_error,
    root_mean_squared_error,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)


# ---------------------------------------------------------------------------
# 1. Time-based splitting
# ---------------------------------------------------------------------------

def time_based_split(
    df: pd.DataFrame,
    date_col: str,
    train_frac: float = 0.7,
    val_frac: float = 0.15,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split a DataFrame into train / validation / test by time order.
    Never shuffles — always splits on sorted date values.

    Args:
        df:         DataFrame with a date/datetime column.
        date_col:   Name of the date column to sort by.
        train_frac: Fraction of data for training (default 70%).
        val_frac:   Fraction of data for validation (default 15%).
                    Remaining fraction goes to test.

    Returns:
        (train_df, val_df, test_df) — non-overlapping, time-ordered.
    """
    if train_frac + val_frac >= 1.0:
        raise ValueError("train_frac + val_frac must be less than 1.0")

    df_sorted = df.sort_values(date_col).reset_index(drop=True)
    n = len(df_sorted)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))

    train = df_sorted.iloc[:train_end]
    val = df_sorted.iloc[train_end:val_end]
    test = df_sorted.iloc[val_end:]

    return train, val, test


# ---------------------------------------------------------------------------
# 2. Leakage check
# ---------------------------------------------------------------------------

def check_no_date_leakage(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    date_col: str,
) -> bool:
    """
    Assert that train max date < val min date < test min date.
    Raises ValueError if any overlap is detected.

    Returns True if clean.
    """
    train_max = train[date_col].max()
    val_min = val[date_col].min()
    val_max = val[date_col].max()
    test_min = test[date_col].min()

    if train_max >= val_min:
        raise ValueError(
            f"Leakage: train max date ({train_max}) >= val min date ({val_min})"
        )
    if val_max >= test_min:
        raise ValueError(
            f"Leakage: val max date ({val_max}) >= test min date ({test_min})"
        )

    return True


# ---------------------------------------------------------------------------
# 3. Regression metrics (forecasting)
# ---------------------------------------------------------------------------

def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute MAPE and RMSE for regression/forecasting models.

    Args:
        y_true: Ground truth values.
        y_pred: Predicted values.

    Returns:
        Dict with keys 'mape' and 'rmse'.
    """
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    return {"mape": round(float(mape), 4), "rmse": round(float(rmse), 4)}


# ---------------------------------------------------------------------------
# 4. Classification metrics (delivery risk)
# ---------------------------------------------------------------------------

def classification_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None
) -> Dict[str, float]:
    """
    Compute AUC, precision, recall, F1 for binary classifiers.

    Args:
        y_true: Ground truth binary labels.
        y_pred: Predicted binary labels.
        y_prob: Predicted probabilities for the positive class (for AUC).

    Returns:
        Dict with keys 'auc', 'precision', 'recall', 'f1'.
    """
    metrics = {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
    }
    if y_prob is not None:
        metrics["auc"] = round(float(roc_auc_score(y_true, y_prob)), 4)
    else:
        metrics["auc"] = None
    return metrics


# ---------------------------------------------------------------------------
# 5. Baseline comparisons
# ---------------------------------------------------------------------------

def naive_forecast_baseline(y_true: np.ndarray) -> np.ndarray:
    """
    Naive forecasting baseline: predict the previous observed value.
    y_true[i] is predicted by y_true[i-1].
    First prediction uses y_true[0] (no shift available).

    Returns array of same length as y_true.
    """
    baseline = np.empty_like(y_true, dtype=float)
    baseline[0] = y_true[0]
    baseline[1:] = y_true[:-1]
    return baseline


def majority_class_baseline(y_true: np.ndarray) -> np.ndarray:
    """
    Classification baseline: always predict the majority class.
    Returns array of same length as y_true filled with the majority label.
    """
    values, counts = np.unique(y_true, return_counts=True)
    majority = values[np.argmax(counts)]
    return np.full_like(y_true, fill_value=majority)


def compare_to_baseline(
    model_metrics: Dict[str, float],
    baseline_metrics: Dict[str, float],
) -> Dict[str, float]:
    """
    Compute the delta between model and baseline metrics.
    Positive delta = model is better.

    Returns dict of {metric: delta}.
    """
    deltas = {}
    for key in model_metrics:
        if model_metrics[key] is not None and baseline_metrics.get(key) is not None:
            deltas[key] = round(model_metrics[key] - baseline_metrics[key], 4)
    return deltas