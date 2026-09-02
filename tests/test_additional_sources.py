"""
Unit tests for Excel, DB, and API data source implementations.
"""

import os
import tempfile
import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from data_ingestion.excel_source import ExcelDataSource
from data_ingestion.db_source import DBDataSource
from data_ingestion.api_source import APIDataSource


def test_excel_data_source():
    """Verify ExcelDataSource correctly loads sheets from an Excel workbook."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        excel_path = os.path.join(tmp_dir, "test_data.xlsx")
        
        demand_df = pd.DataFrame({
            "sku_id": ["SKU_001"],
            "date": ["2026-06-01"],
            "quantity_demanded": [50],
            "location_id": ["LOC_NORTH"]
        })
        inventory_df = pd.DataFrame({
            "sku_id": ["SKU_001"],
            "current_stock": [100],
            "reorder_point": [50],
            "safety_stock": [30],
            "unit_cost": [10.0],
            "lead_time_days": [5],
            "location_id": ["LOC_NORTH"]
        })
        deliveries_df = pd.DataFrame({
            "delivery_id": ["DEL_001"],
            "carrier_id": ["C1"],
            "origin": ["WH1"],
            "destination": ["R1"],
            "distance_km": [100],
            "scheduled_date": ["2026-06-01"],
            "actual_date": ["2026-06-01"],
            "is_late": [0],
            "weather_condition": ["CLEAR"],
            "traffic_delay_hrs": [0.0]
        })
        
        with pd.ExcelWriter(excel_path) as writer:
            demand_df.to_excel(writer, sheet_name="historical_demand", index=False)
            inventory_df.to_excel(writer, sheet_name="inventory_snapshot", index=False)
            deliveries_df.to_excel(writer, sheet_name="deliveries", index=False)
            
        source = ExcelDataSource(excel_path=excel_path)
        
        loaded_demand = source.load_historical_demand()
        assert not loaded_demand.empty
        assert loaded_demand.iloc[0]["sku_id"] == "SKU_001"
        
        loaded_inv = source.load_inventory_snapshot()
        assert loaded_inv.iloc[0]["current_stock"] == 100
        
        loaded_del = source.load_deliveries()
        assert loaded_del.iloc[0]["delivery_id"] == "DEL_001"


def test_db_data_source():
    """Verify DBDataSource reads data correctly using SQLite in-memory engine."""
    engine = create_engine("sqlite:///:memory:")
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE historical_demand (
                sku_id TEXT, date TEXT, quantity_demanded INTEGER, location_id TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE inventory_snapshots (
                sku_id TEXT, current_stock INTEGER, reorder_point INTEGER, safety_stock INTEGER, unit_cost REAL, lead_time_days INTEGER, location_id TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE deliveries (
                delivery_id TEXT, carrier_id TEXT, origin TEXT, destination TEXT, distance_km INTEGER, scheduled_date TEXT, actual_date TEXT, is_late INTEGER, weather_condition TEXT, traffic_delay_hrs REAL
            )
        """))
        conn.execute(text("INSERT INTO historical_demand VALUES ('SKU_002', '2026-07-01', 75, 'LOC_SOUTH')"))
        conn.execute(text("INSERT INTO inventory_snapshots VALUES ('SKU_002', 200, 100, 50, 25.0, 7, 'LOC_SOUTH')"))
        conn.execute(text("INSERT INTO deliveries VALUES ('DEL_002', 'C2', 'WH2', 'R2', 200, '2026-07-01', '2026-07-02', 1, 'RAIN', 1.5)"))
        conn.commit()
        
    source = DBDataSource(connection_url="sqlite:///:memory:")
    source.engine = engine
    
    df_demand = source.load_historical_demand()
    assert len(df_demand) == 1
    assert df_demand.iloc[0]["sku_id"] == "SKU_002"
    
    df_inv = source.load_inventory_snapshot()
    assert df_inv.iloc[0]["current_stock"] == 200
    
    df_del = source.load_deliveries()
    assert df_del.iloc[0]["is_late"] == 1


def test_api_data_source_stubs():
    """Verify APIDataSource raises NotImplementedError for stubs."""
    source = APIDataSource()
    with pytest.raises(NotImplementedError):
        source.load_historical_demand()
