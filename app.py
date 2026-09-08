import streamlit as st
import json
from datetime import datetime
import time
import pandas as pd

from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation, Approval, InventoryRisk, DeliveryRiskPrediction, SKU
from agent.orchestrator import run_agent_loop
from data_ingestion.csv_source import CSVDataSource
from core.delivery_risk import train_delivery_risk_model
from core.simulation import (
    simulate_inventory_scenario,
    simulate_delivery_scenario,
    simulate_logistics_scenario
)

@st.cache_resource
def load_simulation_resources():
    source = CSVDataSource(data_dir="data")
    inv_df = source.load_inventory_snapshot()
    del_df = source.load_deliveries()
    model, _, _ = train_delivery_risk_model(del_df)
    return inv_df, del_df, model

st.set_page_config(page_title="SupplyChain Sentinel AI", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Enterprise Look ---
st.markdown("""
<style>
    /* Clean up the main padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Risk Badges */
    .badge-high { background-color: #ff4b4b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-medium { background-color: #ffa421; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-low { background-color: #00c04b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-neutral { background-color: #1e1e1e; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    
    /* Cards */
    .decision-card {
        border: 1px solid #444;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

def get_db_session():
    return SessionLocal()

# --- HELPER FUNCTIONS ---
def get_risk_badge(level: str):
    lvl = level.lower()
    if lvl in ["high", "critical", "stockout"]:
        return f"<span class='badge-high'>{level.upper()}</span>"
    elif lvl in ["medium", "warning", "overstock"]:
        return f"<span class='badge-medium'>{level.upper()}</span>"
    elif lvl in ["low", "ok", "passed", "approved"]:
        return f"<span class='badge-low'>{level.upper()}</span>"
    else:
        return f"<span class='badge-neutral'>{level.upper()}</span>"

# --- MAIN NAVIGATION ---
def main():
    st.sidebar.title("🛡️ SupplyChain Sentinel AI")
    st.sidebar.markdown("**AI Decision Intelligence**")
    st.sidebar.markdown("---")
    
    menu = ["Command Center", "Create a Decision", "Approval Queue", "Decision History", "What-If Simulation"]
    choice = st.sidebar.radio("Navigation", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("AI-powered supply-chain risk & decision intelligence platform.")
    st.sidebar.caption("© 2026 Sentinel Corp.")

    if choice == "Command Center":
        render_command_center()
    elif choice == "Create a Decision":
        render_create_decision()
    elif choice == "Approval Queue":
        render_approval_queue()
    elif choice == "Decision History":
        render_decision_history()
    elif choice == "What-If Simulation":
        render_simulation()

# --- VIEW: COMMAND CENTER ---
def render_command_center():
    st.title("Supply Chain Command Center")
    st.markdown("Monitor risk, evaluate decisions, and understand operational impact.")
    
    session = get_db_session()
    try:
        # Fetch actual metrics
        active_inventory_risks = session.query(InventoryRisk).filter(InventoryRisk.risk_flag != "ok").count()
        high_delivery_risks = session.query(DeliveryRiskPrediction).filter(DeliveryRiskPrediction.risk_label == "high").count()
        recent_decisions = session.query(DecisionTrace).count()
        
        # Calculate exposure (just a rough proxy summing unit_cost of at-risk SKUs if available, else placeholder)
        at_risk_skus = session.query(SKU).join(InventoryRisk).filter(InventoryRisk.risk_flag == "stockout").all()
        exposure = sum([sku.unit_cost * 100 for sku in at_risk_skus]) if at_risk_skus else 0
        exposure_str = f"₹{exposure:,.0f}" if exposure > 0 else "—"
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ACTIVE RISKS", active_inventory_risks, delta="Requires Attention", delta_color="inverse")
        col2.metric("INVENTORY AT RISK", exposure_str, delta="Potential Exposure", delta_color="off")
        col3.metric("DELIVERY RISK", high_delivery_risks, delta="Delayed Shipments", delta_color="inverse")
        col4.metric("AI DECISIONS", recent_decisions, delta="This Week", delta_color="normal")
        
        st.markdown("---")
        st.subheader("Priority Risks")
        
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("""
            <div class='decision-card'>
                <h4>🔴 HIGH RISK: SKU-104</h4>
                <p style="color: #bbb;">Electronics Component</p>
                <h3>Stockout Risk: 82%</h3>
                <p>Expected demand is exceeding available inventory coverage. Supplier lead-time increases exposure.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Review Decision →", key="btn_risk1"):
                st.info("Navigate to 'Approval Queue' to review pending AI decisions.")
                
        with r2:
            st.markdown("""
            <div class='decision-card'>
                <h4>🟠 DELIVERY RISK: Shipment #2048</h4>
                <p style="color: #bbb;">Carrier: Global Freight</p>
                <h3>High probability of delay</h3>
                <p>Supplier lead-time disruption detected at origin port.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Investigate →", key="btn_risk2"):
                st.info("Navigate to 'Create a Decision' to evaluate alternatives.")
                
    finally:
        session.close()

# --- VIEW: CREATE A DECISION ---
def render_create_decision():
    st.title("Create a Decision")
    st.markdown("Tell Sentinel what supply-chain situation you want to evaluate.")
    
    with st.container(border=True):
        st.subheader("BUSINESS CONTEXT")
        col1, col2 = st.columns(2)
        
        with col1:
            sku_input = st.text_input("Product / SKU ID", placeholder="e.g., SKU_101")
            inventory_input = st.number_input("Current Inventory (Units)", min_value=0, value=0, step=10)
        
        with col2:
            demand_input = st.text_input("Expected Demand Context", placeholder="e.g., Sudden spike in region B")
            supplier_input = st.text_input("Supplier / Lead Time Issues", placeholder="e.g., Delayed by 4 days")
            
        constraints = st.text_area("Additional Constraints or Context", placeholder="e.g., Must prioritize enterprise clients.")
    
    if st.button("Run AI Decision Analysis", type="primary", use_container_width=True):
        if not sku_input:
            st.warning("Please specify a Product / SKU ID to proceed.")
            return
            
        situation = f"SKU: {sku_input}. Inventory: {inventory_input}. Demand context: {demand_input}. Supplier info: {supplier_input}. Constraints: {constraints}"
        
        status_container = st.status("Initializing AI Analysis...", expanded=True)
        with status_container:
            st.write("Analyzing supply-chain data... ✓")
            time.sleep(0.5)
            st.write("Forecasting demand & assessing operational risk... ✓")
            time.sleep(0.5)
            st.write("Retrieving applicable policies... ✓")
            time.sleep(0.5)
            st.write("Generating candidate actions... ✓")
            
            try:
                trace_id = run_agent_loop(situation)
                st.write("Running independent reviews... ✓")
                time.sleep(0.5)
                st.write("Building consensus... ✓")
                status_container.update(label="Analysis Complete", state="complete", expanded=False)
                
                st.success(f"Decision created successfully (ID: {trace_id})")
                st.info("Please go to the **Approval Queue** to review the recommendation.")
            except Exception as e:
                status_container.update(label="Analysis Failed", state="error", expanded=True)
                st.error(f"Error during analysis: {str(e)}")

# --- VIEW: APPROVAL QUEUE ---
def render_approval_queue():
    st.title("Decision Approval Queue")
    st.markdown("AI-generated decisions waiting for human review.")
    
    session = get_db_session()
    try:
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        pending_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") == "pending"]
        
        if not pending_traces:
            st.success("All caught up! No pending recommendations require approval right now.")
            return
            
        for trace in pending_traces:
            with st.container(border=True):
                # Overview Header
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                c1.markdown(get_risk_badge("HIGH"), unsafe_allow_html=True)
                
                # Extract situation string cleanly
                sit_str = str(trace.inputs.get("situation", "Unknown Situation"))
                short_sit = sit_str[:50] + "..." if len(sit_str) > 50 else sit_str
                c2.markdown(f"**Issue:** {short_sit}")
                
                rec_action = trace.consensus_result.get("recommendation", "Review needed") if trace.consensus_result else "Review needed"
                if isinstance(rec_action, dict):
                    rec_action = rec_action.get("action", str(rec_action))
                c3.markdown(f"**Recommended Action:** {rec_action}")
                c4.markdown(f"*{trace.timestamp.strftime('%Y-%m-%d')}*")
                
                if st.button("Review Decision", key=f"rev_{trace.trace_id}"):
                    st.session_state[f"show_trace_{trace.trace_id}"] = not st.session_state.get(f"show_trace_{trace.trace_id}", False)
                
                if st.session_state.get(f"show_trace_{trace.trace_id}", False):
                    st.markdown("---")
                    render_detailed_decision(trace, is_pending=True)
                
    finally:
        session.close()

# --- REUSABLE COMPONENT: DETAILED DECISION RESULT ---
def render_detailed_decision(trace: DecisionTrace, is_pending: bool):
    # 1. AI Decision Header
    st.subheader("AI DECISION")
    
    rec_action = trace.consensus_result.get("recommendation", "Unknown") if trace.consensus_result else "Unknown"
    if isinstance(rec_action, dict):
        rec_action = rec_action.get("action", str(rec_action))
        
    narration = trace.consensus_result.get("narration", "No reasoning provided.") if trace.consensus_result else ""
    
    st.markdown(f"### RECOMMENDED ACTION: **{str(rec_action).upper()}**")
    
    st.markdown("**Why Sentinel recommends this:**")
    # Convert narration into pseudo bullet points if it's just a string, 
    # or just display it cleanly.
    st.write(narration)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Validation Flow
    st.subheader("Why should I trust this decision?")
    
    pol_status = "✓ PASSED" if trace.policy_critic_output and trace.policy_critic_output.get("compliant") else "⚠ NEEDS REVIEW"
    bus_status = "✓ PASSED" if trace.business_critic_output and trace.business_critic_output.get("approved") else "⚠ NEEDS REVIEW"
    
    vcol1, vcol2, vcol3, vcol4 = st.columns(4)
    vcol1.info(f"**Primary AI**\n\nProposed action formulated.")
    vcol2.warning(f"**Policy Review**\n\n{pol_status}")
    vcol3.success(f"**Business Review**\n\n{bus_status}")
    vcol4.info(f"**Consensus**\n\n✓ Validated")
    
    # 3. Decision Transparency (Technical Details Hidden)
    with st.expander("Decision Transparency (Technical Details)"):
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Data Considered**")
            st.json(trace.inputs)
            st.markdown("**AI Predictions**")
            st.json(trace.predictions if trace.predictions else {})
            st.markdown("**Policies Consulted**")
            st.json(trace.policies_retrieved if trace.policies_retrieved else [])
        with t2:
            st.markdown("**Evidence & Analysis (Tools)**")
            st.json(trace.tools_used if trace.tools_used else [])
            st.markdown("**Independent Review Logs**")
            st.json(trace.policy_critic_output if trace.policy_critic_output else {})
            st.json(trace.business_critic_output if trace.business_critic_output else {})
            
    # 4. Human Approval
    if is_pending:
        st.markdown("---")
        st.subheader("Human Approval Required")
        st.caption("This recommendation has been independently reviewed by multiple AI agents. No operational action will be taken without human approval.")
        
        with st.form(key=f"approval_{trace.trace_id}"):
            notes = st.text_area("Reviewer Notes (Optional)", placeholder="Looks good, proceed.")
            approver = st.text_input("Reviewer Name", value="System Admin")
            
            c1, c2, c3 = st.columns([1, 1, 4])
            approve_btn = c1.form_submit_button("✓ Approve Recommendation", type="primary")
            reject_btn = c2.form_submit_button("✕ Reject Recommendation")
            
            if approve_btn:
                process_approval(trace.trace_id, "approved", approver, notes)
                st.rerun()
            elif reject_btn:
                process_approval(trace.trace_id, "rejected", approver, notes)
                st.rerun()

def process_approval(trace_id: str, status: str, approver: str, notes: str):
    session = get_db_session()
    try:
        trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
        
        if trace and rec:
            approval = Approval(
                trace_id=trace_id,
                status=status,
                approver=approver,
                timestamp=datetime.utcnow(),
                notes=notes
            )
            session.add(approval)
            rec.status = status
            
            current_approval = trace.human_approval or {}
            new_approval = current_approval.copy()
            new_approval["status"] = status
            new_approval["approver"] = approver
            new_approval["timestamp"] = datetime.utcnow().isoformat()
            new_approval["notes"] = notes
            trace.human_approval = new_approval
            
            session.commit()
            if status == "approved":
                st.success("✓ Decision Approved: Recommendation approved by human reviewer.")
            else:
                st.error("✕ Decision Rejected: Decision returned for review.")
            time.sleep(1.5)
    except Exception as e:
        session.rollback()
        st.error(f"Error processing approval: {e}")
    finally:
        session.close()

# --- VIEW: DECISION HISTORY ---
def render_decision_history():
    st.title("Decision History")
    st.markdown("Audit trail of approved and rejected decisions.")
    
    session = get_db_session()
    try:
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        history_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") in ["approved", "rejected"]]
        
        if not history_traces:
            st.info("No historical decisions found.")
            return
            
        for trace in history_traces:
            status = trace.human_approval.get("status", "unknown").upper()
            sit_str = str(trace.inputs.get("situation", ""))
            short_sit = sit_str[:60] + "..." if len(sit_str) > 60 else sit_str
            rec_action = trace.consensus_result.get("recommendation", "Unknown") if trace.consensus_result else "Unknown"
            if isinstance(rec_action, dict):
                rec_action = rec_action.get("action", str(rec_action))
            date_str = trace.timestamp.strftime('%Y-%m-%d %H:%M')
            
            with st.expander(f"{date_str} | {status} | {short_sit}"):
                st.markdown(f"**Status:** {get_risk_badge(status)}", unsafe_allow_html=True)
                st.markdown(f"**Recommendation:** {rec_action}")
                st.markdown(f"**Reviewer:** {trace.human_approval.get('approver')} | **Notes:** {trace.human_approval.get('notes')}")
                st.markdown("---")
                render_detailed_decision(trace, is_pending=False)
    finally:
        session.close()

# --- VIEW: WHAT-IF SIMULATION (Phase 4) ---
def render_simulation():
    st.title("What-If Simulation & Business Intelligence")
    st.markdown("Stress-test supply-chain operations under shifting market conditions, disruptions, and capacity constraints.")
    
    st.markdown("""
    <div style="background-color: #1a1a2e; border: 1px solid #30363d; border-radius: 8px; padding: 12px 18px; margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #c9d1d9; font-weight: 500;">
            <span>🔍 <b>1. Identify Operational Risk</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>⚙️ <b>2. Configure Stress Test Overrides</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>📊 <b>3. Compare Baseline vs. Scenario</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>🛡️ <b>4. Evaluate Action Delta (Do Nothing vs. Act)</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    inv_df, del_df, delivery_model = load_simulation_resources()
    
    sim_mode = st.selectbox(
        "Select Simulation Domain",
        ["📦 Inventory Risk & Stockout", "🚚 Delivery Risk & Transit Delay", "🗺️ Logistics Fleet & Routing Capacity"],
        key="sim_mode_selector"
    )
    st.markdown("---")

    if sim_mode == "📦 Inventory Risk & Stockout":
        st.subheader("📦 Inventory Stress-Testing: Demand Shocks & Supplier Delays")
        st.markdown("Simulate how demand spikes or supplier lead time extensions impact Days of Supply and Stockout exposure.")
        
        sku_options = inv_df["sku_id"].tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="inv_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_sku = st.selectbox("Select Target SKU", sku_options, index=0)
                sku_row = inv_df[inv_df["sku_id"] == selected_sku].iloc[0]
                
                base_stock = float(sku_row.get("current_stock", 100.0))
                base_lead_time = float(sku_row.get("lead_time_days", 7.0))
                unit_cost = float(sku_row.get("unit_cost", 50.0))
                
                st.caption(f"Baseline: Stock = **{base_stock:.0f} units** | Lead Time = **{base_lead_time:.0f} days** | Unit Cost = **₹{unit_cost:.2f}**")
                
                demand_mult = st.slider(
                    "Demand Surge Multiplier",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    help="1.0 = baseline demand, 1.5 = 50% surge, 2.0 = 100% surge"
                )
                
                stock_override_opt = st.checkbox("Override Current On-Hand Stock?", value=False)
                stock_override = None
                if stock_override_opt:
                    stock_override = st.number_input("Adjusted Stock (units)", min_value=0.0, max_value=5000.0, value=base_stock, step=10.0)
                    
                lead_override_opt = st.checkbox("Override Supplier Lead Time?", value=False)
                lead_time_override = None
                if lead_override_opt:
                    lead_time_override = st.slider("Adjusted Lead Time (days)", min_value=1.0, max_value=45.0, value=float(base_lead_time), step=1.0)
                    
                run_inv = st.form_submit_button("⚡ Run Inventory Simulation", type="primary")

        with col_results:
            st.markdown("#### Projected Business Impact")
            base_daily = max(1.0, base_stock / 15.0)
            base_forecast_14d = base_daily * 14.0
            
            sim_res = simulate_inventory_scenario(
                sku_id=selected_sku,
                base_current_stock=base_stock,
                base_avg_daily_demand=base_daily,
                base_forecast_demand=base_forecast_14d,
                base_forecast_period_days=14,
                base_lead_time_days=base_lead_time,
                base_safety_stock_days=14.0,
                demand_multiplier=demand_mult,
                stock_override=stock_override,
                lead_time_override=lead_time_override,
            )
            
            before = sim_res["before"]
            after = sim_res["after"]
            deltas = sim_res["deltas"]
            
            m1, m2, m3 = st.columns(3)
            dos_delta = deltas["days_of_supply_delta"]
            m1.metric("Days of Supply", f"{after['days_of_supply']:.1f} d", delta=f"{dos_delta:+.1f} d", delta_color="normal" if dos_delta >= 0 else "inverse")
            
            rop_delta = deltas["reorder_point_delta"]
            m2.metric("Reorder Point", f"{after['reorder_point_units']:.0f} u", delta=f"{rop_delta:+.0f} u", delta_color="inverse" if rop_delta > 0 else "normal")
            
            m3.markdown(f"**Risk Level**<br>{get_risk_badge(before['risk_level'])} ➔ {get_risk_badge(after['risk_level'])}", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### Detailed Metric Breakdown")
            comp_data = {
                "Metric": ["Current Stock (units)", "Lead Time (days)", "Avg Daily Demand (units/d)", "14-Day Demand Forecast (units)", "Days of Supply (days)", "Reorder Point (units)", "Operational Risk Status"],
                "Baseline State": [
                    f"{before['current_stock']:.0f}",
                    f"{before['lead_time_days']:.0f}",
                    f"{before['avg_daily_demand']:.1f}",
                    f"{before['forecasted_demand']:.1f}",
                    f"{before['days_of_supply']:.1f}",
                    f"{before['reorder_point_units']:.1f}",
                    before['risk_level'].upper()
                ],
                "Scenario State": [
                    f"{after['current_stock']:.0f}",
                    f"{after['lead_time_days']:.0f}",
                    f"{after['avg_daily_demand']:.1f}",
                    f"{after['forecasted_demand']:.1f}",
                    f"{after['days_of_supply']:.1f}",
                    f"{after['reorder_point_units']:.1f}",
                    after['risk_level'].upper()
                ],
                "Observed Delta": [
                    f"{after['current_stock'] - before['current_stock']:+.0f}",
                    f"{after['lead_time_days'] - before['lead_time_days']:+.0f}",
                    f"{after['avg_daily_demand'] - before['avg_daily_demand']:+.1f}",
                    f"{after['forecasted_demand'] - before['forecasted_demand']:+.1f}",
                    f"{deltas['days_of_supply_delta']:+.1f}",
                    f"{deltas['reorder_point_delta']:+.1f}",
                    "CHANGED ⚠️" if deltas["risk_level_changed"] else "UNCHANGED"
                ]
            }
            st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)
            
            st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                st.error(f"""
                **❌ Do Nothing Scenario**
                - Buffer depleted within **{after['days_of_supply']:.1f} days**.
                - Stockout penalty incurred; customer fulfillments backlogged.
                - Operational exposure of approx **₹{base_stock * unit_cost:,.0f}**.
                """)
            with a_col2:
                reorder_qty = max(0.0, after['reorder_point_units'] - after['current_stock'])
                st.success(f"""
                **✅ Recommended Action (AI Decision)**
                - Issue replenishment PO for **{reorder_qty:.0f} units**.
                - Enforce expedited supplier dispatch to hold lead time to **{after['lead_time_days']:.0f} days**.
                - Preserves service level stability and eliminates stockout penalty.
                """)

    elif sim_mode == "🚚 Delivery Risk & Transit Delay":
        st.subheader("🚚 Delivery Risk: Severe Weather & Traffic Bottlenecks")
        st.markdown("Simulate how severe weather disruptions or extreme highway congestion elevate delivery delay probability.")
        
        delivery_ids = del_df["delivery_id"].tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="del_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_del = st.selectbox("Select Target Delivery ID", delivery_ids, index=0)
                del_row = del_df[del_df["delivery_id"] == selected_del].iloc[0]
                
                carrier = del_row.get("carrier_id", "Unknown")
                origin = del_row.get("origin", "Depot")
                dest = del_row.get("destination", "Retail")
                distance = float(del_row.get("distance_km", 100))
                base_weather = str(del_row.get("weather_condition", "CLEAR"))
                base_traffic = float(del_row.get("traffic_delay_hrs", 0.0))
                
                st.caption(f"Route: **{origin} ➔ {dest}** ({distance:.0f} km) | Carrier: **{carrier}**")
                st.caption(f"Baseline Weather: **{base_weather}** | Baseline Traffic Delay: **{base_traffic:.1f} hrs**")
                
                weather_options = ["CLEAR", "RAIN", "FOG", "STORM"]
                w_idx = weather_options.index(base_weather) if base_weather in weather_options else 0
                weather_override = st.selectbox("Simulate Weather Condition", weather_options, index=w_idx)
                traffic_override = st.slider("Simulate Traffic Delay (Hours)", min_value=0.0, max_value=12.0, value=float(base_traffic), step=0.5)
                
                run_del = st.form_submit_button("⚡ Run Delivery Simulation", type="primary")
                
        with col_results:
            st.markdown("#### Projected Business Impact")
            sim_res = simulate_delivery_scenario(
                model=delivery_model,
                df_deliveries=del_df,
                delivery_id=selected_del,
                traffic_delay_override=traffic_override,
                weather_condition_override=weather_override
            )
            
            before = sim_res["before"]
            after = sim_res["after"]
            deltas = sim_res["deltas"]
            
            m1, m2 = st.columns(2)
            score_delta = deltas["risk_score_delta"]
            m1.metric("Late Delivery Probability", f"{after['risk_score']*100:.1f}%", delta=f"{score_delta*100:+.1f}%", delta_color="inverse" if score_delta > 0 else "normal")
            m2.markdown(f"**Risk Classification**<br>{get_risk_badge(before['risk_label'])} ➔ {get_risk_badge(after['risk_label'])}", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### ML Driving Risk Factors (SHAP Explanation)")
            top_feats = after.get("top_features", {})
            if top_feats:
                feat_df = pd.DataFrame([{"Feature": k, "Impact Score (SHAP)": f"{v:+.4f}"} for k, v in top_feats.items()])
                st.dataframe(feat_df, hide_index=True, use_container_width=True)
                
            st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                st.error("""
                **❌ Do Nothing Scenario**
                - Shipment stuck in severe weather / congestion corridor.
                - Promised delivery window missed by estimated delay duration.
                - On-time delivery SLA breach penalty applied.
                """)
            with a_col2:
                st.success("""
                **✅ Recommended Action (AI Decision)**
                - Reroute shipment via alternate regional bypass to circumvent bottlenecks.
                - Pre-notify receiving facility for dynamic cross-dock priority staging.
                - If delay estimate exceeds 4 hours, dispatch emergency courier unit.
                """)

    elif sim_mode == "🗺️ Logistics Fleet & Routing Capacity":
        st.subheader("🗺️ Logistics Routing: Fleet Capacity & Vehicle Constraints")
        st.markdown("Simulate how fleet availability and vehicle payload capacity affect route efficiency and fuel costs.")
        
        all_dels = del_df["delivery_id"].head(8).tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="log_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_dels = st.multiselect("Select Deliveries to Route", all_dels, default=all_dels[:5])
                
                num_vehicles = st.slider("Available Delivery Vehicles", min_value=1, max_value=5, value=2, step=1)
                capacity_mult = st.slider("Vehicle Payload Capacity Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1, help="Adjust capacity limit per vehicle (1.0 = standard 500kg capacity)")
                
                run_log = st.form_submit_button("⚡ Run Routing Simulation", type="primary")
                
        with col_results:
            st.markdown("#### Projected Business Impact")
            if not selected_dels:
                st.warning("Please select at least 1 delivery to route.")
            else:
                base_constraints = {"num_vehicles": 2, "capacities": [500] * 2}
                del_records = del_df[del_df["delivery_id"].isin(selected_dels)].to_dict(orient="records")
                for d in del_records:
                    if "weight" not in d:
                        d["weight"] = 100
                        
                sim_res = simulate_logistics_scenario(
                    delivery_ids=selected_dels,
                    df_deliveries=del_records,
                    base_vehicle_constraints=base_constraints,
                    capacity_multiplier=capacity_mult,
                    num_vehicles_override=num_vehicles
                )
                
                before = sim_res["before"]
                after = sim_res["after"]
                deltas = sim_res["deltas"]
                
                if after.get("status") != "Success":
                    st.warning(f"⚠️ Routing Constraint Alert: {after.get('status', 'No solution found')}. Fleet capacity is insufficient to deliver all assigned shipments. Increase vehicle count or payload multiplier.")
                else:
                    m1, m2, m3 = st.columns(3)
                    dist_delta = deltas["total_distance_delta"]
                    cost_delta = deltas["total_cost_delta"]
                    
                    m1.metric("Total Transit Distance", f"{after.get('total_distance_km', 0):.0f} km", delta=f"{dist_delta:+.0f} km", delta_color="inverse" if dist_delta > 0 else "normal")
                    m2.metric("Estimated Route Cost", f"₹{after.get('total_cost', 0):,.0f}", delta=f"₹{cost_delta:+,.0f}", delta_color="inverse" if cost_delta > 0 else "normal")
                    m3.metric("Dispatched Routes", f"{len(after.get('routes', []))} vehicles", delta=f"{len(after.get('routes', [])) - len(before.get('routes', [])):+d} vs Base")
                    
                    st.markdown("---")
                    st.markdown("##### Optimized Vehicle Allocations")
                    for r in after.get("routes", []):
                        stops_str = " ➔ ".join([s["delivery_id"] for s in r["stops"]])
                        st.markdown(f"**Vehicle #{r['vehicle_id'] + 1}:** {stops_str} *(Distance: {r['route_distance_km']} km | Load: {r['route_load']} kg)*")
                        
                st.markdown("---")
                st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
                a_col1, a_col2 = st.columns(2)
                with a_col1:
                    st.error("""
                    **❌ Do Nothing (Fixed / Unoptimized Dispatch)**
                    - Underutilized vehicles run redundant cross-city mileage.
                    - Overloaded vehicles risk breakdown or safety compliance breach.
                    """)
                with a_col2:
                    st.success("""
                    **✅ Recommended Action (VRP Optimization)**
                    - Re-cluster shipments into optimal density zones.
                    - Minimize total fleet transit kilometers and driver overtime expenses.
                    """)

if __name__ == "__main__":
    main()
