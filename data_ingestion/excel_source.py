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

    def __init__(self, excel_path: str = os.path.join("data", "supplychain_data.xlsx"), sheet_mapping: dict = None):
        self.excel_path = excel_path
        self.sheet_mapping = sheet_mapping or {}

    def load_historical_demand(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        sheet_name = self.sheet_mapping.get("historical_demand", "historical_demand")
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
        df = df.dropna(how="all").reset_index(drop=True)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, format='mixed')
        return df

    def load_inventory_snapshot(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        sheet_name = self.sheet_mapping.get("inventory_snapshot", "inventory_snapshot")
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
        return df.dropna(how="all").reset_index(drop=True)

    def load_deliveries(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at: {self.excel_path}")
        sheet_name = self.sheet_mapping.get("deliveries", "deliveries")
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
        df = df.dropna(how="all").reset_index(drop=True)
        if 'scheduled_date' in df.columns:
            df['scheduled_date'] = pd.to_datetime(df['scheduled_date'], dayfirst=True, format='mixed')
        if 'actual_date' in df.columns:
            df['actual_date'] = pd.to_datetime(df['actual_date'], dayfirst=True, format='mixed')
        return df
