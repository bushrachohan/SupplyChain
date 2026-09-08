"""
agent/tools.py
Tool wrappers and Groq function-calling schemas for the AI Decision Agent.
Uses the Active Dataset architecture for safe, session-aware data access.
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timezone

from data_ingestion.base import DataSource
from data_ingestion.active_dataset import active_dataset, DatasetMetadata
from data_ingestion.csv_source import CSVDataSource
from core.forecasting import train_forecast_model, predict_demand
from core.inventory_risk import evaluate_sku_risk
from core.delivery_risk import train_delivery_risk_model, predict_delivery_risk
from core.logistics_optimizer import optimize_routes as core_optimize_routes
from core.rag import retrieve_policies as core_retrieve_policies

# Cached models and DataFrames (lazy-loaded and automatically invalidated on active dataset change)
_demand_df = None
_forecast_model = None
_deliveries_df = None
_delivery_model = None
_inventory_df = None

def _invalidate_caches():
    """Reset cached models and DataFrames when the active dataset changes or is cleared."""
    global _demand_df, _forecast_model, _deliveries_df, _delivery_model, _inventory_df
    _demand_df = None
    _forecast_model = None
    _deliveries_df = None
    _delivery_model = None
    _inventory_df = None

# Register cache invalidation hook
active_dataset.subscribe(_invalidate_caches)

def set_active_datasource(source: Any, name: str = "Active Business Dataset") -> None:
    """
    Sets the active DataSource on the global active_dataset context,
    automatically invalidating caches and synchronizing with ActiveDatasetContext.
    """
    source_type = "csv"
    if hasattr(source, "excel_path"):
        source_type = "excel"
    elif hasattr(source, "engine") or hasattr(source, "connection_url"):
        source_type = "db"
    elif hasattr(source, "api_endpoint"):
        source_type = "api"

    meta = DatasetMetadata(
        source_type=source_type,
        name=name,
        status="active",
        connected_at=datetime.now(timezone.utc).isoformat()
    )
    active_dataset.set_active(source, meta)

def _get_active_source():
    """
    Returns the configured business dataset. If no dataset is active yet,
    initializes the default bundled CSV source explicitly into the context.
    """
    try:
        return active_dataset.get_source()
    except ValueError:
        default_source = CSVDataSource(data_dir="data")
        default_meta = DatasetMetadata(
            source_type="csv",
            name="Default Bundled CSV Data",
            status="active",
            connected_at=datetime.now(timezone.utc).isoformat()
        )
        active_dataset.set_active(default_source, default_meta)
        return active_dataset.get_source()

def _get_demand_model():
    global _demand_df, _forecast_model
    if _forecast_model is None:
        source = _get_active_source()
        _demand_df = source.load_historical_demand()
        _forecast_model, _, _ = train_forecast_model(_demand_df)
    return _forecast_model, _demand_df

def _get_delivery_model():
    global _deliveries_df, _delivery_model
    if _delivery_model is None:
        source = _get_active_source()
        _deliveries_df = source.load_deliveries()
        _delivery_model, _, _ = train_delivery_risk_model(_deliveries_df)
    return _delivery_model, _deliveries_df

def _get_inventory_df():
    global _inventory_df
    if _inventory_df is None:
        source = _get_active_source()
        _inventory_df = source.load_inventory_snapshot()
    return _inventory_df

# ---------------------------------------------------------------------------
# Tool Execution Wrappers
# ---------------------------------------------------------------------------

def get_demand_forecast(sku_id: str) -> Dict[str, Any]:
    """Get the demand forecast for a specific SKU."""
    model, df = _get_demand_model()
    try:
        preds = predict_demand(model, df, sku_id)
        num_days = len(preds)
        return {
            "sku_id": sku_id,
            "forecast_horizon_days": num_days,
            "forecast_horizon_weeks": max(1, round(num_days / 7.0)),
            "predicted_quantities": preds["predicted_demand"].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

def get_inventory_risk(sku_id: str) -> Dict[str, Any]:
    """Assess the inventory risk (stockout/overstock) for a specific SKU."""
    try:
        inv_df = _get_inventory_df()
        sku_inv = inv_df[inv_df["sku_id"] == sku_id]
        if sku_inv.empty:
            return {"error": f"SKU {sku_id} not found in inventory."}
        
        sku_row = sku_inv.iloc[0]
        
        # We need forecast for this SKU
        try:
            forecast = get_demand_forecast(sku_id)
            forecast_period_days = forecast.get("forecast_horizon_days", len(forecast.get("predicted_quantities", [0])))
            forecasted_demand = sum(forecast.get("predicted_quantities", [0]))
            avg_daily_demand = forecasted_demand / max(1, forecast_period_days)
        except:
            forecasted_demand = 0.0
            avg_daily_demand = 0.0
            forecast_period_days = 1
            
        risk = evaluate_sku_risk(
            sku_id=sku_id,
            current_stock=sku_row["current_stock"],
            avg_daily_demand=avg_daily_demand,
            forecasted_demand_next_period=forecasted_demand,
            forecast_period_days=forecast_period_days,
            lead_time_days=sku_row["lead_time_days"],
            safety_stock_days=14.0
        )
        return risk.to_dict()
    except Exception as e:
        return {"error": str(e)}

def get_delivery_risk(delivery_id: str) -> Dict[str, Any]:
    """Predict if a specific delivery will be late and return risk drivers."""
    try:
        model, df = _get_delivery_model()
        risk = predict_delivery_risk(model, df, delivery_id)
        return risk
    except Exception as e:
        return {"error": str(e)}

def optimize_routes(delivery_ids: List[str], vehicle_constraints: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize vehicle routes for a set of deliveries."""
    try:
        _, df = _get_delivery_model()
        deliveries_list = df.to_dict(orient="records")
        return core_optimize_routes(delivery_ids, vehicle_constraints, df_deliveries=deliveries_list)
    except Exception as e:
        return {"error": str(e)}

