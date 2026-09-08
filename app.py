import streamlit as st
import json
from datetime import datetime
from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation, Approval
from agent.orchestrator import run_agent_loop

# Must be the first Streamlit command
st.set_page_config(page_title="SupplyChain Sentinel AI", layout="wide")

def get_db_session():
    return SessionLocal()

def main():
    st.title("🛡️ SupplyChain Sentinel AI")
    st.markdown("### Human-in-the-Loop Decision Intelligence Dashboard")

    menu = ["Pending Approvals", "New Decision", "Decision History"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "New Decision":
        show_new_decision()
    elif choice == "Pending Approvals":
        show_pending_approvals()
    elif choice == "Decision History":
        show_history()

def show_new_decision():
    st.header("Trigger New AI Agent Decision")
    situation = st.text_area("Describe the Situation:", "e.g., SKU_101 is predicted to have a stockout soon.")
    
    if st.button("Run AI Agent"):
        if not situation.strip():
            st.warning("Please enter a situation.")
            return
            
        with st.spinner("AI Agent is analyzing data, consulting tools, and deliberating..."):
            try:
                trace_id = run_agent_loop(situation)
                st.success(f"Orchestration complete! Created trace: {trace_id}")
                st.info("Check 'Pending Approvals' to review the decision trace and approve/reject.")
            except Exception as e:
                st.error(f"Error running agent: {str(e)}")

def render_decision_trace(trace: DecisionTrace, is_pending: bool = True):
    st.markdown(f"**Trace ID:** `{trace.trace_id}` | **Generated:** `{trace.timestamp}`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📝 Initial Situation (Inputs)", expanded=True):
            st.json(trace.inputs)
            
        with st.expander("📊 Predictions & Risk Scores"):
            st.json(trace.predictions if trace.predictions else {})
            
        with st.expander("📖 Policies Retrieved (RAG)"):
            if trace.policies_retrieved:
                for idx, policy in enumerate(trace.policies_retrieved):
                    st.markdown(f"**Policy {idx+1}**")
                    st.json(policy)
            else:
                st.info("No policies were retrieved.")

    with col2:
        with st.expander("🛠️ Tools Used by Agent"):
            if trace.tools_used:
                for idx, tool in enumerate(trace.tools_used):
                    st.markdown(f"**Step {idx+1}:** `{tool.get('tool')}`")
                    st.json({"args": tool.get('args'), "result": tool.get('result')})
            else:
                st.info("No tools were called.")
                
    st.markdown("---")
    st.subheader("Multi-Agent Critique & Consensus")
    
    cr_col1, cr_col2, cr_col3 = st.columns(3)
    
    with cr_col1:
        st.info("🧠 **Primary Proposal**")
        st.json(trace.primary_proposal if trace.primary_proposal else {})
        
    with cr_col2:
        st.warning("🛡️ **Policy Critic Output**")
        st.json(trace.policy_critic_output if trace.policy_critic_output else {})
        
    with cr_col3:
        st.success("💰 **Business Critic Output**")
        st.json(trace.business_critic_output if trace.business_critic_output else {})
        
    st.markdown("### 🤝 Consensus Result")
    st.write(trace.consensus_result)

    if is_pending:
        st.markdown("---")
        st.subheader("👤 Human Approval Gate")
        
        with st.form(key=f"approval_form_{trace.trace_id}"):
            notes = st.text_input("Approver Notes:")
            approver = st.text_input("Approver Name:", value="System Admin")
            
            c1, c2, c3 = st.columns([1, 1, 4])
            approve_btn = c1.form_submit_button("✅ Approve")
            reject_btn = c2.form_submit_button("❌ Reject")
            
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
            st.success(f"Recommendation {status.upper()} successfully!")
            
            if status == "approved":
                # Phase 4 placeholder
                st.info("Simulation mode activated. Business-impact simulation would be shown here.")
    except Exception as e:
        session.rollback()
        st.error(f"Error processing approval: {e}")
    finally:
        session.close()

def show_pending_approvals():
    st.header("Pending Approvals")
    
    session = get_db_session()
    try:
        # We need to find traces where human_approval->>'status' == 'pending'
        # To keep it DB agnostic for SQLite/Postgres in dev, we can pull all and filter in memory if few, 
        # or use SQLAlchemy JSON filters. Since it's an MVP, fetching and filtering is safe.
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        pending_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") == "pending"]
        
        if not pending_traces:
            st.info("No pending recommendations require approval right now.")
            return
            
        for trace in pending_traces:
            with st.container():
                st.markdown(f"### Trace: {trace.trace_id}")
                render_decision_trace(trace, is_pending=True)
                st.markdown("<br><br>", unsafe_allow_html=True)
                
    finally:
        session.close()

def show_history():
    st.header("Decision History")
    
    session = get_db_session()
    try:
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        history_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") in ["approved", "rejected"]]
        
        if not history_traces:
            st.info("No historical decisions found.")
            return
            
        for trace in history_traces:
            status = trace.human_approval.get("status", "unknown").upper()
            color = "green" if status == "APPROVED" else "red"
            st.markdown(f"### <span style='color:{color}'>{status}</span> Trace: {trace.trace_id}", unsafe_allow_html=True)
            with st.expander(f"View details for {trace.trace_id}"):
                render_decision_trace(trace, is_pending=False)
                st.markdown(f"**Processed by:** {trace.human_approval.get('approver')} | **Notes:** {trace.human_approval.get('notes')}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
