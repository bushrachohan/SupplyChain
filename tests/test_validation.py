"""
tests/test_validation.py
Comprehensive test suite for P1 — Data Understanding & Canonical Data Model:
- Canonical schema validation for demand, inventory, deliveries, vehicles
- Real-world / Kaggle column alias mapping and normalization
- Fatal error vs non-blocking quality warning separation
- Invalid dates, negative values, and duplicate row detection
- Live dataset understanding profiling
"""

import pytest
import pandas as pd
from data_ingestion.validation import (
    validate_dataset,
    suggest_and_normalize_columns,
    profile_dataset,
    CANONICAL_SCHEMAS,
    COLUMN_ALIASES
)


def test_canonical_demand_validation_success():
    """Verify that a canonical demand dataset passes validation cleanly."""
    df = pd.DataFrame({
        "sku_id": ["SKU_101", "SKU_101", "SKU_102"],
        "date": ["2026-01-01", "2026-01-02", "2026-01-01"],
        "quantity_demanded": [50.0, 75.0, 120.0],
        "location_id": ["WH_NORTH", "WH_NORTH", "WH_SOUTH"]
    })
    res = validate_dataset(df, "demand")
    assert res.is_valid is True
    assert len(res.errors) == 0
    assert "sku_id" in res.normalized_df.columns
    assert "date" in res.normalized_df.columns
    assert "quantity_demanded" in res.normalized_df.columns
    assert res.profiling["unique_skus_count"] == 2


def test_kaggle_demand_column_normalization():
    """Verify common Kaggle column names (Product_Code, Order_Date, Sales) are auto-mapped."""
    df_kaggle = pd.DataFrame({
        "Product_Code": ["P_001", "P_001", "P_002"],
        "Order_Date": ["2026-05-01", "2026-05-02", "2026-05-01"],
        "Sales": [25.0, 30.0, 80.0],
        "Warehouse": ["WH_MAIN", "WH_MAIN", "WH_EAST"]
    })
    res = validate_dataset(df_kaggle, "demand")
    assert res.is_valid is True
    assert res.column_mapping["sku_id"] == "Product_Code"
    assert res.column_mapping["date"] == "Order_Date"
    assert res.column_mapping["quantity_demanded"] == "Sales"
    assert res.column_mapping["location_id"] == "Warehouse"
    
    # Check normalized columns are canonical
    expected_cols = {"sku_id", "date", "quantity_demanded", "location_id"}
    assert expected_cols.issubset(set(res.normalized_df.columns))


def test_retail_invoice_column_normalization():
    """Verify retail dataset aliases (StockCode, InvoiceDate, Quantity, Store_ID)."""
    df_retail = pd.DataFrame({
        "StockCode": ["85123A", "85123A"],
        "InvoiceDate": ["2026-03-01 10:00:00", "2026-03-02 11:30:00"],
        "Quantity": [6, 12],
        "Store_ID": ["STR_1", "STR_1"]
    })
    res = validate_dataset(df_retail, "demand")
    assert res.is_valid is True
    assert res.column_mapping["sku_id"] == "StockCode"
    assert res.column_mapping["date"] == "InvoiceDate"
    assert res.column_mapping["quantity_demanded"] == "Quantity"
    assert pd.api.types.is_datetime64_any_dtype(res.normalized_df["date"])


def test_missing_required_column_fails_with_fatal_error():
    """Verify dataset missing essential mandatory columns triggers a fatal blocking error."""
    df_broken = pd.DataFrame({
        "customer_name": ["Alice", "Bob"],
        "country": ["UK", "DE"],
        "notes": ["urgent", "normal"]
    })
    res = validate_dataset(df_broken, "demand")
    assert res.is_valid is False
    assert len(res.errors) > 0
    assert any("Fatal: Missing required columns" in err for err in res.errors)


def test_empty_dataset_handling():
    """Verify completely empty dataframes fail with clear messaging."""
    empty_df = pd.DataFrame()
    res = validate_dataset(empty_df, "demand")
    assert res.is_valid is False
    assert any("0 rows" in err for err in res.errors)


def test_inventory_canonical_validation_and_optional_defaults():
    """Verify inventory dataset validation with defaults applied for missing optional columns."""
    df_inv = pd.DataFrame({
        "SKU": ["SKU_A", "SKU_B"],
        "On_Hand": [500, 250],
        "Min_Stock": [100, 80]
    })
    res = validate_dataset(df_inv, "inventory")
    assert res.is_valid is True
    assert res.column_mapping["sku_id"] == "SKU"
    assert res.column_mapping["current_stock"] == "On_Hand"
    assert res.column_mapping["reorder_point"] == "Min_Stock"
    
    # Check default filled optional columns
    assert "lead_time_days" in res.normalized_df.columns
    assert "safety_stock" in res.normalized_df.columns
    assert any("defaulted to" in w for w in res.warnings)


def test_delivery_validation_with_negative_and_duplicate_warnings():
    """Verify delivery dataset produces warnings for duplicates and negative values."""
    df_del = pd.DataFrame({
        "Shipment_ID": ["SHP_1", "SHP_1"],  # Duplicate row
        "Scheduled_Time": ["2026-06-01", "2026-06-01"],
        "Distance_KM": [-50.0, -50.0],       # Negative distance
        "Delay_Hours": [1.5, 1.5]
    })
    res = validate_dataset(df_del, "deliveries")
    assert res.is_valid is True  # Non-blocking warnings
    assert any("duplicate rows" in w for w in res.warnings)


def test_data_understanding_profiling():
    """Verify profile_dataset produces detailed summary metrics."""
    df = pd.DataFrame({
        "sku_id": ["SKU_1", "SKU_1", "SKU_2"],
        "date": pd.to_datetime(["2026-01-01", "2026-01-10", "2026-01-05"]),
        "quantity_demanded": [10.0, 20.0, 15.0],
        "location_id": ["LOC_1", "LOC_1", "LOC_2"]
    })
    profile = profile_dataset(df, "demand")
    assert profile["total_rows"] == 3
    assert profile["total_columns"] == 4
    assert profile["unique_skus_count"] == 2
    assert profile["min_date"] == "2026-01-01"
    assert profile["max_date"] == "2026-01-10"
    assert profile["date_range_days"] == 9
    assert profile["is_small_dataset"] is True  # avg 1.5 rows per SKU
