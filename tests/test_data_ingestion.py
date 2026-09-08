"""
Unit tests for data ingestion layer.
Tests base DataSource interface adherence and CSVDataSource implementation.
"""

import os
import pytest
import pandas as pd
from data_ingestion.base import DataSource
from data_ingestion.csv_source import CSVDataSource


def test_data_source_abstract_class():
    """Verify DataSource cannot be instantiated directly."""
    with pytest.raises(TypeError):
        DataSource()


def test_csv_data_source_loads_demand():
    """Verify CSVDataSource loads historical demand with correct columns."""
    source = CSVDataSource(data_dir="data")
    df = source.load_historical_demand()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"sku_id", "date", "quantity_demanded", "location_id"}
    assert expected_cols.issubset(set(df.columns))
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_csv_data_source_loads_inventory():
    """Verify CSVDataSource loads inventory snapshot with correct columns."""
    source = CSVDataSource(data_dir="data")
    df = source.load_inventory_snapshot()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"sku_id", "current_stock", "reorder_point", "safety_stock", "unit_cost", "lead_time_days", "location_id"}
    assert expected_cols.issubset(set(df.columns))


def test_csv_data_source_loads_deliveries():
    """Verify CSVDataSource loads deliveries data with correct columns."""
    source = CSVDataSource(data_dir="data")
    df = source.load_deliveries()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"delivery_id", "carrier_id", "origin", "destination", "distance_km", "scheduled_date", "actual_date", "is_late"}
    assert expected_cols.issubset(set(df.columns))


def test_csv_data_source_missing_directory():
    """Verify FileNotFoundError is raised when file directory does not exist."""
    source = CSVDataSource(data_dir="non_existent_dir_123")
    with pytest.raises(FileNotFoundError):
        source.load_historical_demand()


def test_csv_data_source_drops_completely_blank_rows():
    """Verify completely blank rows (e.g. trailing empty row) are dropped, giving exactly 450 rows."""
    source = CSVDataSource(data_dir="data")
    df = source.load_historical_demand()
    assert len(df) == 450, f"Expected 450 valid rows after dropping blank row, got {len(df)}"
    assert df.isnull().sum().sum() == 0, "No missing values should remain from trailing blank rows"


def test_validate_dataframe_behavior():
    """Verify validate_dataframe drops completely blank rows but flags partially missing rows."""
    from app import validate_dataframe
    
    # 1. DataFrame with 1 valid row + 1 completely blank row
    df_blank = pd.DataFrame([
        {"sku_id": "SKU_101", "date": "2026-06-01", "quantity_demanded": 10, "location_id": "LOC_1"},
        {"sku_id": None, "date": None, "quantity_demanded": None, "location_id": None}
    ])
    req_cols = ["sku_id", "date", "quantity_demanded", "location_id"]
    status, msgs = validate_dataframe(df_blank, req_cols, "test.csv")
    assert status == "pass"
    assert "1 rows" in msgs[0]
    
    # 2. DataFrame with a partially missing row (1 field missing out of 4)
    df_partial = pd.DataFrame([
        {"sku_id": "SKU_101", "date": "2026-06-01", "quantity_demanded": None, "location_id": "LOC_1"}
    ])
    status_p, msgs_p = validate_dataframe(df_partial, req_cols, "test.csv")
    assert status_p == "warning"
    assert any("missing values" in msg for msg in msgs_p)

