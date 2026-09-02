"""
Abstract base class for data sources in SupplyChain Sentinel AI.
Provides a pluggable interface for loading demand, inventory, and delivery data.
"""

from abc import ABC, abstractmethod
import pandas as pd


class DataSource(ABC):
    """
    Abstract interface for loading data into the supply chain platform.
    Concrete implementations (CSV, Excel, DB, API) must implement all abstract methods.
    """

    @abstractmethod
    def load_historical_demand(self) -> pd.DataFrame:
        """
        Loads historical demand data.
        Returns a DataFrame with columns: ['sku_id', 'date', 'quantity_demanded', 'location_id']
        """
        pass

    @abstractmethod
    def load_inventory_snapshot(self) -> pd.DataFrame:
        """
        Loads current inventory status.
        Returns a DataFrame with columns: ['sku_id', 'current_stock', 'reorder_point', 'safety_stock', 'unit_cost', 'lead_time_days', 'location_id']
        """
        pass

    @abstractmethod
    def load_deliveries(self) -> pd.DataFrame:
        """
        Loads delivery history and status.
        Returns a DataFrame with columns: ['delivery_id', 'carrier_id', 'origin', 'destination', 'distance_km', 'scheduled_date', 'actual_date', 'is_late', 'weather_condition', 'traffic_delay_hrs']
        """
        pass
