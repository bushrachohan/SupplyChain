"""
tests/test_inventory_risk.py

Per Section 9 (Testing Strategy): known input -> expected risk flag.
Per Definition of Done (15.10): real test input used, errors/invalid
inputs handled, output correct and explainable.
"""

import pandas as pd
import pytest

from core.inventory_risk import (
    RiskLevel,
    evaluate_portfolio_risk,
    evaluate_sku_risk,
)


def test_stockout_risk_flagged_when_stock_below_reorder_point():
    result = evaluate_sku_risk(
        sku_id="SKU-LOW",
        current_stock=20,
        avg_daily_demand=10,
        forecasted_demand_next_period=70,  # 10/day over 7 days
        forecast_period_days=7,
        lead_time_days=10,
        safety_stock_days=14,
    )
    assert result.risk_level == RiskLevel.STOCKOUT_RISK
    assert "low_stock_level" in result.contributing_factors


def test_overstock_risk_flagged_when_stock_far_exceeds_demand():
    result = evaluate_sku_risk(
        sku_id="SKU-HIGH",
        current_stock=5000,
        avg_daily_demand=5,
        forecasted_demand_next_period=35,  # 5/day over 7 days
        forecast_period_days=7,
        lead_time_days=5,
        safety_stock_days=14,
    )
    assert result.risk_level == RiskLevel.OVERSTOCK_RISK
    assert "excess_stock_vs_demand" in result.contributing_factors


def test_normal_risk_when_stock_is_well_balanced():
    result = evaluate_sku_risk(
        sku_id="SKU-OK",
        current_stock=250,
        avg_daily_demand=10,
        forecasted_demand_next_period=70,  # 10/day over 7 days, matches history
        forecast_period_days=7,
        lead_time_days=5,
        safety_stock_days=14,
    )
    assert result.risk_level == RiskLevel.NORMAL
    assert result.contributing_factors == {}


def test_demand_spike_is_captured_as_a_contributing_factor():
    result = evaluate_sku_risk(
        sku_id="SKU-SPIKE",
        current_stock=80,
        avg_daily_demand=10,
        forecasted_demand_next_period=140,  # 20/day forecast vs 10/day historical
        forecast_period_days=7,
        lead_time_days=5,
        safety_stock_days=14,
    )
    assert "demand_spike_vs_history" in result.contributing_factors


def test_invalid_forecast_period_raises():
    with pytest.raises(ValueError):
        evaluate_sku_risk(
            sku_id="SKU-BAD",
            current_stock=10,
            avg_daily_demand=5,
            forecasted_demand_next_period=10,
            forecast_period_days=0,
            lead_time_days=5,
        )


def test_negative_stock_raises():
    with pytest.raises(ValueError):
        evaluate_sku_risk(
            sku_id="SKU-BAD2",
            current_stock=-1,
            avg_daily_demand=5,
            forecasted_demand_next_period=10,
            forecast_period_days=7,
            lead_time_days=5,
        )


def test_zero_avg_daily_demand_does_not_crash():
    # Edge case: brand-new SKU with no historical demand yet.
    result = evaluate_sku_risk(
        sku_id="SKU-NEW",
        current_stock=100,
        avg_daily_demand=0,
        forecasted_demand_next_period=70,
        forecast_period_days=7,
        lead_time_days=5,
        safety_stock_days=14,
    )
    assert result.risk_level in {RiskLevel.STOCKOUT_RISK, RiskLevel.OVERSTOCK_RISK, RiskLevel.NORMAL}


def test_evaluate_portfolio_risk_batch_runs_over_dataframe():
    df = pd.DataFrame(
        [
            {
                "sku_id": "SKU-A",
                "current_stock": 20,
                "avg_daily_demand": 10,
                "forecasted_demand_next_period": 70,
                "forecast_period_days": 7,
                "lead_time_days": 10,
            },
            {
                "sku_id": "SKU-B",
                "current_stock": 5000,
                "avg_daily_demand": 5,
                "forecasted_demand_next_period": 35,
                "forecast_period_days": 7,
                "lead_time_days": 5,
            },
        ]
    )
    result_df = evaluate_portfolio_risk(df)
    assert len(result_df) == 2
    assert set(result_df["sku_id"]) == {"SKU-A", "SKU-B"}
    assert "risk_level" in result_df.columns
    assert result_df.loc[result_df["sku_id"] == "SKU-A", "risk_level"].iloc[0] == "STOCKOUT_RISK"
    assert result_df.loc[result_df["sku_id"] == "SKU-B", "risk_level"].iloc[0] == "OVERSTOCK_RISK"


def test_evaluate_portfolio_risk_missing_column_raises():
    df = pd.DataFrame([{"sku_id": "SKU-X", "current_stock": 10}])
    with pytest.raises(ValueError):
        evaluate_portfolio_risk(df)
