"""
API concrete implementation of the DataSource interface.
Defines the production contract for enterprise REST/GraphQL ERP/WMS connectors
while remaining extensible and explicitly identifying connection requirements.
"""

from typing import Optional, Dict, Any, Callable
import pandas as pd
from data_ingestion.base import DataSource


class APIDataSource(DataSource):
    """
    Enterprise API Connector for ERP/WMS systems (SAP, NetSuite, Oracle, etc.).

    Production Contract:
    - Base Endpoint: Configurable HTTPS endpoint URL.
    - Authentication: Bearer token or API key passed in headers.
    - Endpoints:
        GET /demand      -> List[{"sku_id", "date", "quantity_demanded", "location_id"}]
        GET /inventory   -> List[{"sku_id", "current_stock", "reorder_point", "safety_stock", "unit_cost", "lead_time_days", "location_id"}]
        GET /deliveries  -> List[{"delivery_id", "carrier_id", "origin", "destination", "distance_km", "scheduled_date", "actual_date", "is_late", ...}]
    - Serialization: JSON payloads parsed into canonical pandas DataFrames.
    """

    def __init__(
        self,
        api_endpoint: str = "https://api.supplychain.company.com/v1",
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        client: Optional[Callable[[str, Dict[str, str]], Dict[str, Any]]] = None
    ):
        self.api_endpoint = api_endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._client = client  # Injectable HTTP client function (endpoint, headers) -> JSON response

    def _fetch_endpoint(self, endpoint_name: str) -> pd.DataFrame:
        """
        Executes an HTTP request to the API contract endpoint.
        If no active client/credentials are provided, raises NotImplementedError
        explaining the production connection requirements.
        """
        if self._client is not None:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            response_json = self._client(f"{self.api_endpoint}/{endpoint_name}", headers)
            data = response_json.get("data", response_json) if isinstance(response_json, dict) else response_json
            return pd.DataFrame(data)

        # Default stub behavior: explicitly declare the contract and lack of live enterprise credentials
        raise NotImplementedError(
            f"API endpoint '{self.api_endpoint}/{endpoint_name}' requires live ERP/WMS enterprise credentials. "
            f"Production contract: Pass an authenticated client or set live enterprise credentials in configuration."
        )

    def load_historical_demand(self) -> pd.DataFrame:
        df = self._fetch_endpoint("demand")
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def load_inventory_snapshot(self) -> pd.DataFrame:
        return self._fetch_endpoint("inventory")

    def load_deliveries(self) -> pd.DataFrame:
        df = self._fetch_endpoint("deliveries")
        if not df.empty:
            if "scheduled_date" in df.columns:
                df["scheduled_date"] = pd.to_datetime(df["scheduled_date"])
            if "actual_date" in df.columns:
                df["actual_date"] = pd.to_datetime(df["actual_date"])
        return df
