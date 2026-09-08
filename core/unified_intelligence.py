"""
core/unified_intelligence.py
Unified Supply Chain Intelligence Engine for SupplyChain Sentinel AI.

Combines siloed operational signals into a single coherent state:
Demand Forecast → Inventory Risk → Delivery Delay → Logistics Routes → Unified Situation

Core responsibilities:
1. Synthesize multi-source intelligence into `UnifiedSupplyChainState`.
2. Discover cross-risk dependencies (e.g., low stock compounded by delayed replenishment).
3. Identify the primary operational bottleneck.
4. Compute standardized enterprise severity (CRITICAL, HIGH, MEDIUM, LOW, NORMAL).
5. Preserve deterministic source attribution for every numerical output.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import pandas as pd
import numpy as np

from data_ingestion.base import DataSource
from data_ingestion.active_dataset import active_dataset
from core.forecasting import train_forecast_model, predict_demand, get_feature_importance
from core.inventory_risk import evaluate_sku_risk, RiskLevel
from core.delivery_risk import train_delivery_risk_model, predict_delivery_risk


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NORMAL = "NORMAL"


@dataclass
class OperationalBottleneck:
    """Represents the primary operational failure point in the supply chain."""
    bottleneck_type: str
    primary_entity_id: str
    description: str
    impact_urgency_hours: float
    mitigation_options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bottleneck_type": self.bottleneck_type,
            "primary_entity_id": self.primary_entity_id,
            "description": self.description,
            "impact_urgency_hours": round(self.impact_urgency_hours, 1),
            "mitigation_options": self.mitigation_options,
        }


@dataclass
class UnifiedSupplyChainState:
    """
    Unified state representing the complete operational picture of a situation.
    Supplies structured, traceable evidence to the AI Decision Agent and Command Center.
    """
    situation_id: str
    timestamp: str
    target_sku_id: Optional[str]
    target_delivery_id: Optional[str]
    overall_severity: SeverityLevel
    bottleneck: OperationalBottleneck
    cross_risk_dependencies: List[str]
    demand_forecast: Dict[str, Any]
    inventory_state: Dict[str, Any]
    delivery_state: Dict[str, Any]
    affected_entities: Dict[str, List[str]]
    deterministic_attribution: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "situation_id": self.situation_id,
            "timestamp": self.timestamp,
            "target_sku_id": self.target_sku_id,
            "target_delivery_id": self.target_delivery_id,
            "overall_severity": self.overall_severity.value,
            "bottleneck": self.bottleneck.to_dict(),
            "cross_risk_dependencies": self.cross_risk_dependencies,
            "demand_forecast": self.demand_forecast,
            "inventory_state": self.inventory_state,
            "delivery_state": self.delivery_state,
            "affected_entities": self.affected_entities,
            "deterministic_attribution": self.deterministic_attribution,
        }

    def to_summary_markdown(self) -> str:
        """Generates an executive structured markdown briefing for the AI Decision Agent."""
        lines = [
            f"### 🛡️ Unified Situation Briefing: {self.situation_id}",
            f"**Overall Severity:** `{self.overall_severity.value}` | **Timestamp:** `{self.timestamp}`",
            "",
            "#### 🚨 Primary Operational Bottleneck",
            f"- **Type:** `{self.bottleneck.bottleneck_type}` ({self.bottleneck.primary_entity_id})",
            f"- **Description:** {self.bottleneck.description}",
            f"- **Urgency Window:** ~{self.bottleneck.impact_urgency_hours:.0f} hours",
            "",
            "#### 🔗 Cross-Risk Dependencies",
        ]
        if self.cross_risk_dependencies:
            for dep in self.cross_risk_dependencies:
                lines.append(f"- ⚠️ {dep}")
        else:
            lines.append("- No compounding multi-tier risks detected.")

        lines.extend([
            "",
            "#### 📊 Quantitative Operational Evidence",
            f"- **Demand Forecast (Avg/Day):** {self.demand_forecast.get('avg_forecasted_units', 'N/A')} units *(Source: {self.deterministic_attribution.get('demand_forecast', 'LightGBM')})*",
            f"- **Inventory Coverage:** {self.inventory_state.get('days_of_supply', 'N/A')} days *(Risk: {self.inventory_state.get('risk_level', 'N/A')})*",
            f"- **Delivery Risk:** {self.delivery_state.get('risk_score_pct', 'N/A')}% delay probability *(Carrier: {self.delivery_state.get('carrier_id', 'N/A')})*",
        ])
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Intelligence Synthesis Logic
# ---------------------------------------------------------------------------

def calculate_overall_severity(
    inv_risk_level: str,
    days_of_supply: float,
    delivery_risk_pct: float,
    has_compounding_dependency: bool
) -> SeverityLevel:
    """
    Computes unified enterprise situation severity based on deterministic rules.
    """
    if has_compounding_dependency or (inv_risk_level == "STOCKOUT_RISK" and days_of_supply < 3.0 and delivery_risk_pct > 60.0):
        return SeverityLevel.CRITICAL
    elif inv_risk_level == "STOCKOUT_RISK" and days_of_supply < 7.0:
        return SeverityLevel.HIGH
    elif delivery_risk_pct >= 70.0:
        return SeverityLevel.HIGH
    elif inv_risk_level == "OVERSTOCK_RISK" or delivery_risk_pct >= 40.0:
        return SeverityLevel.MEDIUM
    elif inv_risk_level == "STOCKOUT_RISK" or delivery_risk_pct >= 20.0:
        return SeverityLevel.LOW
    else:
        return SeverityLevel.NORMAL


def identify_bottleneck(
    sku_id: Optional[str],
    delivery_id: Optional[str],
    inv_risk_level: str,
    days_of_supply: float,
    delivery_risk_pct: float,
    carrier: str,
    top_shap_features: List[Dict[str, Any]]
) -> Tuple[OperationalBottleneck, List[str]]:
    """
    Identifies the primary operational bottleneck and cross-risk dependencies.
    """
    dependencies: List[str] = []
    
    # 1. Compound Risk: Low stock + Delayed Inbound
    if inv_risk_level == "STOCKOUT_RISK" and delivery_risk_pct >= 50.0:
        dep = (
            f"Low inventory on {sku_id} ({days_of_supply:.1f} days remaining) compounds "
            f"with delayed shipment {delivery_id} ({delivery_risk_pct:.1f}% delay risk). "
            f"Stockout will occur before replenishment arrives."
        )
        dependencies.append(dep)
        
        # Primary bottleneck is replenishment transit delay
        top_driver = top_shap_features[0]["feature"] if top_shap_features else "transit bottleneck"
        bottleneck = OperationalBottleneck(
            bottleneck_type="COMPOUND_TRANSIT_STOCKOUT",
            primary_entity_id=f"{sku_id} + {delivery_id}",
            description=f"Replenishment shipment {delivery_id} delayed by {top_driver}; stockout imminent for {sku_id}.",
            impact_urgency_hours=max(days_of_supply * 24.0, 12.0),
            mitigation_options=["Expedite shipment via air freight", "Transfer emergency stock from adjacent DC", "Split delivery order"]
        )
        return bottleneck, dependencies

    # 2. Pure Stockout Risk
    if inv_risk_level == "STOCKOUT_RISK":
        bottleneck = OperationalBottleneck(
            bottleneck_type="STOCKOUT_IMMINENT",
            primary_entity_id=sku_id or "UNKNOWN_SKU",
            description=f"Demand velocity exceeds inventory coverage. Only {days_of_supply:.1f} days of supply remaining.",
            impact_urgency_hours=max(days_of_supply * 24.0, 24.0),
            mitigation_options=["Emergency reorder", "Reroute surplus inventory from regional hub", "Cap order allocation"]
        )
        return bottleneck, dependencies

    # 3. Pure Delivery Delay Risk
    if delivery_risk_pct >= 50.0:
        driver_desc = f" ({top_shap_features[0]['feature']})" if top_shap_features else ""
        bottleneck = OperationalBottleneck(
            bottleneck_type="DELIVERY_TRANSIT_DELAY",
            primary_entity_id=delivery_id or "UNKNOWN_DELIVERY",
            description=f"Carrier {carrier} facing high transit delay probability ({delivery_risk_pct:.1f}%){driver_desc}.",
            impact_urgency_hours=24.0,
            mitigation_options=["Switch to secondary carrier", "Reroute via less congested corridor", "Pre-notify receiving customer"]
        )
        return bottleneck, dependencies

    # 4. Overstock / Holding Cost Inefficiency
    if inv_risk_level == "OVERSTOCK_RISK":
        bottleneck = OperationalBottleneck(
            bottleneck_type="OVERSTOCK_ACCUMULATION",
            primary_entity_id=sku_id or "UNKNOWN_SKU",
            description=f"Excess inventory detected ({days_of_supply:.1f} days of supply). High carrying costs.",
            impact_urgency_hours=168.0, # 1 week
            mitigation_options=["Promotional discounting", "Pause pending purchase orders", "Redistribute to high-demand DCs"]
        )
        return bottleneck, dependencies

    # 5. Normal / Balanced
    bottleneck = OperationalBottleneck(
        bottleneck_type="NONE",
        primary_entity_id="SYSTEM",
        description="Operations balanced. No acute inventory or logistics bottlenecks detected.",
        impact_urgency_hours=720.0,
        mitigation_options=["Continue monitoring routine telemetry"]
    )
    return bottleneck, dependencies


def build_unified_situation(
    sku_id: Optional[str] = None,
    delivery_id: Optional[str] = None,
    data_source: Optional[DataSource] = None,
) -> UnifiedSupplyChainState:
    """
    Builds a complete, deterministic, unified supply chain intelligence situation.
    Integrates forecasting, inventory state, delivery risk, and cross-risk dependencies.
    """
    source = data_source or active_dataset.get_source()
    timestamp_now = datetime.now(timezone.utc).isoformat()
    situation_id = f"SIT_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    # 1. Load operational data
    inv_df = source.load_inventory_snapshot()
    demand_df = source.load_historical_demand()
    del_df = source.load_deliveries()

    # Target SKU selection
    if sku_id is None:
        if not inv_df.empty:
            # Pick highest risk SKU (lowest current_stock / reorder_point ratio)
            ratio = inv_df["current_stock"] / np.maximum(inv_df["reorder_point"], 1.0)
            sku_id = str(inv_df.loc[ratio.idxmin(), "sku_id"])
        else:
            sku_id = "SKU_DEFAULT"

    # Target Delivery selection
    if delivery_id is None:
        if not del_df.empty:
            delivery_id = str(del_df.iloc[0]["delivery_id"])
        else:
            delivery_id = "DEL_DEFAULT"

    affected_skus = [sku_id]
    affected_deliveries = [delivery_id]

    deterministic_attribution: Dict[str, str] = {}

    # 2. Demand Forecast
    demand_forecast_info: Dict[str, Any] = {}
    try:
        forecast_model, _, _ = train_forecast_model(demand_df)
        preds_df = predict_demand(forecast_model, demand_df, sku_id)
        avg_units = float(np.round(preds_df["predicted_demand"].mean(), 2))
        total_units = float(np.round(preds_df["predicted_demand"].sum(), 2))
        feat_imp = get_feature_importance(forecast_model)
        
        demand_forecast_info = {
            "sku_id": sku_id,
            "avg_forecasted_units": avg_units,
            "total_forecasted_units": total_units,
            "forecast_horizon_days": len(preds_df),
            "top_drivers": list(feat_imp.keys())[:3],
        }
        deterministic_attribution["demand_forecast"] = "LightGBM LGBMRegressor (trained on active historical demand)"
    except Exception as e:
        demand_forecast_info = {
            "sku_id": sku_id,
            "avg_forecasted_units": 10.0,
            "total_forecasted_units": 140.0,
            "forecast_horizon_days": 14,
            "warning": f"Forecast model fallback: {e}"
        }
        deterministic_attribution["demand_forecast"] = "Empirical Demand Baseline Average"

    # 3. Inventory Risk
    inventory_state_info: Dict[str, Any] = {}
    sku_inv_row = inv_df[inv_df["sku_id"] == sku_id]
    if not sku_inv_row.empty:
        curr_stock = float(sku_inv_row.iloc[0]["current_stock"])
        lead_time = float(sku_inv_row.iloc[0].get("lead_time_days", 7.0))
        unit_cost = float(sku_inv_row.iloc[0].get("unit_cost", 10.0))
    else:
        curr_stock = 50.0
        lead_time = 7.0
        unit_cost = 10.0

    avg_demand = demand_forecast_info.get("avg_forecasted_units", 10.0)
    inv_res = evaluate_sku_risk(
        sku_id=sku_id,
        current_stock=curr_stock,
        avg_daily_demand=avg_demand,
        forecasted_demand_next_period=avg_demand * lead_time,
        forecast_period_days=int(lead_time),
        lead_time_days=lead_time
    )
    inventory_state_info = {
        "sku_id": sku_id,
        "current_stock": curr_stock,
        "days_of_supply": inv_res.days_of_supply,
        "risk_level": inv_res.risk_level.value,
        "reorder_point_units": inv_res.reorder_point_units,
        "safety_stock_units": inv_res.safety_stock_units,
        "lead_time_days": lead_time,
        "unit_cost": unit_cost,
        "detail": inv_res.detail,
    }
    deterministic_attribution["inventory_risk"] = "Deterministic Inventory Position Calculation"

    # 4. Delivery Risk
    delivery_state_info: Dict[str, Any] = {}
    del_row = del_df[del_df["delivery_id"] == delivery_id]
    carrier_id = str(del_row.iloc[0].get("carrier_id", "DEFAULT_CARRIER")) if not del_row.empty else "CARRIER_A"

    try:
        del_model, _, _ = train_delivery_risk_model(del_df)
        del_risk_output = predict_delivery_risk(del_model, del_df, delivery_id)
        
        delay_prob = float(del_risk_output["risk_score"])
        top_shap = del_risk_output.get("top_features", [])
        
        delivery_state_info = {
            "delivery_id": delivery_id,
            "carrier_id": carrier_id,
            "risk_score_pct": round(delay_prob * 100.0, 1),
            "risk_label": del_risk_output.get("risk_label", "LOW"),
            "top_shap_features": top_shap,
            "origin": str(del_row.iloc[0].get("origin", "WH_CENTRAL")) if not del_row.empty else "WH_CENTRAL",
            "destination": str(del_row.iloc[0].get("destination", "RETAIL_1")) if not del_row.empty else "RETAIL_1",
        }
        deterministic_attribution["delivery_risk"] = "LightGBM Binary Classifier with TreeExplainer SHAP"
    except Exception as e:
        delivery_state_info = {
            "delivery_id": delivery_id,
            "carrier_id": carrier_id,
            "risk_score_pct": 15.0,
            "risk_label": "LOW",
            "top_shap_features": [],
            "warning": f"Delivery model fallback: {e}"
        }
        deterministic_attribution["delivery_risk"] = "Empirical Delivery Default"

    # 5. Bottleneck & Cross-Risk Synthesis
    bottleneck, cross_deps = identify_bottleneck(
        sku_id=sku_id,
        delivery_id=delivery_id,
        inv_risk_level=inventory_state_info["risk_level"],
        days_of_supply=inventory_state_info["days_of_supply"],
        delivery_risk_pct=delivery_state_info["risk_score_pct"],
        carrier=carrier_id,
        top_shap_features=delivery_state_info.get("top_shap_features", [])
    )

    # 6. Overall Severity
    overall_sev = calculate_overall_severity(
        inv_risk_level=inventory_state_info["risk_level"],
        days_of_supply=inventory_state_info["days_of_supply"],
        delivery_risk_pct=delivery_state_info["risk_score_pct"],
        has_compounding_dependency=len(cross_deps) > 0
    )

    return UnifiedSupplyChainState(
        situation_id=situation_id,
        timestamp=timestamp_now,
        target_sku_id=sku_id,
        target_delivery_id=delivery_id,
        overall_severity=overall_sev,
        bottleneck=bottleneck,
        cross_risk_dependencies=cross_deps,
        demand_forecast=demand_forecast_info,
        inventory_state=inventory_state_info,
        delivery_state=delivery_state_info,
        affected_entities={"skus": affected_skus, "deliveries": affected_deliveries},
        deterministic_attribution=deterministic_attribution,
    )
