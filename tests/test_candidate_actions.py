"""
tests/test_candidate_actions.py

Comprehensive tests for Project 17 / P3 Decision & Replenishment Layer:
- do_nothing baseline evaluation
- Deterministic replenishment quantity and timing calculation
- POL-INV-001 60-day maximum stock holding cap
- POL-PRO-003 $10,000 approval threshold hierarchy
- Expedite feasibility and timing
- Transfer inventory feasibility (surplus vs no surplus)
- Decision Agent tool integration
- Decision trace options_considered persistence
- PO draft recommendation generation
"""

import pytest
import pandas as pd
import math

from core.candidate_actions import (
    generate_inventory_candidate_actions,
    generate_po_draft,
    ActionType,
    ApprovalTier,
    CandidateAction,
    CandidateActionSet,
    POLICY_MAX_STOCK_HOLDING_DAYS,
    POLICY_APPROVAL_THRESHOLD_DIRECTOR,
)
from agent.tools import get_candidate_actions, set_active_datasource
from data_ingestion.csv_source import CSVDataSource
from agent.decision_trace import DecisionTraceBuilder
from db.connection import SessionLocal
from db.models import DecisionTrace


@pytest.fixture
def sample_inventory_df():
    return pd.DataFrame([
        {
            "sku_id": "SKU_STOCKOUT_CRITICAL",
            "current_stock": 20.0,
            "reorder_point": 100.0,
            "safety_stock": 30.0,
            "lead_time_days": 10.0,
            "unit_cost": 50.0,
            "location_id": "LOC_WAREHOUSE_A",
            "tier": 1,
        },
        {
            "sku_id": "SKU_HEALTHY",
            "current_stock": 500.0,
            "reorder_point": 80.0,
            "safety_stock": 30.0,
            "lead_time_days": 7.0,
            "unit_cost": 25.0,
            "location_id": "LOC_WAREHOUSE_A",
            "tier": 2,
        },
    ])


def test_do_nothing_baseline_for_stockout_and_healthy(sample_inventory_df):
    """Verify do_nothing baseline represents truthful current state with 0 cost."""
    # Under stockout risk
    forecast = {"predicted_quantities": [70.0, 70.0], "forecast_horizon_weeks": 2}
    cand_set = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=sample_inventory_df,
        demand_forecast=forecast
    )
    
    dn = next(a for a in cand_set.actions if a.action_type == ActionType.DO_NOTHING)
    assert dn.is_baseline is True
    assert dn.feasible is True
    assert dn.quantity == 0.0
    assert dn.estimated_cost == 0.0
    assert dn.expected_stock_after == 20.0
    assert dn.expected_risk_level_after == "STOCKOUT_RISK"
    assert "stock out" in dn.reason.lower()

    # Under healthy inventory
    cand_set_healthy = generate_inventory_candidate_actions(
        "SKU_HEALTHY",
        inv_df=sample_inventory_df,
        demand_forecast=forecast
    )
    dn_healthy = next(a for a in cand_set_healthy.actions if a.action_type == ActionType.DO_NOTHING)
    assert dn_healthy.expected_risk_level_after == "NORMAL"
    assert "healthy" in dn_healthy.reason.lower()


def test_deterministic_reorder_quantity_and_timing(sample_inventory_df):
    """Verify replenishment quantity and timing are computed deterministically without LLM."""
    # Forecast: 70 units/wk => 10 units/day
    forecast = {"predicted_quantities": [70.0, 70.0], "forecast_horizon_weeks": 2}
    
    cand_set = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=sample_inventory_df,
        demand_forecast=forecast,
        custom_review_cycle_days=14.0  # 14 days review cycle
    )
    
    # ROP = 100, current = 20, projected daily = 10
    # Target stock = 100 + (14 * 10) = 240
    # Quantity = 240 - 20 = 220
    reorder = next(a for a in cand_set.actions if a.action_type == ActionType.REORDER)
    assert reorder.quantity == 220.0
    assert reorder.unit_cost == 50.0
    assert reorder.estimated_cost == 220.0 * 50.0  # 11,000.0
    
    # Current DOS = 20 / 10 = 2 days <= lead time (10 days) => timing must be immediate (0.0 days)
    assert reorder.timing_days == 0.0
    assert reorder.arrival_days == 10.0  # timing + lead time
    assert reorder.expected_stock_after == 240.0
    assert reorder.expected_days_of_supply_after == 24.0  # 240 / 10
    assert reorder.expected_risk_level_after == "NORMAL"


