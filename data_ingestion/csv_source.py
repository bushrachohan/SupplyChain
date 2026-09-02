"""
CSV concrete implementation of the DataSource interface.
Loads demand, inventory, and delivery data from CSV files.
"""

import os
import pandas as pd
from data_ingestion.base import DataSource


class CSVDataSource(DataSource):
    """
    Concrete data source reading from local CSV files.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def load_historical_demand(self) -> pd.DataFrame:
        file_path = self._get_path("historical_demand.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Demand data file not found at: {file_path}")
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def load_inventory_snapshot(self) -> pd.DataFrame:
        file_path = self._get_path("inventory_snapshot.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Inventory snapshot file not found at: {file_path}")
        return pd.read_csv(file_path)

    def load_deliveries(self) -> pd.DataFrame:
        file_path = self._get_path("deliveries.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Deliveries data file not found at: {file_path}")
        df = pd.read_csv(file_path)
        if 'scheduled_date' in df.columns:
            df['scheduled_date'] = pd.to_datetime(df['scheduled_date'])
        if 'actual_date' in df.columns:
            df['actual_date'] = pd.to_datetime(df['actual_date'])
        return df
