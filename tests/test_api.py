import sys
sys.path.insert(0, '.')

import pytest
from fastapi.testclient import TestClient
from api.main import app
from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation, Approval
from agent.decision_trace import DecisionTraceBuilder
import uuid

client = TestClient(app)

def test_get_traces():
    response = client.get("/api/traces?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_recommendations():
    response = client.get("/api/recommendations?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_orchestrate_and_approval(monkeypatch):
    # Mock run_agent_loop to just return a dummy trace ID after inserting it
    def mock_run_agent_loop(situation):
        builder = DecisionTraceBuilder(inputs={"situation": situation})
        builder.set_primary_proposal({"action": "Test Action", "reason": "Test"})
        builder.set_consensus_result({"recommendation": "Test Action", "narration": "Test"})
        return builder.persist()
        
    monkeypatch.setattr("api.main.run_agent_loop", mock_run_agent_loop)
    
    # 1. Orchestrate
    orch_response = client.post("/api/orchestrate", json={"situation": "Stock is low"})
    assert orch_response.status_code == 200
    trace_id = orch_response.json()["trace_id"]
    assert trace_id.startswith("TRACE_")
    
    try:
        # 2. Get Trace
        trace_response = client.get(f"/api/traces/{trace_id}")
        assert trace_response.status_code == 200
        assert trace_response.json()["trace_id"] == trace_id
        assert trace_response.json()["inputs"]["situation"] == "Stock is low"
        
        # 3. Approve Trace
        appr_response = client.post(f"/api/traces/{trace_id}/approval", json={
            "status": "approved",
            "approver": "Test User",
            "notes": "Looks good"
        })
        assert appr_response.status_code == 200
        
        # 4. Verify Approval in DB
        session = SessionLocal()
        trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        assert trace.human_approval["status"] == "approved"
        assert trace.human_approval["approver"] == "Test User"
        
        rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
        assert rec.status == "approved"
        
        approval = session.query(Approval).filter(Approval.trace_id == trace_id).first()
        assert approval.status == "approved"
        assert approval.approver == "Test User"
        
    finally:
        # Cleanup
        session = SessionLocal()
        approval = session.query(Approval).filter(Approval.trace_id == trace_id).first()
        if approval:
            session.delete(approval)
            
        trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        if trace:
            session.delete(trace)
            
        rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
        if rec:
            session.delete(rec)
            
        session.commit()
        session.close()

def test_approve_invalid_status():
    response = client.post("/api/traces/FAKE_TRACE/approval", json={
        "status": "invalid_status"
    })
    assert response.status_code == 400
    assert "must be 'approved' or 'rejected'" in response.json()["detail"]
