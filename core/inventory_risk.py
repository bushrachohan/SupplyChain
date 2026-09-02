"""
core/inventory_risk.py

Rule-based inventory risk detection: flags each SKU as STOCKOUT_RISK,
OVERSTOCK_RISK, or NORMAL based on current stock, forecasted demand
(from core/forecasting.py), and lead time.

Design notes (per progress.md rules):
- This module is intentionally rule-based, not an ML model — no train/test
  split or baseline comparison is required for it (that rule applies to
  forecasting.py and delivery_risk.py). It DOES still need standalone
  tests and explainability, per the Build Checklist and Testing Strategy.
- No numbers are invented here beyond straightforward arithmetic on the
  inputs given. This module does not call any LLM.
- Expected upstream input: forecasted_demand should come from
  core/forecasting.py's output for the SKU's next period. If your
  forecasting.py uses different column names when you wire this into a
  DataFrame pipeline, adjust `evaluate_portfolio_risk`'s column mapping
  accordingly — the per-SKU function `evaluate_sku_risk` is
  column-agnostic (plain arguments).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pandas as pd


class RiskLevel(str, Enum):
    STOCKOUT_RISK = "STOCKOUT_RISK"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"
    NORMAL = "NORMAL"


@dataclass
class InventoryRiskResult:
    sku_id: str
    risk_level: RiskLevel
    days_of_supply: float
    reorder_point_units: float
    safety_stock_units: float
    contributing_factors: dict = field(default_factory=dict)
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "sku_id": self.sku_id,
            "risk_level": self.risk_level.value,
            "days_of_supply": round(self.days_of_supply, 2),
            "reorder_point_units": round(self.reorder_point_units, 2),
            "safety_stock_units": round(self.safety_stock_units, 2),
            "contributing_factors": self.contributing_factors,
            "detail": self.detail,
        }


def evaluate_sku_risk(
    sku_id: str,
    current_stock: float,
    avg_daily_demand: float,
    forecasted_demand_next_period: float,
    forecast_period_days: int,
    lead_time_days: float,
    safety_stock_days: float = 14.0,
    overstock_multiplier: float = 3.0,
) -> InventoryRiskResult:
    """
    Evaluate stockout/overstock risk for a single SKU.

    Args:
        sku_id: SKU identifier.
        current_stock: units currently on hand.
        avg_daily_demand: historical average daily demand (units/day).
        forecasted_demand_next_period: total forecasted demand over the
            next `forecast_period_days`, as produced by core/forecasting.py.
        forecast_period_days: length of the forecast horizon in days
            (must be > 0).
        lead_time_days: supplier lead time in days.
        safety_stock_days: policy-driven buffer, in days of demand
            (default 14 — override per policy from core/rag.py if available).
        overstock_multiplier: a SKU is flagged OVERSTOCK_RISK if days of
            supply on hand exceeds overstock_multiplier x reorder point
            (in days). Default 3.0x.

    Returns:
        InventoryRiskResult with risk_level and explainability breakdown.

    Raises:
        ValueError: on invalid (negative or zero-where-required) inputs.
    """
    if forecast_period_days <= 0:
        raise ValueError("forecast_period_days must be > 0")
    if current_stock < 0 or avg_daily_demand < 0 or forecasted_demand_next_period < 0:
        raise ValueError("stock and demand values must be non-negative")
    if lead_time_days < 0 or safety_stock_days < 0:
        raise ValueError("lead_time_days and safety_stock_days must be non-negative")

    # Blend historical average and forecasted demand into a single
    # forward-looking daily demand rate. Forecast is weighted higher since
    # it reflects trend/seasonality; historical avg guards against a
    # single noisy forecast period.
    forecast_daily_demand = forecasted_demand_next_period / forecast_period_days
    projected_daily_demand = (0.7 * forecast_daily_demand) + (0.3 * avg_daily_demand)

    safety_stock_units = projected_daily_demand * safety_stock_days
    reorder_point_units = (projected_daily_demand * lead_time_days) + safety_stock_units

    days_of_supply = (
        current_stock / projected_daily_demand
        if projected_daily_demand > 0
        else float("inf")
    )

    # --- Contributing factors (feature-importance-style explainability) ---
    # Each factor is a normalized 0-1 signal of how much it's driving risk.
    stock_gap = reorder_point_units - current_stock  # positive => below reorder point
    demand_spike_ratio = (
        forecast_daily_demand / avg_daily_demand if avg_daily_demand > 0 else 1.0
    )

    factors = {}

    if stock_gap > 0:
        factors["low_stock_level"] = round(
            min(stock_gap / max(reorder_point_units, 1e-9), 1.0), 3
        )
    if demand_spike_ratio > 1.15:
        factors["demand_spike_vs_history"] = round(
            min((demand_spike_ratio - 1.0), 1.0), 3
        )
    if lead_time_days * projected_daily_demand > safety_stock_units:
        factors["long_lead_time_relative_to_buffer"] = round(
            min(
                (lead_time_days * projected_daily_demand)
                / max(safety_stock_units, 1e-9)
                - 1.0,
                1.0,
            ),
            3,
        )

    overstock_threshold_days = (
        (reorder_point_units / projected_daily_demand) * overstock_multiplier
        if projected_daily_demand > 0
        else float("inf")
    )

    if projected_daily_demand > 0 and current_stock > overstock_threshold_days * projected_daily_demand:
        factors["excess_stock_vs_demand"] = round(
            min((days_of_supply / max(overstock_threshold_days, 1e-9)) - 1.0, 1.0), 3
        )

    # --- Risk classification ---
    if current_stock < reorder_point_units:
        risk_level = RiskLevel.STOCKOUT_RISK
        detail = (
            f"Projected stock ({current_stock:.0f} units) is below the reorder "
            f"point ({reorder_point_units:.0f} units needed to cover lead time "
            f"+ safety stock)."
        )
    elif projected_daily_demand > 0 and current_stock > overstock_threshold_days * projected_daily_demand:
        risk_level = RiskLevel.OVERSTOCK_RISK
        detail = (
            f"Stock on hand covers {days_of_supply:.0f} days of projected demand, "
            f"more than {overstock_multiplier}x the reorder cycle."
        )
    else:
        risk_level = RiskLevel.NORMAL
        detail = "Stock level is within the normal operating range."
        factors = {}  # no meaningful risk drivers when normal

    return InventoryRiskResult(
        sku_id=sku_id,
        risk_level=risk_level,
        days_of_supply=days_of_supply,
        reorder_point_units=reorder_point_units,
        safety_stock_units=safety_stock_units,
        contributing_factors=factors,
        detail=detail,
    )


def evaluate_portfolio_risk(
    df: pd.DataFrame,
    safety_stock_days: float = 14.0,
    overstock_multiplier: float = 3.0,
) -> pd.DataFrame:
    """
    Batch version of evaluate_sku_risk over a DataFrame of SKUs.

    Expected columns (rename upstream if core/forecasting.py uses
    different names):
        sku_id, current_stock, avg_daily_demand,
        forecasted_demand_next_period, forecast_period_days, lead_time_days

    Returns:
        DataFrame with one row per SKU, including risk_level,
        days_of_supply, reorder_point_units, safety_stock_units,
        contributing_factors (dict), detail.
    """
    required_cols = {
        "sku_id",
        "current_stock",
        "avg_daily_demand",
        "forecasted_demand_next_period",
        "forecast_period_days",
        "lead_time_days",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    results = []
    for _, row in df.iterrows():
        result = evaluate_sku_risk(
            sku_id=row["sku_id"],
            current_stock=row["current_stock"],
            avg_daily_demand=row["avg_daily_demand"],
            forecasted_demand_next_period=row["forecasted_demand_next_period"],
            forecast_period_days=row["forecast_period_days"],
            lead_time_days=row["lead_time_days"],
            safety_stock_days=safety_stock_days,
            overstock_multiplier=overstock_multiplier,
        )
        results.append(result.to_dict())

    return pd.DataFrame(results)


if __name__ == "__main__":
    # Quick manual smoke test — mirrors what `uv run python core/inventory_risk.py`
    # should show you in the terminal.
    sample = evaluate_sku_risk(
        sku_id="SKU-001",
        current_stock=50,
        avg_daily_demand=10,
        forecasted_demand_next_period=140,  # 20/day over 7 days -> spike
        forecast_period_days=7,
        lead_time_days=5,
        safety_stock_days=14,
    )
    print(sample.to_dict())
