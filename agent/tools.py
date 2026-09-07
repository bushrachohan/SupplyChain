"""
agent/tools.py
Tool wrappers and Groq function-calling schemas for the AI Decision Agent.
"""

import pandas as pd
from typing import List, Dict, Any

from data_ingestion.csv_source import CSVDataSource
from core.forecasting import train_forecast_model, predict_demand
from core.inventory_risk import evaluate_sku_risk
from core.delivery_risk import train_delivery_risk_model, predict_delivery_risk
from core.logistics_optimizer import optimize_routes as core_optimize_routes
from core.rag import retrieve_policies as core_retrieve_policies

# Initialize data sources and models (lazy loading for MVP)
_source = CSVDataSource(data_dir="data")
_demand_df = None
_forecast_model = None
_deliveries_df = None
_delivery_model = None
_inventory_df = None

def _get_demand_model():
    global _demand_df, _forecast_model
    if _forecast_model is None:
        _demand_df = _source.load_historical_demand()
        _forecast_model, _, _ = train_forecast_model(_demand_df)
    return _forecast_model, _demand_df

def _get_delivery_model():
    global _deliveries_df, _delivery_model
    if _delivery_model is None:
        _deliveries_df = _source.load_deliveries()
        _delivery_model, _, _ = train_delivery_risk_model(_deliveries_df)
    return _delivery_model, _deliveries_df

def _get_inventory_df():
    global _inventory_df
    if _inventory_df is None:
        _inventory_df = _source.load_inventory_snapshot()
    return _inventory_df

# ---------------------------------------------------------------------------
# Tool Execution Wrappers
# ---------------------------------------------------------------------------

def get_demand_forecast(sku_id: str) -> Dict[str, Any]:
    """Get the demand forecast for a specific SKU."""
    model, df = _get_demand_model()
    try:
        preds = predict_demand(model, df, sku_id)
        # Return summary
        return {
            "sku_id": sku_id,
            "forecast_horizon_weeks": len(preds),
            "predicted_quantities": preds["predicted_demand"].tolist()
        }
    except Exception as e:
        return {"error": str(e)}

def get_inventory_risk(sku_id: str) -> Dict[str, Any]:
    """Assess the inventory risk (stockout/overstock) for a specific SKU."""
    inv_df = _get_inventory_df()
    sku_inv = inv_df[inv_df["sku_id"] == sku_id]
    if sku_inv.empty:
        return {"error": f"SKU {sku_id} not found in inventory."}
    
    sku_row = sku_inv.iloc[0]
    
    # We need forecast for this SKU. Let's mock a simple future demand based on forecast
    try:
        forecast = get_demand_forecast(sku_id)
        # forecast returns weekly demand. Let's assume forecast_horizon_weeks is returned
        weeks = max(1, forecast.get("forecast_horizon_weeks", 1))
        forecasted_demand = sum(forecast.get("predicted_quantities", [0]))
        avg_daily_demand = forecasted_demand / (weeks * 7)
    except:
        forecasted_demand = 0.0
        avg_daily_demand = 0.0
        weeks = 1
        
    risk = evaluate_sku_risk(
        sku_id=sku_id,
        current_stock=sku_row["current_stock"],
        avg_daily_demand=avg_daily_demand,
        forecasted_demand_next_period=forecasted_demand,
        forecast_period_days=weeks * 7,
        lead_time_days=sku_row["lead_time_days"],
        safety_stock_days=14.0 # default
    )
    return risk.to_dict()

def get_delivery_risk(delivery_id: str) -> Dict[str, Any]:
    """Predict if a specific delivery will be late and return risk drivers."""
    model, df = _get_delivery_model()
    try:
        risk = predict_delivery_risk(model, df, delivery_id)
        return risk
    except Exception as e:
        return {"error": str(e)}

def optimize_routes(delivery_ids: List[str], vehicle_constraints: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize vehicle routes for a set of deliveries."""
    _, df = _get_delivery_model()
    # Convert dataframe to list of dicts
    deliveries_list = df.to_dict(orient="records")
    return core_optimize_routes(delivery_ids, vehicle_constraints, df_deliveries=deliveries_list)

def retrieve_policies(query: str) -> List[Dict[str, Any]]:
    """Retrieve relevant business policies using RAG."""
    # This calls core.rag.retrieve_policies which uses ChromaDB
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
            "description": "Get the predicted future demand quantities for a specific SKU. Use this to check if demand is unexpectedly high or low.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {
                        "type": "string",
                        "description": "The ID of the SKU, e.g., SKU_101"
                    }
                },
                "required": ["sku_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_inventory_risk",
            "description": "Evaluate the risk of stockout or overstock for a specific SKU based on current stock, safety stock policies, and lead time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {
                        "type": "string",
                        "description": "The ID of the SKU, e.g., SKU_101"
                    }
                },
                "required": ["sku_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_delivery_risk",
            "description": "Predict the risk of a delivery arriving late and return the top contributing factors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delivery_id": {
                        "type": "string",
                        "description": "The ID of the delivery, e.g., DEL_001"
                    }
                },
                "required": ["delivery_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_routes",
            "description": "Optimize logistics routes for a set of deliveries, given vehicle constraints (number of vehicles and capacity).",
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
            "description": "Search and retrieve business, procurement, and logistics policies relevant to the current situation to ensure constraints are respected.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, e.g., 'safety stock rules for Tier 1 SKUs' or 'carrier late delivery policy'"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Map of tool names to functions for dynamic execution
TOOL_FUNCTIONS = {
    "get_demand_forecast": get_demand_forecast,
    "get_inventory_risk": get_inventory_risk,
    "get_delivery_risk": get_delivery_risk,
    "optimize_routes": optimize_routes,
    "retrieve_policies": retrieve_policies,
}