def test_max_stock_cap_enforcement_pol_inv_001(sample_inventory_df):
    """Verify POL-INV-001 hard constraint caps order quantity at 60 days of demand."""
    forecast = {"predicted_quantities": [70.0, 70.0], "forecast_horizon_weeks": 2}
    # Projected daily = 10 units/day => max stock allowed = 60 * 10 = 600 units
    
    # If custom review cycle is set to an excessively large value (e.g. 90 days),
    # raw quantity would be: 100 + (90 * 10) - 20 = 980 units
    cand_set = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=sample_inventory_df,
        demand_forecast=forecast,
        custom_review_cycle_days=90.0
    )
    
    reorder = next(a for a in cand_set.actions if a.action_type == ActionType.REORDER)
    # Must be capped at: max_allowed (600) - current (20) = 580 units!
    assert reorder.quantity == 580.0
    assert any("POL-INV-001" in c and "60" in c for c in reorder.policy_constraints)


def test_procurement_approval_threshold_pol_pro_003(sample_inventory_df):
    """Verify POL-PRO-003 approval hierarchy: < $10k Manager, >= $10k Director."""
    forecast = {"predicted_quantities": [70.0, 70.0], "forecast_horizon_weeks": 2}
    
    # Case 1: High value order (220 units * $50 = $11,000 >= $10,000)
    cand_set_high = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=sample_inventory_df,
        demand_forecast=forecast,
        custom_review_cycle_days=14.0
    )
    reorder_high = next(a for a in cand_set_high.actions if a.action_type == ActionType.REORDER)
    assert reorder_high.estimated_cost >= POLICY_APPROVAL_THRESHOLD_DIRECTOR
    assert reorder_high.approval_tier == ApprovalTier.SUPPLY_CHAIN_DIRECTOR
    assert any("Director" in c for c in reorder_high.policy_constraints)
    
    # Case 2: Low value order
    low_cost_df = sample_inventory_df.copy()
    low_cost_df.loc[low_cost_df["sku_id"] == "SKU_STOCKOUT_CRITICAL", "unit_cost"] = 10.0
    cand_set_low = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=low_cost_df,
        demand_forecast=forecast,
        custom_review_cycle_days=14.0
    )
    reorder_low = next(a for a in cand_set_low.actions if a.action_type == ActionType.REORDER)
    assert reorder_low.estimated_cost < POLICY_APPROVAL_THRESHOLD_DIRECTOR
    assert reorder_low.approval_tier == ApprovalTier.SUPPLY_CHAIN_MANAGER


def test_expedite_feasibility_and_lead_time_compression(sample_inventory_df):
    """Verify expedite cuts lead time and is only feasible when stockout is imminent."""
    forecast = {"predicted_quantities": [70.0, 70.0], "forecast_horizon_weeks": 2}
    
    # Imminent stockout (DOS = 2d < lead time 10d): Expedite is feasible
    cand_set = generate_inventory_candidate_actions(
        "SKU_STOCKOUT_CRITICAL",
        inv_df=sample_inventory_df,
        demand_forecast=forecast
    )
    exp = next(a for a in cand_set.actions if a.action_type == ActionType.EXPEDITE)
    assert exp.feasible is True
    # Lead time was 10d => cut to 5.0d (50% compression, max 5d)
    assert exp.arrival_days == 5.0
    # Expedite cost includes +25% freight surcharge
    assert exp.unit_cost == 50.0 * 1.25
    assert exp.estimated_cost == exp.quantity * (50.0 * 1.25)
    
    # Healthy inventory (DOS >> lead time): Expedite is infeasible
    cand_set_healthy = generate_inventory_candidate_actions(
        "SKU_HEALTHY",
        inv_df=sample_inventory_df,
        demand_forecast=forecast
    )
    exp_healthy = next(a for a in cand_set_healthy.actions if a.action_type == ActionType.EXPEDITE)
    assert exp_healthy.feasible is False
    assert "not operationally justifiable" in exp_healthy.feasibility_reason.lower() or "exceeds" in exp_healthy.feasibility_reason.lower()


