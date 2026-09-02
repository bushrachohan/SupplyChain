"""
Excel concrete implementation of the DataSource interface.
Loads demand, inventory, and delivery data from Excel workbook sheets.
"""

import os
import pandas as pd
from data_ingestion.base import DataSource


class ExcelDataSource(DataSource):
    """
    Concrete data source reading from Excel workbook sheets.
    """

    def __init__(self, excel_path: str = os.path.join("data", "supplychain_data.xlsx")):
        self.excel_path = excel_path

    def load_historical_demand(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        df = pd.read_excel(self.excel_path, sheet_name="historical_demand")
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df

    def load_inventory_snapshot(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        return pd.read_excel(self.excel_path, sheet_name="inventory_snapshot")

    def load_deliveries(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        df = pd.read_excel(self.excel_path, sheet_name="deliveries")
        if 'scheduled_date' in df.columns:
            df['scheduled_date'] = pd.to_datetime(df['scheduled_date'])
        if 'actual_date' in df.columns:
            df['actual_date'] = pd.to_datetime(df['actual_date'])
        return df
