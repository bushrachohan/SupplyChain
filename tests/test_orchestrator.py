"""
tests/test_orchestrator.py
Tests for agent/orchestrator.py
"""
import pytest
from unittest.mock import MagicMock
from agent.orchestrator import run_agent_loop
from agent.decision_trace import DecisionTraceBuilder
from db.connection import SessionLocal

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

class MockChatCompletions:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        
    def create(self, **kwargs):
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp

class MockGroqClient:
    def __init__(self, responses):
        self.chat = MagicMock()
        self.chat.completions = MockChatCompletions(responses)

def test_orchestrator_loop():
    # Simulate Groq output: 
    # 1. Ask for a tool call (get_inventory_risk)
    # 2. Return final proposal
    
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "get_inventory_risk"
    mock_tool_call.function.arguments = '{"sku_id": "SKU_101"}'
    
    responses = [
        MockResponse([MockChoice(MockMessage(None, [mock_tool_call]))]),
        MockResponse([MockChoice(MockMessage('{"proposal": {"action": "Expedite", "cost": 100, "reason": "Low stock"}}'))])
    ]
    
    client = MockGroqClient(responses)
    
    # We must also mock the policy critic to not make a network call since client is used there
    trace_id = run_agent_loop("Check SKU_101", client=client)
    
    assert trace_id.startswith("TRACE_")
    
    # Clean up from DB
    session = SessionLocal()
    from db.models import DecisionTrace, Recommendation
    trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
    if trace:
        session.delete(trace)
    if rec:
        session.delete(rec)
    session.commit()
    session.close()
