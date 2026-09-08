from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from db.connection import get_db
from db.models import DecisionTrace, Recommendation, Approval
from agent.orchestrator import run_agent_loop

app = FastAPI(title="SupplyChain Sentinel AI API")

class OrchestrateRequest(BaseModel):
    situation: str

class OrchestrateResponse(BaseModel):
    trace_id: str

class ApprovalRequest(BaseModel):
    status: str
    approver: Optional[str] = None
    notes: Optional[str] = None

class TraceResponse(BaseModel):
    trace_id: str
    timestamp: datetime
    inputs: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None
    policies_retrieved: Optional[List[Dict[str, Any]]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    options_considered: Optional[Dict[str, Any]] = None
    primary_proposal: Optional[Dict[str, Any]] = None
    policy_critic_output: Optional[Dict[str, Any]] = None
    business_critic_output: Optional[Dict[str, Any]] = None
    consensus_result: Optional[Dict[str, Any]] = None
    human_approval: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendation_id: str
    created_at: datetime
    situation: str
    recommended_action: str
    llm_narration: Optional[str] = None
    status: str

    class Config:
        orm_mode = True
        from_attributes = True


@app.post("/api/orchestrate", response_model=OrchestrateResponse)
def orchestrate(request: OrchestrateRequest):
    """Run the multi-agent decision loop for a given situation."""
    try:
        trace_id = run_agent_loop(request.situation)
        return OrchestrateResponse(trace_id=trace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traces", response_model=List[TraceResponse])
def get_traces(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recent decision traces."""
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).offset(skip).limit(limit).all()
    return traces

@app.get("/api/traces/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Get a specific decision trace."""
    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace

@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(status: Optional[str] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recommendations, optionally filtered by status."""
    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)
    recommendations = query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
    return recommendations

@app.post("/api/traces/{trace_id}/approval")
def approve_trace(trace_id: str, request: ApprovalRequest, db: Session = Depends(get_db)):
    """Approve or reject a recommendation based on its trace ID."""
    if request.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Insert approval record
    approval = Approval(
        trace_id=trace_id,
        status=request.status,
        approver=request.approver,
        timestamp=datetime.utcnow(),
        notes=request.notes
    )
    db.add(approval)

    # Update Recommendation status
    rec.status = request.status

    # Update DecisionTrace human_approval dict
    current_approval = trace.human_approval or {}
    new_approval = current_approval.copy()
    new_approval["status"] = request.status
    new_approval["approver"] = request.approver
    new_approval["timestamp"] = datetime.utcnow().isoformat()
    new_approval["notes"] = request.notes
    trace.human_approval = new_approval

    # If approved, we might trigger execution here in a real system. 
    # The requirement says "Rejecting a recommendation does not mark it executed; approving does."
    # For now, we update the status. In Phase 4, "executed" outcome might be logged.

    db.commit()
    return {"message": f"Trace {trace_id} {request.status} successfully"}
