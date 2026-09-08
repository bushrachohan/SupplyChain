"""
tests/test_critics.py
Tests for agent critics and consensus.
"""
from agent.critics.business_critic import evaluate_business_impact
from agent.consensus import resolve_consensus

def test_evaluate_business_impact():
    res1 = evaluate_business_impact({"cost": 5000})
    assert res1["approved"] is True
    
    res2 = evaluate_business_impact({"cost": 15000})
    assert res2["approved"] is False

def test_resolve_consensus():
    proposal = {"action": "Expedite"}
    
    res = resolve_consensus(
        proposal,
        {"compliant": True, "notes": "OK"},
        {"approved": True, "notes": "OK"}
    )
    assert res["status"] == "APPROVED"
    assert res["recommendation"] == proposal
    
    res_rej = resolve_consensus(
        proposal,
        {"compliant": False, "notes": "Violates safety stock."},
        {"approved": True, "notes": "OK"}
    )
    assert res_rej["status"] == "REJECTED"
    assert res_rej["recommendation"] is None
