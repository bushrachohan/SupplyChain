"""
core/simulation.py
What-If Simulation Logic for Phase 4.

Calculates before/after states for business metrics using existing core/* modules.
Does not invent numbers; reuses actual model outputs.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import lightgbm as lgb
from copy import deepcopy

from core.inventory_risk import evaluate_sku_risk, InventoryRiskResult
from core.delivery_risk import predict_delivery_risk
from core.logistics_optimizer import optimize_routes


def simulate_inventory_scenario(
    sku_id: str,
    base_current_stock: float,
    base_avg_daily_demand: float,
    base_forecast_demand: float,
    base_forecast_period_days: int,
    base_lead_time_days: float,
    base_safety_stock_days: float = 14.0,
    demand_multiplier: float = 1.0,
    stock_override: Optional[float] = None,
    lead_time_override: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run a before/after simulation for inventory risk by applying overrides.
    """
    # Calculate Before
    before_result = evaluate_sku_risk(
        sku_id=sku_id,
        current_stock=base_current_stock,
        avg_daily_demand=base_avg_daily_demand,
        forecasted_demand_next_period=base_forecast_demand,
        forecast_period_days=base_forecast_period_days,
        lead_time_days=base_lead_time_days,
        safety_stock_days=base_safety_stock_days
    )

    # Apply Overrides
    after_stock = stock_override if stock_override is not None else base_current_stock
    after_lead_time = lead_time_override if lead_time_override is not None else base_lead_time_days
    
    after_forecast_demand = base_forecast_demand * demand_multiplier
    after_avg_daily_demand = base_avg_daily_demand * demand_multiplier

    # Calculate After
    after_result = evaluate_sku_risk(
        sku_id=sku_id,
        current_stock=after_stock,
        avg_daily_demand=after_avg_daily_demand,
        forecasted_demand_next_period=after_forecast_demand,
        forecast_period_days=base_forecast_period_days,
        lead_time_days=after_lead_time,
        safety_stock_days=base_safety_stock_days
    )

    return {
        "sku_id": sku_id,
        "before": before_result.to_dict(),
        "after": after_result.to_dict(),
        "deltas": {
            "days_of_supply_delta": round(after_result.days_of_supply - before_result.days_of_supply, 2),
            "reorder_point_delta": round(after_result.reorder_point_units - before_result.reorder_point_units, 2),
            "risk_level_changed": before_result.risk_level != after_result.risk_level
        }
    }


def simulate_delivery_scenario(
    model: lgb.LGBMClassifier,
    df_deliveries: pd.DataFrame,
    delivery_id: str,
    traffic_delay_override: Optional[float] = None,
    weather_condition_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a before/after simulation for delivery risk by applying overrides to the dataframe.
    """
    # Calculate Before
    before_result = predict_delivery_risk(model, df_deliveries, delivery_id)
    
    # Create altered dataframe for After
    df_altered = df_deliveries.copy()
    row_idx = df_altered.index[df_altered["delivery_id"] == delivery_id].tolist()
    if not row_idx:
        raise ValueError(f"Delivery ID {delivery_id} not found in dataframe.")
    
    idx = row_idx[0]
    if traffic_delay_override is not None:
        df_altered.at[idx, "traffic_delay_hrs"] = traffic_delay_override
        
    if weather_condition_override is not None:
        df_altered.at[idx, "weather_condition"] = weather_condition_override

    # Calculate After
    after_result = predict_delivery_risk(model, df_altered, delivery_id)
    
    return {
        "delivery_id": delivery_id,
        "before": before_result,
        "after": after_result,
        "deltas": {
            "risk_score_delta": round(after_result["risk_score"] - before_result["risk_score"], 4),
            "risk_label_changed": before_result["risk_label"] != after_result["risk_label"]
        }
    }


def simulate_logistics_scenario(
    delivery_ids: List[str],
    df_deliveries: List[Dict[str, Any]],
    base_vehicle_constraints: Dict[str, Any],
    capacity_multiplier: float = 1.0,
    num_vehicles_override: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a before/after simulation for logistics optimization by altering vehicle constraints.
    """
    # Calculate Before
    before_result = optimize_routes(delivery_ids, base_vehicle_constraints, df_deliveries)
    
    # Apply Overrides
    after_constraints = deepcopy(base_vehicle_constraints)
    if num_vehicles_override is not None:
        after_constraints["num_vehicles"] = num_vehicles_override
        
    if capacity_multiplier != 1.0:
        after_constraints["capacities"] = [int(c * capacity_multiplier) for c in after_constraints["capacities"]]
        
    # Calculate After
    after_result = optimize_routes(delivery_ids, after_constraints, df_deliveries)
    
    before_dist = before_result.get("total_distance_km", before_result.get("total_distance", 0))
    after_dist = after_result.get("total_distance_km", after_result.get("total_distance", 0))
    before_cost = before_result.get("total_cost", 0)
    after_cost = after_result.get("total_cost", 0)

    return {
        "before": before_result,
        "after": after_result,
        "deltas": {
            "total_distance_delta": round(after_dist - before_dist, 2),
            "total_cost_delta": round(after_cost - before_cost, 2)
        }
    }
