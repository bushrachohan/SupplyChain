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
