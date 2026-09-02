import sys
sys.path.insert(0, '.')

import pytest
from sqlalchemy import inspect
from db.connection import engine

EXPECTED_TABLES = [
    "skus",
    "historical_demand",
    "inventory_snapshots",
    "forecast_results",
    "inventory_risk",
    "vehicles",
    "deliveries",
    "delivery_risk_predictions",
    "routes",
    "route_stops",
    "policies",
    "recommendations",
    "impact_simulations",
    "decision_traces",
    "approvals",
]

def test_all_tables_exist():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    for table in EXPECTED_TABLES:
        assert table in existing_tables, f"Missing table: {table}"

def test_connection_is_alive():
    with engine.connect() as conn:
        assert conn is not None