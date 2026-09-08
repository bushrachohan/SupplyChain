"""
core/candidate_actions.py

Deterministic candidate replenishment action generation for SupplyChain Sentinel AI (Project 17 / P3).
Turns detected inventory risks into explicit, evidence-backed replenishment options:
- do_nothing (baseline)
- reorder (standard purchase order)
- expedite (emergency rush order)
- transfer_inventory (inter-facility stock re-allocation)

Rule classification:
Category A: Authoritative Policy Rules (from policies/inventory_policy.md & procurement_policy.md)
Category B: Data-Derived Rules (from active dataset, forecasting output, and inventory_risk)
Category C: Explicit Configurable Assumptions (project parameters with transparent defaults)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import math
import pandas as pd

from core.inventory_risk import evaluate_sku_risk, RiskLevel


# ---------------------------------------------------------------------------
# Category A: Authoritative Policy Constants (verifiable in policies/*.md)
# ---------------------------------------------------------------------------
POLICY_MAX_STOCK_HOLDING_DAYS = 60.0  # POL-INV-001 Section 3: Max stock cap
POLICY_APPROVAL_THRESHOLD_DIRECTOR = 10000.0  # POL-PRO-003 Section 1: >= $10k requires Director approval
POLICY_EMERGENCY_REALLOCATION_DAYS = 7.0  # POL-INV-001 Section 3: Stockout <= 7d requires exploring transfer first


# ---------------------------------------------------------------------------
# Category C: Explicit Configurable Assumptions (Project Parameters)
# Note: These values are explicitly documented assumptions and NOT official policy.
# ---------------------------------------------------------------------------
CONFIGURABLE_REVIEW_CYCLES: Dict[Any, float] = {
    1: 7.0,       # Tier 1 high-velocity: 7-day review cycle assumption
    2: 14.0,      # Tier 2 standard: 14-day review cycle assumption
    3: 21.0,      # Tier 3 low-velocity: 21-day review cycle assumption
    "default": 14.0  # Default assumption when SKU tier is unassigned
}

CONFIGURABLE_EXPEDITE_REDUCTION_FACTOR = 0.50  # Cuts supplier lead time by 50%
CONFIGURABLE_EXPEDITE_MAX_LEAD_TIME_DAYS = 5.0  # Caps expedite lead time to max 5 days
CONFIGURABLE_EXPEDITE_SURCHARGE_RATE = 0.25     # +25% freight expedite surcharge on unit cost

CONFIGURABLE_TRANSFER_TRANSIT_DAYS = 2.0        # Regional inter-warehouse transit days assumption
CONFIGURABLE_TRANSFER_COST_RATE = 0.05          # 5% handling / intra-network freight cost rate


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

class ActionType(str, Enum):
    DO_NOTHING = "do_nothing"
    REORDER = "reorder"
    EXPEDITE = "expedite"
    TRANSFER_INVENTORY = "transfer_inventory"


class ApprovalTier(str, Enum):
    NONE = "NONE"
    SUPPLY_CHAIN_MANAGER = "SUPPLY_CHAIN_MANAGER"
    SUPPLY_CHAIN_DIRECTOR = "SUPPLY_CHAIN_DIRECTOR"


@dataclass
class CandidateAction:
    """Represents an explicit, evidence-backed replenishment or mitigation action."""
    action_type: ActionType
    sku_id: str
    quantity: float
    timing_days: float
    arrival_days: float
    expected_stock_after: float
    expected_days_of_supply_after: float
    expected_risk_level_after: str
    estimated_cost: float
    unit_cost: float
    source_location_id: Optional[str] = None
    destination_location_id: Optional[str] = None
    policy_constraints: List[str] = field(default_factory=list)
    feasible: bool = True
    feasibility_reason: str = ""
    reason: str = ""
    approval_tier: ApprovalTier = ApprovalTier.NONE
    is_baseline: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_name": self.action_type.value,
            "sku_id": self.sku_id,
            "quantity": round(self.quantity, 1),
            "timing_days": round(self.timing_days, 1),
            "arrival_days": round(self.arrival_days, 1),
            "expected_stock_after": round(self.expected_stock_after, 1),
            "expected_days_of_supply_after": round(self.expected_days_of_supply_after, 1),
            "expected_risk_level_after": self.expected_risk_level_after,
            "estimated_cost": round(self.estimated_cost, 2),
            "unit_cost": round(self.unit_cost, 2),
            "source_location_id": self.source_location_id,
            "destination_location_id": self.destination_location_id,
            "policy_constraints": self.policy_constraints,
            "feasible": self.feasible,
            "feasibility_reason": self.feasibility_reason,
            "reason": self.reason,
            "approval_tier": self.approval_tier.value,
            "is_baseline": self.is_baseline,
        }


@dataclass
class CandidateActionSet:
    """Set of candidate actions evaluated for an SKU under risk."""
    sku_id: str
    current_stock: float
    reorder_point: float
    safety_stock: float
    projected_daily_demand: float
    current_days_of_supply: float
    current_risk_level: str
    actions: List[CandidateAction] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku_id": self.sku_id,
            "current_stock": round(self.current_stock, 1),
            "reorder_point": round(self.reorder_point, 1),
            "safety_stock": round(self.safety_stock, 1),
            "projected_daily_demand": round(self.projected_daily_demand, 2),
            "current_days_of_supply": round(self.current_days_of_supply, 1),
            "current_risk_level": self.current_risk_level,
            "candidate_actions": [a.to_dict() for a in self.actions],
            "feasible_actions_count": len([a for a in self.actions if a.feasible]),
        }

    def to_comparison_df(self) -> pd.DataFrame:
        """Generates a business-facing comparison table across candidate actions."""
        rows = []
        for a in self.actions:
            rows.append({
                "Action": a.action_type.value.replace("_", " ").title(),
                "Quantity": f"{a.quantity:,.0f} units" if a.quantity > 0 else "0 units",
                "Arrival Timing": f"{a.arrival_days:.0f} days" if a.action_type != ActionType.DO_NOTHING else "Immediate (Baseline)",
                "Estimated Cost": f"₹{a.estimated_cost:,.0f}" if a.estimated_cost > 0 else "₹0",
                "Projected DOS": f"{a.expected_days_of_supply_after:.1f} d",
                "Expected Risk": a.expected_risk_level_after,
                "Approval Level": a.approval_tier.value.replace("_", " ").title(),
                "Feasible": "✅ Yes" if a.feasible else "❌ Infeasible",
                "Rationale / Constraints": a.reason if a.feasible else a.feasibility_reason,
            })
        return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Deterministic Generation Logic
# ---------------------------------------------------------------------------

def generate_inventory_candidate_actions(
    sku_id: str,
    inv_df: pd.DataFrame,
    demand_forecast: Optional[Dict[str, Any]] = None,
    demand_df: Optional[pd.DataFrame] = None,
    custom_review_cycle_days: Optional[float] = None,
    custom_expedite_surcharge_rate: Optional[float] = None,
    custom_transfer_transit_days: Optional[float] = None,
) -> CandidateActionSet:
    """
    Deterministically generates the 4 candidate inventory replenishment actions for an SKU.
    All calculations are deterministic and trace directly to data and policy rules.
    """
    if inv_df is None or inv_df.empty:
        raise ValueError("Inventory dataframe is empty or missing.")

    sku_rows = inv_df[inv_df["sku_id"] == sku_id]
    if sku_rows.empty:
        raise ValueError(f"SKU '{sku_id}' not found in active inventory data.")

    target_row = sku_rows.iloc[0]
    current_stock = float(target_row.get("current_stock", 0.0))
    reorder_point = float(target_row.get("reorder_point", 0.0))
    safety_stock = float(target_row.get("safety_stock", 0.0))
    lead_time_days = float(target_row.get("lead_time_days", 7.0))
    unit_cost = float(target_row.get("unit_cost", 10.0))
    location_id = str(target_row.get("location_id", "LOC_PRIMARY"))
    sku_tier = target_row.get("tier", None)

    # Category B: Calculate projected daily demand rate
    # Blends forward forecast (70%) with historical mean (30%) matching core/inventory_risk.py
    forecast_quantities = []
    forecast_weeks = 2
    if demand_forecast and isinstance(demand_forecast, dict):
        forecast_quantities = demand_forecast.get("predicted_quantities", [])
        forecast_weeks = max(1, demand_forecast.get("forecast_horizon_weeks", 2))

    if forecast_quantities:
        forecast_daily = sum(forecast_quantities) / (forecast_weeks * 7.0)
    else:
        # Fallback to historical daily demand if forecast is unavailable
        forecast_daily = 0.0

    avg_daily_demand = 0.0
    if demand_df is not None and not demand_df.empty and "sku_id" in demand_df.columns:
        sku_dem = demand_df[demand_df["sku_id"] == sku_id]
        if not sku_dem.empty and "quantity_demanded" in sku_dem.columns:
            avg_daily_demand = float(sku_dem["quantity_demanded"].mean())
    elif forecast_daily > 0:
        avg_daily_demand = forecast_daily

    if forecast_daily > 0 and avg_daily_demand > 0:
        projected_daily = (0.7 * forecast_daily) + (0.3 * avg_daily_demand)
    elif forecast_daily > 0:
        projected_daily = forecast_daily
    elif avg_daily_demand > 0:
        projected_daily = avg_daily_demand
    else:
        projected_daily = max(1.0, reorder_point / max(1.0, lead_time_days))

    current_dos = (current_stock / projected_daily) if projected_daily > 0 else 999.0
    is_stockout_risk = current_stock < reorder_point
    current_risk_str = "STOCKOUT_RISK" if is_stockout_risk else ("OVERSTOCK_RISK" if current_dos > POLICY_MAX_STOCK_HOLDING_DAYS else "NORMAL")

    # Category C: Determine order review cycle days
    if custom_review_cycle_days is not None:
        review_cycle = custom_review_cycle_days
    elif sku_tier in CONFIGURABLE_REVIEW_CYCLES:
        review_cycle = CONFIGURABLE_REVIEW_CYCLES[sku_tier]
    else:
        review_cycle = CONFIGURABLE_REVIEW_CYCLES["default"]

    # Category A & C: Deterministic order quantity calculation
    # Target stock S = ROP + (Review Cycle * Daily Demand)
    target_stock_level = reorder_point + (review_cycle * projected_daily)
    raw_reorder_qty = max(0.0, target_stock_level - current_stock)

    # Apply Category A hard constraint: POL-INV-001 60-day maximum stock holding cap
    max_allowed_stock = POLICY_MAX_STOCK_HOLDING_DAYS * projected_daily
    max_cap_applied = False
    if current_stock + raw_reorder_qty > max_allowed_stock:
        final_reorder_qty = max(0.0, max_allowed_stock - current_stock)
        max_cap_applied = True
    else:
        final_reorder_qty = raw_reorder_qty

    final_reorder_qty = float(math.ceil(final_reorder_qty))
    if final_reorder_qty <= 0 and is_stockout_risk:
        final_reorder_qty = float(math.ceil(max(1.0, reorder_point - current_stock)))

    actions: List[CandidateAction] = []

    # -----------------------------------------------------------------------
    # 1. Action: DO_NOTHING (Evaluation Baseline)
    # -----------------------------------------------------------------------
    dn_policies = []
    if is_stockout_risk:
        dn_reason = f"Baseline option: No intervention taken. Inventory will stock out in {current_dos:.1f} days."
        dn_risk = "STOCKOUT_RISK"
    else:
        dn_reason = f"Stock level ({current_stock:.0f} units) is healthy and exceeds reorder point ({reorder_point:.0f} units)."
        dn_risk = "NORMAL"

    actions.append(CandidateAction(
        action_type=ActionType.DO_NOTHING,
        sku_id=sku_id,
        quantity=0.0,
        timing_days=0.0,
        arrival_days=0.0,
        expected_stock_after=current_stock,
        expected_days_of_supply_after=current_dos,
        expected_risk_level_after=dn_risk,
        estimated_cost=0.0,
        unit_cost=unit_cost,
        source_location_id=location_id,
        destination_location_id=location_id,
        policy_constraints=dn_policies,
        feasible=True,
        feasibility_reason="Always feasible as the operational evaluation baseline.",
        reason=dn_reason,
        approval_tier=ApprovalTier.NONE,
        is_baseline=True
    ))

    # -----------------------------------------------------------------------
    # 2. Action: REORDER (Standard Procurement Purchase Order)
    # -----------------------------------------------------------------------
    reorder_cost = final_reorder_qty * unit_cost
    reorder_policies = []
    if max_cap_applied:
        reorder_policies.append(f"POL-INV-001: Order quantity capped to prevent exceeding {POLICY_MAX_STOCK_HOLDING_DAYS:.0f}-day max stock threshold.")

    # Category A: Approval hierarchy by value (POL-PRO-003)
    if reorder_cost >= POLICY_APPROVAL_THRESHOLD_DIRECTOR:
        reorder_approval = ApprovalTier.SUPPLY_CHAIN_DIRECTOR
        reorder_policies.append(f"POL-PRO-003: Order amount (₹{reorder_cost:,.0f}) >= ₹{POLICY_APPROVAL_THRESHOLD_DIRECTOR:,.0f} requires Supply Chain Director approval.")
    else:
        reorder_approval = ApprovalTier.SUPPLY_CHAIN_MANAGER
        reorder_policies.append(f"POL-PRO-003: Order amount (₹{reorder_cost:,.0f}) < ₹{POLICY_APPROVAL_THRESHOLD_DIRECTOR:,.0f} requires Supply Chain Manager approval.")

    # Timing: Immediate if stockout is imminent, else buffer days
    reorder_timing = 0.0 if current_dos <= lead_time_days else max(0.0, current_dos - lead_time_days)
    reorder_arrival = round(reorder_timing + lead_time_days, 1)
    reorder_stock_after = current_stock + final_reorder_qty
    reorder_dos_after = reorder_stock_after / projected_daily if projected_daily > 0 else 999.0

    actions.append(CandidateAction(
        action_type=ActionType.REORDER,
        sku_id=sku_id,
        quantity=final_reorder_qty,
        timing_days=round(reorder_timing, 1),
        arrival_days=reorder_arrival,
        expected_stock_after=round(reorder_stock_after, 1),
        expected_days_of_supply_after=round(reorder_dos_after, 1),
        expected_risk_level_after="NORMAL",
        estimated_cost=round(reorder_cost, 2),
        unit_cost=round(unit_cost, 2),
        source_location_id="SUPPLIER_EXTERNAL",
        destination_location_id=location_id,
        policy_constraints=reorder_policies,
        feasible=True,
        feasibility_reason="Standard replenishment is feasible through regular supplier procurement channels.",
        reason=f"Place standard replenishment purchase order for {final_reorder_qty:.0f} units to restore inventory buffer above reorder point.",
        approval_tier=reorder_approval,
        is_baseline=False
    ))

    # -----------------------------------------------------------------------
    # 3. Action: EXPEDITE (Emergency Rush Order)
    # -----------------------------------------------------------------------
    surcharge_rate = custom_expedite_surcharge_rate if custom_expedite_surcharge_rate is not None else CONFIGURABLE_EXPEDITE_SURCHARGE_RATE
    expedite_unit_cost = unit_cost * (1.0 + surcharge_rate)
    expedite_cost = final_reorder_qty * expedite_unit_cost

    # Category C: Expedite lead time assumption
    expedite_lead_time = max(1.0, min(CONFIGURABLE_EXPEDITE_MAX_LEAD_TIME_DAYS, round(lead_time_days * CONFIGURABLE_EXPEDITE_REDUCTION_FACTOR, 1)))

    expedite_policies = [
        f"POL-PRO-003: Emergency order expedited with certified supplier targeting under {CONFIGURABLE_EXPEDITE_MAX_LEAD_TIME_DAYS:.0f} days lead time.",
        f"Configurable Assumption: Expedite airfreight premium surcharge modeled at {surcharge_rate * 100:.0f}% on unit cost."
    ]
    if expedite_cost >= POLICY_APPROVAL_THRESHOLD_DIRECTOR:
        expedite_approval = ApprovalTier.SUPPLY_CHAIN_DIRECTOR
        expedite_policies.append(f"POL-PRO-003: Order amount (₹{expedite_cost:,.0f}) >= ₹{POLICY_APPROVAL_THRESHOLD_DIRECTOR:,.0f} requires Supply Chain Director approval.")
    else:
        expedite_approval = ApprovalTier.SUPPLY_CHAIN_MANAGER

    # Feasibility check: Only feasible if stockout is imminent and expedited arrival beats standard lead time
    if not is_stockout_risk:
        expedite_feasible = False
        expedite_feasibility_reason = "Current stock is healthy; paying emergency freight surcharge is not operationally justifiable."
    elif current_dos >= lead_time_days:
        expedite_feasible = False
        expedite_feasibility_reason = f"Current Days of Supply ({current_dos:.1f}d) exceeds standard supplier lead time ({lead_time_days:.1f}d). Standard reorder is sufficient without rush fees."
    elif expedite_lead_time >= lead_time_days:
        expedite_feasible = False
        expedite_feasibility_reason = f"Supplier cannot compress lead time below standard ({lead_time_days:.1f}d)."
    else:
        expedite_feasible = True
        expedite_feasibility_reason = f"Critical stockout risk: Expedited delivery arrives in {expedite_lead_time:.1f}d vs standard {lead_time_days:.1f}d, preventing {lead_time_days - expedite_lead_time:.1f} days of stockout."

    actions.append(CandidateAction(
        action_type=ActionType.EXPEDITE,
        sku_id=sku_id,
        quantity=final_reorder_qty,
        timing_days=0.0,
        arrival_days=expedite_lead_time,
        expected_stock_after=round(reorder_stock_after, 1),
        expected_days_of_supply_after=round(reorder_dos_after, 1),
        expected_risk_level_after="NORMAL",
        estimated_cost=round(expedite_cost, 2),
        unit_cost=round(expedite_unit_cost, 2),
        source_location_id="SUPPLIER_EMERGENCY",
        destination_location_id=location_id,
        policy_constraints=expedite_policies,
        feasible=expedite_feasible,
        feasibility_reason=expedite_feasibility_reason,
        reason=f"Fast-track shipment of {final_reorder_qty:.0f} units via priority express freight to arrive in {expedite_lead_time:.1f} days.",
        approval_tier=expedite_approval,
        is_baseline=False
    ))

    # -----------------------------------------------------------------------
    # 4. Action: TRANSFER_INVENTORY (Inter-Warehouse Stock Re-allocation)
    # -----------------------------------------------------------------------
    transfer_transit_days = custom_transfer_transit_days if custom_transfer_transit_days is not None else CONFIGURABLE_TRANSFER_TRANSIT_DAYS
    transfer_policies = [
        f"POL-INV-001: Zero-stock penalty requires investigating inter-facility re-allocation for projected stockouts within {POLICY_EMERGENCY_REALLOCATION_DAYS:.0f} days.",
        f"Configurable Assumption: Inter-warehouse transit time modeled at {transfer_transit_days:.1f} days with {CONFIGURABLE_TRANSFER_COST_RATE * 100:.0f}% handling fee."
    ]

    # Category B: Inspect active dataset for alternative facilities stocking the same SKU
    alt_locations = inv_df[(inv_df["sku_id"] == sku_id) & (inv_df["location_id"] != location_id)].copy()
    transfer_feasible = False
    transfer_source_loc: Optional[str] = None
    transfer_qty = 0.0
    transfer_cost = 0.0

    if alt_locations.empty:
        transfer_feasibility_reason = "No secondary warehouse or distribution facility exists in the active dataset for this SKU."
    else:
        # Calculate surplus above ROP at candidate facilities
        alt_locations["surplus"] = (alt_locations["current_stock"] - alt_locations["reorder_point"]).clip(lower=0)
        viable_sources = alt_locations[alt_locations["surplus"] > 0].sort_values(by="surplus", ascending=False)

        if viable_sources.empty:
            transfer_feasibility_reason = "Alternative facilities in dataset were evaluated, but none currently hold surplus inventory above their reorder point."
        else:
            best_source = viable_sources.iloc[0]
            transfer_source_loc = str(best_source["location_id"])
            available_surplus = float(best_source["surplus"])
            transfer_qty = float(math.ceil(min(final_reorder_qty, available_surplus)))

            if transfer_qty >= 1.0:
                transfer_feasible = True
                transfer_unit_cost = unit_cost * CONFIGURABLE_TRANSFER_COST_RATE
                transfer_cost = transfer_qty * transfer_unit_cost
                transfer_feasibility_reason = f"Facility '{transfer_source_loc}' has {available_surplus:.0f} units surplus available for transfer."
            else:
                transfer_feasibility_reason = f"Facility '{transfer_source_loc}' surplus is insufficient to fulfill a meaningful re-allocation."

    if transfer_feasible:
        transfer_stock_after = current_stock + transfer_qty
        transfer_dos_after = transfer_stock_after / projected_daily if projected_daily > 0 else 999.0
        transfer_risk_after = "NORMAL" if transfer_stock_after >= reorder_point else "STOCKOUT_RISK"
        transfer_reason = f"Re-allocate {transfer_qty:.0f} units from facility '{transfer_source_loc}' arriving in {transfer_transit_days:.0f} days at ₹{transfer_cost:,.0f} internal transit fee."
    else:
        transfer_stock_after = current_stock
        transfer_dos_after = current_dos
        transfer_risk_after = current_risk_str
        transfer_reason = "Inter-facility transfer cannot be executed."

    actions.append(CandidateAction(
        action_type=ActionType.TRANSFER_INVENTORY,
        sku_id=sku_id,
        quantity=transfer_qty,
        timing_days=0.0,
        arrival_days=transfer_transit_days if transfer_feasible else 0.0,
        expected_stock_after=round(transfer_stock_after, 1),
        expected_days_of_supply_after=round(transfer_dos_after, 1),
        expected_risk_level_after=transfer_risk_after,
        estimated_cost=round(transfer_cost, 2),
        unit_cost=round(unit_cost * CONFIGURABLE_TRANSFER_COST_RATE, 2),
        source_location_id=transfer_source_loc,
        destination_location_id=location_id,
        policy_constraints=transfer_policies,
        feasible=transfer_feasible,
        feasibility_reason=transfer_feasibility_reason,
        reason=transfer_reason,
        approval_tier=ApprovalTier.SUPPLY_CHAIN_MANAGER if transfer_feasible else ApprovalTier.NONE,
        is_baseline=False
    ))

    return CandidateActionSet(
        sku_id=sku_id,
        current_stock=current_stock,
        reorder_point=reorder_point,
        safety_stock=safety_stock,
        projected_daily_demand=projected_daily,
        current_days_of_supply=current_dos,
        current_risk_level=current_risk_str,
        actions=actions
    )


# ---------------------------------------------------------------------------
# PO Draft Recommendation Generator
# ---------------------------------------------------------------------------

def generate_po_draft(
    action: CandidateAction,
    approver_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a formal PO Draft recommendation artifact after decision review.
    IMPORTANT: This is an internal recommendation artifact only.
    It does NOT execute, submit, or transmit a purchase transaction to an external vendor.
    """
    if action.action_type not in [ActionType.REORDER, ActionType.EXPEDITE]:
        raise ValueError(f"Cannot generate a Purchase Order draft for non-procurement action '{action.action_type.value}'.")

    import hashlib
    hash_seed = f"{action.sku_id}-{action.quantity}-{action.estimated_cost}"
    po_suffix = hashlib.md5(hash_seed.encode()).hexdigest()[:6].upper()

    return {
        "artifact_type": "PURCHASE_ORDER_DRAFT_RECOMMENDATION",
        "po_number": f"PO-DRAFT-{action.sku_id}-{po_suffix}",
        "action_type": action.action_type.value,
        "sku_id": action.sku_id,
        "supplier_id": "PREFERRED_VENDOR (Unassigned in Dataset)",
        "destination_facility": action.destination_location_id or "PRIMARY_DC",
        "recommended_quantity": round(action.quantity, 0),
        "unit_cost": round(action.unit_cost, 2),
        "total_estimated_amount": round(action.estimated_cost, 2),
        "expected_lead_time_days": round(action.arrival_days, 1),
        "approval_status": "DRAFT_PENDING_HUMAN_APPROVAL",
        "approval_tier_required": action.approval_tier.value,
        "approver": approver_name,
        "policy_governance": action.policy_constraints,
        "automated_execution": False,
        "disclaimer": "This document is an AI-assisted procurement recommendation draft generated for human decision-maker review. External submission requires manual ERP transmission."
    }
