import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from core.inventory_risk import RiskLevel
from core.simulation import (
    simulate_inventory_scenario,
    simulate_delivery_scenario,
    simulate_logistics_scenario
)

def test_simulate_inventory_scenario():
    result = simulate_inventory_scenario(
        sku_id="SKU-123",
        base_current_stock=200.0,
        base_avg_daily_demand=10.0,
        base_forecast_demand=140.0,
        base_forecast_period_days=14,
        base_lead_time_days=5.0,
        base_safety_stock_days=14.0,
        demand_multiplier=3.0,  # 3x demand -> DOS drops
    )
    
    assert result["sku_id"] == "SKU-123"
    assert result["deltas"]["days_of_supply_delta"] < 0
    # Before: stock=200, daily=10, DOS=20. Lead time=5, Safety=14. Reorder = 190. Stock > Reorder -> NORMAL
    # After: daily=30, DOS=6.66. Reorder = 5*30 + 14*30 = 570. Stock < 570 -> STOCKOUT_RISK
    assert result["before"]["risk_level"] == RiskLevel.NORMAL.value
    assert result["after"]["risk_level"] == RiskLevel.STOCKOUT_RISK.value
    assert result["deltas"]["risk_level_changed"] is True


@patch("core.simulation.predict_delivery_risk")
def test_simulate_delivery_scenario(mock_predict):
    # Mock predict_delivery_risk to return predefined results based on dataframe content
    def side_effect(model, df, delivery_id):
        traffic = df.loc[df["delivery_id"] == delivery_id, "traffic_delay_hrs"].iloc[0]
        score = 0.2 + (0.5 if traffic > 5 else 0.0)
        label = "high" if score > 0.5 else "low"
        return {"delivery_id": delivery_id, "risk_score": score, "risk_label": label}
        
    mock_predict.side_effect = side_effect
    
    df = pd.DataFrame({
        "delivery_id": ["DEL-1"],
        "traffic_delay_hrs": [1.0],
        "weather_condition": ["Clear"]
    })
    
    mock_model = MagicMock()
    
    result = simulate_delivery_scenario(
        model=mock_model,
        df_deliveries=df,
        delivery_id="DEL-1",
        traffic_delay_override=10.0  # Should trigger high risk based on mock
    )
    
    assert result["delivery_id"] == "DEL-1"
    assert result["before"]["risk_label"] == "low"
    assert result["after"]["risk_label"] == "high"
    assert result["deltas"]["risk_label_changed"] is True
    assert result["deltas"]["risk_score_delta"] > 0


def test_simulate_logistics_scenario():
    delivery_ids = ["D1", "D2"]
    base_constraints = {"num_vehicles": 2, "capacities": [1000, 1000]}
    df_deliveries = [
        {"delivery_id": "D1", "distance_km": 50, "weight": 100},
        {"delivery_id": "D2", "distance_km": 100, "weight": 200}
    ]
    
    result = simulate_logistics_scenario(
        delivery_ids=delivery_ids,
        df_deliveries=df_deliveries,
        base_vehicle_constraints=base_constraints,
        capacity_multiplier=0.5,
        num_vehicles_override=3
    )
    
    assert "before" in result
    assert "after" in result
    assert "total_distance_delta" in result["deltas"]
    assert "total_cost_delta" in result["deltas"]
