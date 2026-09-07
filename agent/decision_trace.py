"""
agent/decision_trace.py
Builds and persists the full decision trace to the database.
"""

from typing import Dict, Any, Optional
import uuid
import json
from datetime import datetime
from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation

class DecisionTraceBuilder:
    def __init__(self, inputs: Dict[str, Any]):
        self.trace_id = f"TRACE_{uuid.uuid4().hex[:8].upper()}"
        self.inputs = inputs
        self.predictions = {}
        self.policies_retrieved = []
        self.tools_used = []
        self.options_considered = {}
        self.primary_proposal = {}
        self.policy_critic_output = {}
        self.business_critic_output = {}
        self.consensus_result = {}
        self.human_approval = {"status": "pending", "approver": None, "timestamp": None, "notes": ""}
        self.outcome = {}
        
    def add_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any):
        """Record a tool call in the trace."""
        self.tools_used.append({
            "tool": tool_name,
            "args": args,
            "result": result
        })
        
    def add_prediction(self, key: str, value: Any):
        self.predictions[key] = value
        
    def set_primary_proposal(self, proposal: Dict[str, Any]):
        self.primary_proposal = proposal
        
    def set_policy_critic_output(self, output: Dict[str, Any]):
        self.policy_critic_output = output
        
    def set_business_critic_output(self, output: Dict[str, Any]):
        self.business_critic_output = output
        
    def set_consensus_result(self, result: Dict[str, Any]):
        self.consensus_result = result
        
    def persist(self) -> str:
        """Persist the full trace and create a pending recommendation to the database."""
        session = SessionLocal()
        try:
            trace = DecisionTrace(
                trace_id=self.trace_id,
                inputs=self.inputs,
                predictions=self.predictions,
                policies_retrieved=self.policies_retrieved,
                tools_used=self.tools_used,
                options_considered=self.options_considered,
                primary_proposal=self.primary_proposal,
                policy_critic_output=self.policy_critic_output,
                business_critic_output=self.business_critic_output,
                consensus_result=self.consensus_result,
                human_approval=self.human_approval,
                outcome=self.outcome
            )
            session.add(trace)
            
            # Also create a Recommendation record tied to this trace
            rec = Recommendation(
                recommendation_id=f"REC_{self.trace_id}",
                situation=json.dumps(self.inputs),
                recommended_action=json.dumps(self.consensus_result.get("recommendation", {})),
                llm_narration=self.consensus_result.get("narration", ""),
                status="pending"
            )
            session.add(rec)
            
            session.commit()
            return self.trace_id
        finally:
            session.close()

