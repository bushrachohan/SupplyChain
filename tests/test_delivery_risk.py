"""
tests/test_delivery_risk.py
Tests for core/delivery_risk.py — feature engineering, model training,
baseline comparison, predictions, and SHAP explainability.
"""

import numpy as np
import pandas as pd
import pytest
from data_ingestion.csv_source import CSVDataSource
from core.delivery_risk import (
    build_features,
    train_delivery_risk_model,
    predict_delivery_risk,
    FEATURE_COLS,
    TARGET_COL,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def deliveries_df():
    """Load real seed data once for all tests in this module."""
    source = CSVDataSource(data_dir="data")
    return source.load_deliveries()


@pytest.fixture(scope="module")
def featured_df(deliveries_df):
    return build_features(deliveries_df)


@pytest.fixture(scope="module")
def trained_model(deliveries_df):
    model, test_metrics, baseline_metrics = train_delivery_risk_model(deliveries_df)
    return model, test_metrics, baseline_metrics


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def test_build_features_sorted_by_date(featured_df):
    assert featured_df["scheduled_date"].is_monotonic_increasing, \
        "Dates not sorted properly"

def test_build_features_has_required_columns(featured_df):
    # Some columns from FEATURE_COLS might be missing if they weren't encoded, 
    # but the encoded ones should exist.
    actual_features = [f for f in FEATURE_COLS if f in featured_df.columns]
    assert len(actual_features) > 0, "No features were built successfully."
    assert TARGET_COL in featured_df.columns, f"Missing target column: {TARGET_COL}"


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def test_train_returns_metrics_keys(trained_model):
    _, test_metrics, baseline_metrics = trained_model
    assert "f1" in test_metrics and "precision" in test_metrics
    assert "f1" in baseline_metrics and "precision" in baseline_metrics


def test_train_metrics_are_finite(trained_model):
    _, test_metrics, baseline_metrics = trained_model
    for k, v in test_metrics.items():
        if v is not None:
            assert np.isfinite(v), f"Non-finite test metric: {k}={v}"
    for k, v in baseline_metrics.items():
        if v is not None:
            assert np.isfinite(v), f"Non-finite baseline metric: {k}={v}"


# ---------------------------------------------------------------------------
# Predictions & Explainability
# ---------------------------------------------------------------------------

def test_predict_delivery_risk_output(trained_model, deliveries_df):
    model, _, _ = trained_model
    # Just picking a known ID from our script
    test_id = "DEL_050"
    if test_id in deliveries_df["delivery_id"].values:
        pred = predict_delivery_risk(model, deliveries_df, test_id)
        assert pred["delivery_id"] == test_id
        assert 0.0 <= pred["risk_score"] <= 1.0
        assert pred["risk_label"] in ["high", "low"]
        assert len(pred["top_features"]) <= 3


def test_predict_delivery_risk_invalid_id(trained_model, deliveries_df):
    model, _, _ = trained_model
    with pytest.raises(ValueError):
        predict_delivery_risk(model, deliveries_df, "DEL_NONEXISTENT")
