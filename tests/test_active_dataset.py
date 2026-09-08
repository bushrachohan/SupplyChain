import os
import tempfile
import pytest
import pandas as pd
from sqlalchemy import create_engine, text

from data_ingestion.active_dataset import ActiveDatasetContext, DatasetMetadata
from data_ingestion.csv_source import CSVDataSource
from data_ingestion.excel_source import ExcelDataSource
from data_ingestion.db_source import DBDataSource


def test_active_dataset_lifecycle():
    """Verify the lifecycle states and transitions of the ActiveDatasetContext."""
    context = ActiveDatasetContext()
    
    # 1. Starts empty, should raise ValueError
    with pytest.raises(ValueError, match="No active dataset configured"):
        context.get_source()
        
    with pytest.raises(ValueError, match="No active dataset metadata configured"):
        context.get_metadata()
        
    # 2. Upload/Connect a dataset
    source = CSVDataSource(data_dir="data")
    metadata = DatasetMetadata(
        source_type="csv",
        name="Test Business Data",
        status="uploaded/connected",
        connected_at="2026-09-08T10:00:00Z"
    )
    context.set_active(source, metadata)
    
    assert context.get_source() is source
    assert context.get_metadata().status == "uploaded/connected"
    assert not context.is_active  # only True when status == "active"
    
    # 3. Update status to validated, then active
    context.update_status("validated")
    assert context.get_metadata().status == "validated"
    assert not context.is_active
    
    context.update_status("active")
    assert context.get_metadata().status == "active"
    assert context.is_active
    
    # 4. Invalid status transition should fail
    with pytest.raises(ValueError, match="Invalid status"):
        context.update_status("not_a_real_status")
        
    # 5. Clear dataset (replaced)
    context.clear()
    
    # It should be empty again
    assert not context.is_active
    with pytest.raises(ValueError, match="No active dataset configured"):
        context.get_source()


def test_active_dataset_invalidation_listeners():
    """Verify listener callbacks are fired on dataset activation, update, and clear."""
    context = ActiveDatasetContext()
    notification_count = 0

    def on_change():
        nonlocal notification_count
        notification_count += 1

    context.subscribe(on_change)

    # Activating triggers listener
    source = CSVDataSource(data_dir="data")
    meta = DatasetMetadata(source_type="csv", name="D1", status="active", connected_at="2026-09-08T10:00:00Z")
    context.set_active(source, meta)
    assert notification_count == 1

    # Status update triggers listener
    context.update_status("validated")
    assert notification_count == 2

    # Clear triggers listener
    context.clear()
    assert notification_count == 3

    # Unsubscribe stops notifications
    context.unsubscribe(on_change)
    context.set_active(source, meta)
    assert notification_count == 3  # unchanged


def test_active_dataset_delegation_with_real_csv():
    """Verify ActiveDataset delegates data loading methods to underlying real CSV data."""
    context = ActiveDatasetContext()
    source = CSVDataSource(data_dir="data")
    meta = DatasetMetadata(source_type="csv", name="CSV Real Data", status="active", connected_at="2026-09-08T10:00:00Z")
    context.set_active(source, meta)

    demand = context.load_historical_demand()
    assert isinstance(demand, pd.DataFrame)
    assert not demand.empty
    assert {"sku_id", "date", "quantity_demanded"}.issubset(set(demand.columns))

    inventory = context.load_inventory_snapshot()
    assert isinstance(inventory, pd.DataFrame)
    assert not inventory.empty
    assert {"sku_id", "current_stock", "reorder_point"}.issubset(set(inventory.columns))

    deliveries = context.load_deliveries()
    assert isinstance(deliveries, pd.DataFrame)
    assert not deliveries.empty
    assert {"delivery_id", "scheduled_date", "is_late"}.issubset(set(deliveries.columns))


