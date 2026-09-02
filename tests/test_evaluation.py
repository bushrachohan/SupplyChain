"""
tests/test_evaluation.py
Tests for ml/evaluation.py — time-based splitting, leakage checks,
metrics, and baseline comparison utilities.
"""

import numpy as np
import pandas as pd
import pytest
from ml.evaluation import (
    time_based_split,
    check_no_date_leakage,
    regression_metrics,
    classification_metrics,
    naive_forecast_baseline,
    majority_class_baseline,
    compare_to_baseline,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    """50-row DataFrame with a date column and a numeric value column."""
    dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
    return pd.DataFrame({"date": dates, "value": np.arange(50, dtype=float)})


# ---------------------------------------------------------------------------
# time_based_split
# ---------------------------------------------------------------------------

def test_split_sizes(sample_df):
    train, val, test = time_based_split(sample_df, "date")
    assert len(train) + len(val) + len(test) == len(sample_df)
    assert len(train) > len(val)
    assert len(test) > 0


def test_split_order(sample_df):
    train, val, test = time_based_split(sample_df, "date")
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()


def test_split_invalid_fracs(sample_df):
    with pytest.raises(ValueError):
        time_based_split(sample_df, "date", train_frac=0.9, val_frac=0.2)


# ---------------------------------------------------------------------------
# check_no_date_leakage
# ---------------------------------------------------------------------------

def test_leakage_check_passes(sample_df):
    train, val, test = time_based_split(sample_df, "date")
    assert check_no_date_leakage(train, val, test, "date") is True


def test_leakage_check_fails():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({"date": dates})
    train = df.iloc[:6]
    val = df.iloc[4:]   # overlaps with train
    test = df.iloc[8:]
    with pytest.raises(ValueError):
        check_no_date_leakage(train, val, test, "date")


# ---------------------------------------------------------------------------
# regression_metrics
# ---------------------------------------------------------------------------

def test_regression_metrics_perfect():
    y = np.array([10.0, 20.0, 30.0])
    m = regression_metrics(y, y)
    assert m["mape"] == 0.0
    assert m["rmse"] == 0.0


def test_regression_metrics_keys():
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([11.0, 19.0, 31.0])
    m = regression_metrics(y_true, y_pred)
    assert "mape" in m and "rmse" in m


# ---------------------------------------------------------------------------
# classification_metrics
# ---------------------------------------------------------------------------

def test_classification_metrics_keys():
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0])
    y_prob = np.array([0.1, 0.9, 0.2, 0.4])
    m = classification_metrics(y_true, y_pred, y_prob)
    assert all(k in m for k in ["auc", "precision", "recall", "f1"])


def test_classification_metrics_no_prob():
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0])
    m = classification_metrics(y_true, y_pred)
    assert m["auc"] is None


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def test_naive_forecast_baseline_length():
    y = np.array([10.0, 20.0, 30.0, 40.0])
    b = naive_forecast_baseline(y)
    assert len(b) == len(y)


def test_naive_forecast_baseline_values():
    y = np.array([10.0, 20.0, 30.0])
    b = naive_forecast_baseline(y)
    assert b[0] == 10.0
    assert b[1] == 10.0
    assert b[2] == 20.0


def test_majority_class_baseline():
    y = np.array([0, 0, 0, 1, 1])
    b = majority_class_baseline(y)
    assert all(b == 0)


def test_compare_to_baseline():
    model = {"mape": 0.05, "rmse": 2.0}
    baseline = {"mape": 0.10, "rmse": 3.0}
    deltas = compare_to_baseline(model, baseline)
    assert deltas["mape"] == round(0.05 - 0.10, 4)
    assert deltas["rmse"] == round(2.0 - 3.0, 4)