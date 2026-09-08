"""
tests/test_unified_intelligence.py
Unit and integration tests for P2 — Unified Supply Chain Intelligence:
- UnifiedSupplyChainState structure & serialization
- Cross-risk dependency detection (low stock + delayed replenishment)
- Operational bottleneck discovery
- Deterministic source attribution for all numerical figures
- Enterprise severity ranking (CRITICAL -> NORMAL)
- Executive markdown briefing output
"""

import pytest
import pandas as pd
from datetime import datetime, timezone

from data_ingestion.csv_source import CSVDataSource
from core.unified_intelligence import (
    build_unified_situation,
    calculate_overall_severity,
    identify_bottleneck,
    UnifiedSupplyChainState,
    SeverityLevel,
    OperationalBottleneck,
)


def test_unified_situation_generation_with_active_data():
    """Verify that build_unified_situation compiles a complete state from a data source."""
    source = CSVDataSource(data_dir="data")
    state = build_unified_situation(sku_id="SKU_101", delivery_id="DEL_001", data_source=source)

    assert isinstance(state, UnifiedSupplyChainState)
    assert state.target_sku_id == "SKU_101"
    assert state.target_delivery_id == "DEL_001"
    assert state.overall_severity in [s for s in SeverityLevel]
    assert state.bottleneck is not None
    assert "demand_forecast" in state.to_dict()
    assert "inventory_state" in state.to_dict()
    assert "delivery_state" in state.to_dict()
    assert "deterministic_attribution" in state.to_dict()


def test_compounding_cross_risk_dependency():
    """Verify that low stock + delayed replenishment creates a COMPOUND_TRANSIT_STOCKOUT bottleneck with CRITICAL severity."""
    bottleneck, deps = identify_bottleneck(
        sku_id="SKU_999",
        delivery_id="DEL_777",
        inv_risk_level="STOCKOUT_RISK",
        days_of_supply=1.8,
        delivery_risk_pct=78.5,
        carrier="CARRIER_A",
        top_shap_features=[{"feature": "traffic_delay_hrs", "value": 3.5, "effect": "INCREASES_RISK"}]
    )

    assert len(deps) == 1
    assert "compounds with delayed shipment" in deps[0]
    assert bottleneck.bottleneck_type == "COMPOUND_TRANSIT_STOCKOUT"
    assert bottleneck.impact_urgency_hours <= 48.0
    assert len(bottleneck.mitigation_options) > 0

    severity = calculate_overall_severity(
        inv_risk_level="STOCKOUT_RISK",
        days_of_supply=1.8,
        delivery_risk_pct=78.5,
        has_compounding_dependency=True
    )
    assert severity == SeverityLevel.CRITICAL


def test_pure_stockout_bottleneck():
    """Verify pure stockout risk without high delivery delay produces STOCKOUT_IMMINENT."""
    bottleneck, deps = identify_bottleneck(
        sku_id="SKU_101",
        delivery_id="DEL_002",
        inv_risk_level="STOCKOUT_RISK",
        days_of_supply=4.0,
        delivery_risk_pct=15.0,
        carrier="CARRIER_B",
        top_shap_features=[]
    )

    assert len(deps) == 0
    assert bottleneck.bottleneck_type == "STOCKOUT_IMMINENT"
    assert bottleneck.primary_entity_id == "SKU_101"

    severity = calculate_overall_severity(
        inv_risk_level="STOCKOUT_RISK",
        days_of_supply=4.0,
        delivery_risk_pct=15.0,
        has_compounding_dependency=False
    )
    assert severity == SeverityLevel.HIGH


def test_pure_delivery_delay_bottleneck():
    """Verify delivery delay with healthy inventory produces DELIVERY_TRANSIT_DELAY."""
    bottleneck, deps = identify_bottleneck(
        sku_id="SKU_102",
        delivery_id="DEL_050",
        inv_risk_level="NORMAL",
        days_of_supply=25.0,
        delivery_risk_pct=82.0,
        carrier="CARRIER_C",
        top_shap_features=[{"feature": "distance_km", "value": 450.0, "effect": "INCREASES_RISK"}]
    )

    assert len(deps) == 0
    assert bottleneck.bottleneck_type == "DELIVERY_TRANSIT_DELAY"
    assert bottleneck.primary_entity_id == "DEL_050"

    severity = calculate_overall_severity(
        inv_risk_level="NORMAL",
        days_of_supply=25.0,
        delivery_risk_pct=82.0,
        has_compounding_dependency=False
    )
    assert severity == SeverityLevel.HIGH


def test_deterministic_source_attribution():
    """Verify that all key numerical streams record their computational source attribution."""
    source = CSVDataSource(data_dir="data")
    state = build_unified_situation(sku_id="SKU_101", delivery_id="DEL_001", data_source=source)

    attr = state.deterministic_attribution
    assert "demand_forecast" in attr
    assert "inventory_risk" in attr
    assert "delivery_risk" in attr
    assert "LightGBM" in attr["demand_forecast"] or "Baseline" in attr["demand_forecast"]
    assert "Inventory" in attr["inventory_risk"]


def test_to_summary_markdown_executive_briefing():
    """Verify executive summary markdown contains key situation metrics."""
    source = CSVDataSource(data_dir="data")
    state = build_unified_situation(sku_id="SKU_101", delivery_id="DEL_001", data_source=source)

    md = state.to_summary_markdown()
    assert "### 🛡️ Unified Situation Briefing" in md
    assert "Overall Severity:" in md
    assert "Primary Operational Bottleneck" in md
    assert "Demand Forecast" in md
    assert "Inventory Coverage" in md
