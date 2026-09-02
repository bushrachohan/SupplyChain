"""
Database concrete implementation of the DataSource interface.
Loads demand, inventory, and delivery data from relational database tables via SQLAlchemy.
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from data_ingestion.base import DataSource


class DBDataSource(DataSource):
    """
    Concrete data source reading from relational DB tables (Postgres/Neon/SQLite).
    """

    def __init__(self, connection_url: str = None):
        if not connection_url:
            connection_url = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
        if not connection_url:
            raise ValueError("No database connection URL provided or found in environment variables.")
        
        self.engine = create_engine(connection_url)

    def load_historical_demand(self) -> pd.DataFrame:
        query = "SELECT sku_id, date, quantity_demanded, location_id FROM historical_demand"
        df = pd.read_sql(query, self.engine)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df

    def load_inventory_snapshot(self) -> pd.DataFrame:
        query = "SELECT sku_id, current_stock, reorder_point, safety_stock, unit_cost, lead_time_days, location_id FROM inventory_snapshots"
        return pd.read_sql(query, self.engine)

    def load_deliveries(self) -> pd.DataFrame:
        query = "SELECT delivery_id, carrier_id, origin, destination, distance_km, scheduled_date, actual_date, is_late, weather_condition, traffic_delay_hrs FROM deliveries"
        df = pd.read_sql(query, self.engine)
        if 'scheduled_date' in df.columns:
            df['scheduled_date'] = pd.to_datetime(df['scheduled_date'])
        if 'actual_date' in df.columns:
            df['actual_date'] = pd.to_datetime(df['actual_date'])
        return df
