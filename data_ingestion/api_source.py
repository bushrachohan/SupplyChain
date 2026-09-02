"""
API concrete implementation stub of the DataSource interface.
Demonstrates the shape a future enterprise REST/GraphQL API connector takes for real company integration.
"""

import pandas as pd
from data_ingestion.base import DataSource


class APIDataSource(DataSource):
    """
    Extensible connector interface for enterprise ERP/WMS API integration.
    """

    def __init__(self, api_endpoint: str = "https://api.supplychain.company.com/v1", api_key: str = None):
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def load_historical_demand(self) -> pd.DataFrame:
        # In a live deployment, this makes HTTP GET requests to endpoint
        # e.g., response = requests.get(f"{self.api_endpoint}/demand", headers=...)
        # For current interface demonstration:
        raise NotImplementedError("API integration endpoint is a stub for future live enterprise connection.")

    def load_inventory_snapshot(self) -> pd.DataFrame:
        raise NotImplementedError("API integration endpoint is a stub for future live enterprise connection.")

    def load_deliveries(self) -> pd.DataFrame:
        raise NotImplementedError("API integration endpoint is a stub for future live enterprise connection.")
