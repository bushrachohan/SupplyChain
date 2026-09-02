"""
Unit tests for ML evaluation utilities in ml/evaluation.py.
"""

import numpy as np
import pandas as pd
import pytest
from ml.evaluation import (
    time_based_split,
    check_data_leakage,
    evaluate_forecasting_metrics,
    naive_forecasting_baseline,
    evaluate_classification_metrics,
    majority_class_baseline
)


def test_time_based_split_ordering():
    """Verify time-based split preserves chronological order and proportions."""
    dates = pd.date_range("2026-01-01", periods=100, freq="D")
    df = pd.DataFrame({"date": dates, "val": np.arange(100)})
    
    train, val, test = time_based_split(df, time_column="date", train_ratio=0.7, val_ratio=0.15)
    
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()


def test_check_data_leakage():
    """Verify check_data_leakage correctly detects temporal order."""
    dates_train = pd.date_range("2026-01-01", periods=10, freq="D")
    dates_test = pd.date_range("2026-01-11", periods=5, freq="D")
    
    df_train = pd.DataFrame({"date": dates_train})
    df_test = pd.DataFrame({"date": dates_test})
    
    assert check_data_leakage(df_train, df_test, time_column="date") is True
    
    # Overlapping leakage case
    df_leakage = pd.DataFrame({"date": pd.date_range("2026-01-08", periods=5, freq="D")})
    assert check_data_leakage(df_train, df_leakage, time_column="date") is False


def test_evaluate_forecasting_metrics():
    """Verify calculation of MAE, RMSE, and MAPE."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([12.0, 18.0, 33.0])
    
    metrics = evaluate_forecasting_metrics(y_true, y_pred)
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "mape" in metrics
    assert metrics["mae"] > 0
    assert metrics["rmse"] > 0


def test_naive_forecasting_baseline():
    """Verify naive baseline repeats last observed value."""
    y_train = np.array([10, 15, 22])
    y_test = np.array([25, 30])
    
    pred = naive_forecasting_baseline(y_train, y_test)
    assert np.all(pred == 22)


def test_evaluate_classification_metrics():
    """Verify classification metrics calculation."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0, 1])
    y_prob = np.array([0.1, 0.9, 0.4, 0.2, 0.8])
    
    metrics = evaluate_classification_metrics(y_true, y_pred, y_prob)
    assert metrics["accuracy"] == 0.8
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics


def test_majority_class_baseline():
    """Verify majority class baseline predicts most frequent class."""
    y_train = np.array([0, 0, 0, 1])
    y_test = np.array([1, 1])
    
    pred = majority_class_baseline(y_train, y_test)
    assert np.all(pred == 0)
