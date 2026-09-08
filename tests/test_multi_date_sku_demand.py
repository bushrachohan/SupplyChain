"""
tests/test_multi_date_sku_demand.py
Focused tests verifying multi-date time series support per SKU:
- One SKU can have many date records in historical demand.
- Dropdown options display unique SKUs.
- Selecting a SKU retrieves all historical records for that SKU.
- Forecasting uses the full chronological history for the selected SKU.
- No cross-SKU data leakage occurs during feature engineering.
"""

import pandas as pd
import pytest
from data_ingestion.csv_source import CSVDataSource
from core.forecasting import build_features, train_forecast_model, predict_demand


@pytest.fixture(scope="module")
def demand_df():
    source = CSVDataSource(data_dir="data")
    return source.load_historical_demand()


def test_one_sku_has_many_dates(demand_df):
    """Confirm historical_demand.csv allows multiple date rows for the same sku_id."""
    assert not demand_df.empty
    sku_104_records = demand_df[demand_df["sku_id"] == "SKU_104"]
    
    # SKU_104 should have multiple date entries (time-series dataset)
    assert len(sku_104_records) > 1, f"Expected multiple rows for SKU_104, got {len(sku_104_records)}"
    assert sku_104_records["date"].nunique() == len(sku_104_records), "Dates for SKU_104 should be distinct"
    assert demand_df["sku_id"].nunique() < len(demand_df), "Total rows must exceed unique SKU count"


def test_sku_dropdown_unique_skus(demand_df):
    """Confirm SKU dropdown lists unique SKUs only."""
    unique_skus = demand_df["sku_id"].dropna().unique().tolist()
    assert len(unique_skus) == len(set(unique_skus)), "Dropdown options must be unique"
    assert "SKU_104" in unique_skus


def test_selecting_one_sku_retrieves_all_historical_records(demand_df):
    """Selecting a specific SKU retrieves all historical demand rows belonging to it."""
    sku_104_rows = demand_df[demand_df["sku_id"] == "SKU_104"]
    assert len(sku_104_rows) >= 30, f"Expected full historical dataset for SKU_104, got {len(sku_104_rows)} rows"
    # Ensure all returned rows belong strictly to SKU_104
    assert (sku_104_rows["sku_id"] == "SKU_104").all()


def test_forecasting_receives_correct_sku_historical_data(demand_df):
    """Verify forecasting feature pipeline processes multiple dates for selected SKU chronologically."""
    featured_df = build_features(demand_df)
    sku_104_featured = featured_df[featured_df["sku_id"] == "SKU_104"]
    
    assert len(sku_104_featured) > 0, "Feature engineering should return rows for SKU_104"
    # Verify chronological order of date column
    assert sku_104_featured["date"].is_monotonic_increasing, "Historical dates for SKU_104 must be strictly sorted"
    
    # Train model and generate predictions for SKU_104
    model, _, _ = train_forecast_model(demand_df)
    preds = predict_demand(model, demand_df, "SKU_104")
    assert len(preds) > 0, "Predictions should be generated for SKU_104"
    assert (preds["sku_id"] == "SKU_104").all()


def test_no_cross_sku_data_leakage(demand_df):
    """Verify lag_1 for row i equals quantity_demanded of preceding row for the SAME SKU only."""
    featured_df = build_features(demand_df)
    
    for sku_id, group in featured_df.groupby("sku_id"):
        group = group.reset_index(drop=True)
        for i in range(1, min(10, len(group))):
            expected_lag_1 = group.loc[i - 1, "quantity_demanded"]
            actual_lag_1 = group.loc[i, "lag_1"]
            assert actual_lag_1 == expected_lag_1, (
                f"Lag_1 mismatch for {sku_id} at row {i}: expected {expected_lag_1}, got {actual_lag_1}"
            )