def test_active_dataset_with_excel_and_db_sources():
    """Verify Excel and Database sources can both be plugged into the ActiveDataset context."""
    context = ActiveDatasetContext()

    # 1. Test Database DataSource integration
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
        conn.execute(text("INSERT INTO historical_demand VALUES ('SKU_DB_1', '2026-08-01', 120, 'LOC_1')"))
        conn.execute(text("INSERT INTO inventory_snapshots VALUES ('SKU_DB_1', 300, 100, 50, 12.5, 4, 'LOC_1')"))
        conn.execute(text("INSERT INTO deliveries VALUES ('DEL_DB_1', 'CAR_1', 'WH1', 'WH2', 150, '2026-08-01', '2026-08-02', 0, 'CLEAR', 0.0)"))
        conn.commit()

    db_source = DBDataSource(connection_url="sqlite:///:memory:")
    db_source.engine = engine

    db_meta = DatasetMetadata(source_type="db", name="Neon Enterprise DB", status="active", connected_at="2026-09-08T10:00:00Z")
    context.set_active(db_source, db_meta)

    assert context.get_metadata().source_type == "db"
    assert context.load_historical_demand().iloc[0]["sku_id"] == "SKU_DB_1"
    assert context.load_inventory_snapshot().iloc[0]["current_stock"] == 300

    # 2. Test Excel DataSource integration
    with tempfile.TemporaryDirectory() as tmp_dir:
        excel_path = os.path.join(tmp_dir, "test_excel.xlsx")
        demand_df = pd.DataFrame({"sku_id": ["SKU_EXCEL_1"], "date": ["2026-08-05"], "quantity_demanded": [90], "location_id": ["LOC_2"]})
        inv_df = pd.DataFrame({"sku_id": ["SKU_EXCEL_1"], "current_stock": [250], "reorder_point": [60], "safety_stock": [30], "unit_cost": [15.0], "lead_time_days": [3], "location_id": ["LOC_2"]})
        del_df = pd.DataFrame({"delivery_id": ["DEL_EXCEL_1"], "carrier_id": ["C1"], "origin": ["WH1"], "destination": ["WH3"], "distance_km": [80], "scheduled_date": ["2026-08-05"], "actual_date": ["2026-08-05"], "is_late": [0], "weather_condition": ["CLEAR"], "traffic_delay_hrs": [0.0]})

        with pd.ExcelWriter(excel_path) as writer:
            demand_df.to_excel(writer, sheet_name="historical_demand", index=False)
            inv_df.to_excel(writer, sheet_name="inventory_snapshot", index=False)
            del_df.to_excel(writer, sheet_name="deliveries", index=False)

        excel_source = ExcelDataSource(excel_path=excel_path)
        excel_meta = DatasetMetadata(source_type="excel", name="Q3 Spreadsheet", status="active", connected_at="2026-09-08T11:00:00Z")

        # Switching to Excel replaces the DB dataset
        context.set_active(excel_source, excel_meta)
        assert context.get_metadata().source_type == "excel"
        assert context.load_historical_demand().iloc[0]["sku_id"] == "SKU_EXCEL_1"


def test_downstream_consumption_and_cache_invalidation():
    """
    Verify a downstream service that consumes active_dataset receives the selected data
    and invalidates its cached derived results when the dataset is replaced or cleared.
    """
    context = ActiveDatasetContext()

    class MockDownstreamForecaster:
        def __init__(self, dataset_ctx: ActiveDatasetContext):
            self.ctx = dataset_ctx
            self.cached_demand = None
            self.ctx.subscribe(self.invalidate)

        def invalidate(self):
            self.cached_demand = None

        def get_demand_skus(self):
            if self.cached_demand is None:
                self.cached_demand = self.ctx.load_historical_demand()
            return set(self.cached_demand["sku_id"].unique())

    forecaster = MockDownstreamForecaster(context)

    # 1. Calling forecaster with no active dataset raises ValueError (no silent fallback)
    with pytest.raises(ValueError, match="No active dataset configured"):
        forecaster.get_demand_skus()

    # 2. Activate Dataset A
    source_a = CSVDataSource(data_dir="data")
    meta_a = DatasetMetadata(source_type="csv", name="Dataset A", status="active", connected_at="2026-09-08T10:00:00Z")
    context.set_active(source_a, meta_a)

    skus_a = forecaster.get_demand_skus()
    assert len(skus_a) > 0
    assert forecaster.cached_demand is not None

    # 3. Activate Dataset B (with different data)
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE historical_demand (sku_id TEXT, date TEXT, quantity_demanded INTEGER, location_id TEXT)"))
        conn.execute(text("INSERT INTO historical_demand VALUES ('SKU_NEW_BUSINESS_DATA', '2026-08-01', 500, 'LOC_MAIN')"))
        conn.commit()

    source_b = DBDataSource(connection_url="sqlite:///:memory:")
    source_b.engine = engine
    meta_b = DatasetMetadata(source_type="db", name="Dataset B", status="active", connected_at="2026-09-08T11:00:00Z")

    # When B is activated, cache was invalidated
    context.set_active(source_b, meta_b)
    assert forecaster.cached_demand is None

    # Re-fetch returns Dataset B SKUs
    skus_b = forecaster.get_demand_skus()
    assert skus_b == {"SKU_NEW_BUSINESS_DATA"}

    # 4. Clear dataset -> invalidates cache and prevents silent fallback
    context.clear()
    assert forecaster.cached_demand is None
    with pytest.raises(ValueError, match="No active dataset configured"):
        forecaster.get_demand_skus()

