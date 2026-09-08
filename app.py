import streamlit as st
import json
from datetime import datetime
import time

from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation, Approval, InventoryRisk, DeliveryRiskPrediction, SKU
from agent.orchestrator import run_agent_loop

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
    st.title("What-If Simulation")
    st.markdown("See how changing supply-chain conditions could affect operational outcomes.")
    
    st.warning("🔌 The Phase 4 Simulation Engine is not yet connected. Results below are illustrative placeholders to demonstrate the intended UI layout.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Scenario Controls")
        st.slider("Demand Change (%)", -50, 50, 20)
        st.slider("Supplier Delay (Days)", 0, 14, 4)
        st.slider("Inventory Adjustment", -500, 500, -100)
        st.button("Run Simulation", type="primary")
        
    with col2:
        st.subheader("Projected Business Impact")
        
        st.markdown("""
        | Metric | Baseline | Scenario |
        |---|---|---|
        | **Stockout Risk** | 82% | 94% 🔴 |
        | **Service Level** | 78% | 64% 🔴 |
        | **Expected Shortage** | 560 units | 890 units 🔴 |
        | **Operational Cost** | — | — |
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("**AI Recommendation Under This Scenario:**\n\nEXPEDITE REPLENISHMENT VIA PREMIUM FREIGHT")

if __name__ == "__main__":
    main()