def retrieve_policies(query: str) -> List[Dict[str, Any]]:
    """Retrieve relevant business policies using RAG."""
    try:
        return core_retrieve_policies(query, top_k=3)
    except Exception as e:
        return [{"error": str(e)}]


# ---------------------------------------------------------------------------
# Groq Function Schemas
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_demand_forecast",
            "description": "Get the predicted future demand quantities for a specific SKU.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {"type": "string", "description": "The ID of the SKU, e.g., SKU_101"}
                },
                "required": ["sku_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_inventory_risk",
            "description": "Evaluate the risk of stockout or overstock for a specific SKU based on current stock and safety stock policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {"type": "string", "description": "The ID of the SKU, e.g., SKU_101"}
                },
                "required": ["sku_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_delivery_risk",
            "description": "Predict the risk of a delivery arriving late and return top contributing factors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delivery_id": {"type": "string", "description": "The ID of the delivery, e.g., DEL_001"}
                },
                "required": ["delivery_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_routes",
            "description": "Optimize logistics routes for a set of deliveries, given vehicle constraints.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delivery_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of delivery IDs to route."
                    },
                    "vehicle_constraints": {
                        "type": "object",
                        "properties": {
                            "num_vehicles": {"type": "integer", "description": "Number of available vehicles"},
                            "capacities": {
                                "type": "array", 
                                "items": {"type": "integer"}, 
                                "description": "Capacity of each vehicle"
                            }
                        },
                        "required": ["num_vehicles", "capacities"]
                    }
                },
                "required": ["delivery_ids", "vehicle_constraints"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_policies",
            "description": "Search and retrieve business, procurement, and logistics policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "get_demand_forecast": get_demand_forecast,
    "get_inventory_risk": get_inventory_risk,
    "get_delivery_risk": get_delivery_risk,
    "optimize_routes": optimize_routes,
    "retrieve_policies": retrieve_policies,
}
