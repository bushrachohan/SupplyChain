"""
ActiveDataset context for managing the globally selected business dataset.
Ensures the backend does not silently fall back to synthetic data.
"""

from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
import pandas as pd

from data_ingestion.base import DataSource


@dataclass
class DatasetMetadata:
    source_type: str  # e.g., 'csv', 'excel', 'db', 'api'
    name: str         # e.g., 'Q3 Business Data'
    status: str       # Lifecycle state: 'uploaded/connected', 'validated', 'active', 'failed', 'replaced'
    connected_at: str
    details: Dict[str, Any] = field(default_factory=dict)


class ActiveDatasetContext:
    """
    Holds the currently active dataset and its metadata.
    This prevents hardcoding synthetic datasets across the pipeline.
    """
    def __init__(self):
        self._source: Optional[DataSource] = None
        self._metadata: Optional[DatasetMetadata] = None
        self._listeners: List[Callable[[], None]] = []

    @property
    def is_active(self) -> bool:
        """Returns True if an active dataset source is loaded and marked 'active'."""
        return self._source is not None and self._metadata is not None and self._metadata.status == "active"

    def subscribe(self, listener: Callable[[], None]) -> None:
        """Register a callback to be called when the active dataset changes, is cleared, or replaced."""
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[], None]) -> None:
        """Remove a previously registered listener callback."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify(self) -> None:
        """Notify all registered listeners that dataset state changed (e.g. for cache invalidation)."""
        for listener in self._listeners:
            try:
                listener()
            except Exception:
                pass

    def set_active(self, source: DataSource, metadata: DatasetMetadata) -> None:
        """Sets the active data source and its metadata, notifying listeners."""
        self._source = source
        self._metadata = metadata
        self._notify()

    def get_source(self) -> DataSource:
        """Returns the active data source. Raises ValueError if none is active."""
        if self._source is None:
            raise ValueError("No active dataset configured. Please select or connect a business dataset.")
        return self._source

    def get_metadata(self) -> DatasetMetadata:
        """Returns the active dataset's metadata."""
        if self._metadata is None:
            raise ValueError("No active dataset metadata configured.")
        return self._metadata

    def update_status(self, new_status: str) -> None:
        """Updates the status of the current active dataset."""
        if self._metadata is None:
            raise ValueError("Cannot update status: No active dataset configured.")
        valid_states = ["uploaded/connected", "validated", "active", "failed", "replaced"]
        if new_status not in valid_states:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of {valid_states}.")
        self._metadata.status = new_status
        self._notify()

    def clear(self) -> None:
        """Clears the active dataset and notifies listeners to invalidate derived results."""
        if self._metadata:
            self._metadata.status = "replaced"
        self._source = None
        self._metadata = None
        self._notify()

    def load_historical_demand(self) -> pd.DataFrame:
        """Convenience delegate to the active DataSource."""
        return self.get_source().load_historical_demand()

    def load_inventory_snapshot(self) -> pd.DataFrame:
        """Convenience delegate to the active DataSource."""
        return self.get_source().load_inventory_snapshot()

    def load_deliveries(self) -> pd.DataFrame:
        """Convenience delegate to the active DataSource."""
        return self.get_source().load_deliveries()


# Global context instance to be used by backend services
active_dataset = ActiveDatasetContext()
