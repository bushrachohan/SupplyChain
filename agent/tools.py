"""
agent/tools.py
Tool wrappers and Groq function-calling schemas for the AI Decision Agent.
Updated to use thread-local state for safe concurrent Streamlit sessions.
"""

import pandas as pd
from typing import List, Dict, Any
import threading

from data_ingestion.base import DataSource
from data_ingestion.csv_source import CSVDataSource
from core.forecasting import train_forecast_model, predict_demand
from core.inventory_risk import evaluate_sku_risk
from core.delivery_risk import train_delivery_risk_model, predict_delivery_risk
from core.logistics_optimizer import optimize_routes as core_optimize_routes
from core.rag import retrieve_policies as core_retrieve_policies

# Thread-local state for safe concurrency across Streamlit user sessions
_state = threading.local()

def _get_state():
    """Ensure thread-local state is initialized with the default demo source."""
    if not hasattr(_state, "source"):
        _state.source = CSVDataSource(data_dir="data")
        _state.demand_df = None
        _state.forecast_model = None
        _state.deliveries_df = None
        _state.delivery_model = None
        _state.inventory_df = None
    return _state

def set_active_datasource(source: DataSource):
    """
    Override the active datasource for the current session/thread.
    Clears all cached models and DataFrames to force a rebuild from the new source.
    """
    state = _get_state()
    state.source = source
    state.demand_df = None
    state.forecast_model = None
    state.deliveries_df = None
    state.delivery_model = None
    state.inventory_df = None

def _get_demand_model():
    state = _get_state()
    if state.forecast_model is None:
        state.demand_df = state.source.load_historical_demand()
        state.forecast_model, _, _ = train_forecast_model(state.demand_df)
    return state.forecast_model, state.demand_df

def _get_delivery_model():
    state = _get_state()
    if state.delivery_model is None:
        state.deliveries_df = state.source.load_deliveries()
        state.delivery_model, _, _ = train_delivery_risk_model(state.deliveries_df)
    return state.delivery_model, state.deliveries_df

def _get_inventory_df():
    state = _get_state()
    if state.inventory_df is None:
        state.inventory_df = state.source.load_inventory_snapshot()
    return state.inventory_df

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