def test_transfer_inventory_feasibility_with_and_without_surplus():
    """Verify transfer is only feasible if another facility has surplus, with no fabricated warehouses."""
    # Scenario A: Multi-facility dataset where LOC_SOUTH has surplus stock above ROP
    multi_loc_df = pd.DataFrame([
        {
            "sku_id": "SKU_X",
            "current_stock": 10.0,
            "reorder_point": 100.0,
            "safety_stock": 20.0,
            "lead_time_days": 10.0,
            "unit_cost": 30.0,
            "location_id": "LOC_NORTH",
        },
        {
            "sku_id": "SKU_X",
            "current_stock": 350.0,
            "reorder_point": 100.0,
            "safety_stock": 20.0,
            "lead_time_days": 10.0,
            "unit_cost": 30.0,
            "location_id": "LOC_SOUTH",  # Surplus = 350 - 100 = 250 units!
        },
    ])
    
    cand_set_a = generate_inventory_candidate_actions("SKU_X", inv_df=multi_loc_df)
    trans_a = next(a for a in cand_set_a.actions if a.action_type == ActionType.TRANSFER_INVENTORY)
    assert trans_a.feasible is True
    assert trans_a.source_location_id == "LOC_SOUTH"
    assert trans_a.quantity > 0.0
    assert trans_a.arrival_days == 2.0  # transfer transit days
    
    # Scenario B: Single-location dataset (no secondary location)
    single_loc_df = pd.DataFrame([
        {
            "sku_id": "SKU_Y",
            "current_stock": 10.0,
            "reorder_point": 100.0,
            "safety_stock": 20.0,
            "lead_time_days": 10.0,
            "unit_cost": 30.0,
            "location_id": "LOC_NORTH",
        }
    ])
    cand_set_b = generate_inventory_candidate_actions("SKU_Y", inv_df=single_loc_df)
    trans_b = next(a for a in cand_set_b.actions if a.action_type == ActionType.TRANSFER_INVENTORY)
    assert trans_b.feasible is False
    assert "no secondary warehouse" in trans_b.feasibility_reason.lower()

    # Scenario C: Multi-location, but secondary location has zero surplus (stock <= ROP)
    no_surplus_df = pd.DataFrame([
        {
            "sku_id": "SKU_Z",
            "current_stock": 10.0,
            "reorder_point": 100.0,
            "safety_stock": 20.0,
            "lead_time_days": 10.0,
            "unit_cost": 30.0,
            "location_id": "LOC_NORTH",
        },
        {
            "sku_id": "SKU_Z",
            "current_stock": 80.0,
            "reorder_point": 100.0,
            "safety_stock": 20.0,
            "lead_time_days": 10.0,
            "unit_cost": 30.0,
            "location_id": "LOC_SOUTH",  # 80 < 100 => 0 surplus
        },
    ])
    cand_set_c = generate_inventory_candidate_actions("SKU_Z", inv_df=no_surplus_df)
    trans_c = next(a for a in cand_set_c.actions if a.action_type == ActionType.TRANSFER_INVENTORY)
    assert trans_c.feasible is False
    assert "none currently hold surplus" in trans_c.feasibility_reason.lower()


def test_agent_tool_get_candidate_actions_integration():
    """Verify get_candidate_actions tool function executes cleanly on demo dataset."""
    set_active_datasource(CSVDataSource(data_dir="data"))
    
    res = get_candidate_actions("SKU_104")
    assert "candidate_actions" in res
    assert len(res["candidate_actions"]) == 4
    
    action_names = [a["action_name"] for a in res["candidate_actions"]]
    assert "do_nothing" in action_names
    assert "reorder" in action_names
    assert "expedite" in action_names
    assert "transfer_inventory" in action_names


def test_po_draft_recommendation_generation():
    """Verify PO draft generates a formal internal recommendation artifact."""
    action = CandidateAction(
        action_type=ActionType.REORDER,
        sku_id="SKU_104",
        quantity=140.0,
        timing_days=0.0,
        arrival_days=14.0,
        expected_stock_after=160.0,
        expected_days_of_supply_after=25.0,
        expected_risk_level_after="NORMAL",
        estimated_cost=35000.0,
        unit_cost=250.0,
        source_location_id="SUPPLIER_EXTERNAL",
        destination_location_id="LOC_SOUTH",
        policy_constraints=["POL-PRO-003: Director Approval Required"],
        feasible=True,
        feasibility_reason="Standard replenishment",
        reason="Order 140 units to restore inventory buffer",
        approval_tier=ApprovalTier.SUPPLY_CHAIN_DIRECTOR
    )
    
    po_draft = generate_po_draft(action, approver_name="Supply Chain Director")
    
    assert po_draft["artifact_type"] == "PURCHASE_ORDER_DRAFT_RECOMMENDATION"
    assert po_draft["sku_id"] == "SKU_104"
    assert po_draft["recommended_quantity"] == 140.0
    assert po_draft["total_estimated_amount"] == 35000.0
    assert po_draft["approval_tier_required"] == "SUPPLY_CHAIN_DIRECTOR"
    assert po_draft["automated_execution"] is False
    assert "unassigned" in po_draft["supplier_id"].lower()
    assert "disclaimer" in po_draft


def test_decision_trace_persists_options_considered():
    """Verify DecisionTraceBuilder records options_considered into the database trace."""
    builder = DecisionTraceBuilder(inputs={"situation": "Critical stockout on SKU_104"})
    
    set_active_datasource(CSVDataSource(data_dir="data"))
    cand_res = get_candidate_actions("SKU_104")
    builder.options_considered = cand_res
    builder.set_primary_proposal({"action": "Place standard purchase order for SKU_104", "cost": 35000.0})
    builder.set_consensus_result({"status": "APPROVED", "recommendation": {"action": "Reorder SKU_104"}})
    
    trace_id = builder.persist()
    assert trace_id.startswith("TRACE_")
    
    session = SessionLocal()
    try:
        saved_trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        assert saved_trace is not None
        assert saved_trace.options_considered is not None
        assert "candidate_actions" in saved_trace.options_considered
        assert len(saved_trace.options_considered["candidate_actions"]) == 4
    finally:
        session.close()
