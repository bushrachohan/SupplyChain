"""
tests/test_decision_trace.py
Tests for agent/decision_trace.py
"""

from agent.decision_trace import DecisionTraceBuilder
from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation

def test_decision_trace_builder():
    builder = DecisionTraceBuilder(inputs={"sku_id": "SKU_101"})
    
    # Simulate a run
    builder.add_tool_call("get_demand_forecast", {"sku_id": "SKU_101"}, {"forecast_horizon_weeks": 4})
    builder.set_primary_proposal({"action": "Expedite shipment", "reason": "High risk of stockout"})
    builder.set_policy_critic_output({"compliant": True, "notes": "Matches safety stock policy"})
    builder.set_business_critic_output({"approved": True, "notes": "Cost justified"})
    builder.set_consensus_result({"recommendation": "Expedite shipment", "narration": "All critics agreed."})
    
    trace_id = builder.persist()
    
    # Verify in DB
    session = SessionLocal()
    try:
        trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        assert trace is not None
        assert trace.inputs == {"sku_id": "SKU_101"}
        assert len(trace.tools_used) == 1
        assert trace.human_approval["status"] == "pending"
        
        rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
        assert rec is not None
        assert rec.status == "pending"
    finally:
        # Cleanup
        if trace:
            session.delete(trace)
        if rec:
            session.delete(rec)
        session.commit()
        session.close()
