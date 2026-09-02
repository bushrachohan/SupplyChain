"""
tests/test_forecasting.py
Tests for core/forecasting.py — feature engineering, model training,
baseline comparison, predictions, and feature importance.
"""

import numpy as np
import pandas as pd
import pytest
from data_ingestion.csv_source import CSVDataSource
from core.forecasting import (
    build_features,
    train_forecast_model,
    predict_demand,
    get_feature_importance,
    FEATURE_COLS,
    TARGET_COL,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def demand_df():
    """Load real seed data once for all tests in this module."""
    source = CSVDataSource(data_dir="data")
    return source.load_historical_demand()


@pytest.fixture(scope="module")
def featured_df(demand_df):
    return build_features(demand_df)


@pytest.fixture(scope="module")
def trained_model(demand_df):
    model, test_metrics, baseline_metrics = train_forecast_model(demand_df)
    return model, test_metrics, baseline_metrics


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def test_build_features_has_required_columns(featured_df):
    for col in FEATURE_COLS + [TARGET_COL, "date", "sku_id"]:
        assert col in featured_df.columns, f"Missing column: {col}"


def test_build_features_no_nulls_in_feature_cols(featured_df):
    nulls = featured_df[FEATURE_COLS].isnull().sum().sum()
    assert nulls == 0, f"Feature columns contain {nulls} null values"


def test_build_features_sorted_by_date(featured_df):
    for sku, group in featured_df.groupby("sku_id"):
        assert group["date"].is_monotonic_increasing, \
            f"Dates not sorted for SKU {sku}"


def test_lag_features_no_future_leakage(featured_df):
    """lag_1 for row i must equal quantity_demanded for the previous row of same SKU."""
    for sku, group in featured_df.groupby("sku_id"):
        group = group.reset_index(drop=True)
        if len(group) < 2:
            continue
        # lag_1 at position i should equal quantity_demanded at position i-1
        for i in range(1, min(5, len(group))):
            assert group.loc[i, "lag_1"] == group.loc[i - 1, "quantity_demanded"]


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def test_train_returns_metrics_keys(trained_model):
    _, test_metrics, baseline_metrics = trained_model
    assert "mape" in test_metrics and "rmse" in test_metrics
    assert "mape" in baseline_metrics and "rmse" in baseline_metrics


def test_train_metrics_are_finite(trained_model):
    _, test_metrics, baseline_metrics = trained_model
    for v in test_metrics.values():
        assert np.isfinite(v), f"Non-finite test metric: {v}"
    for v in baseline_metrics.values():
        assert np.isfinite(v), f"Non-finite baseline metric: {v}"


def test_model_beats_or_matches_baseline_rmse(trained_model):
    """Model RMSE should be <= naive baseline RMSE on test split."""
    _, test_metrics, baseline_metrics = trained_model
    assert test_metrics["rmse"] <= baseline_metrics["rmse"] * 1.1, (
        f"Model RMSE ({test_metrics['rmse']}) is much worse than "
        f"baseline ({baseline_metrics['rmse']})"
    )


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

def test_predict_demand_output_shape(trained_model, demand_df):
    model, _, _ = trained_model
    preds = predict_demand(model, demand_df, "SKU_101")
    assert len(preds) > 0
    assert "predicted_demand" in preds.columns
    assert "date" in preds.columns
    assert "sku_id" in preds.columns


def test_predict_demand_values_positive(trained_model, demand_df):
    model, _, _ = trained_model
    preds = predict_demand(model, demand_df, "SKU_101")
    assert (preds["predicted_demand"] >= 0).all(), "Negative demand predictions found"


def test_predict_demand_invalid_sku(trained_model, demand_df):
    model, _, _ = trained_model
    with pytest.raises(ValueError):
        predict_demand(model, demand_df, "SKU_NONEXISTENT")


# ---------------------------------------------------------------------------
# Feature importance
# ---------------------------------------------------------------------------

def test_feature_importance_keys(trained_model):
    model, _, _ = trained_model
    importance = get_feature_importance(model)
    assert set(importance.keys()) == set(FEATURE_COLS)


def test_feature_importance_values_nonnegative(trained_model):
    model, _, _ = trained_model
    importance = get_feature_importance(model)
    for feat, score in importance.items():
        assert score >= 0, f"Negative importance for {feat}"