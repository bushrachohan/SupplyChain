"""
agent/consensus.py
Resolves conflicts between the agent's primary proposal and the critics.
"""
from typing import Dict, Any

def resolve_consensus(
    primary_proposal: Dict[str, Any],
    policy_result: Dict[str, Any],
    business_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determines the final recommendation based on the primary proposal and the critics' verdicts.
    """
    is_compliant = policy_result.get("compliant", False)
    is_approved = business_result.get("approved", False)
    
    if is_compliant and is_approved:
        return {
            "recommendation": primary_proposal,
            "status": "APPROVED",
            "narration": "The proposal was approved by both policy and business critics."
        }
    else:
        rejection_reasons = []
        if not is_compliant:
            rejection_reasons.append(f"Policy Rejection: {policy_result.get('notes', 'Unknown')}")
        if not is_approved:
            rejection_reasons.append(f"Business Rejection: {business_result.get('notes', 'Unknown')}")
            
        return {
            "recommendation": None,
            "status": "REJECTED",
            "narration": " The proposal was rejected. " + " | ".join(rejection_reasons)
        }
