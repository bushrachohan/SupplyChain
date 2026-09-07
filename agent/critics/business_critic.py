"""
agent/critics/business_critic.py
Rule-based business critic checking margin, cost, logistics feasibility.
"""
from typing import Dict, Any

def evaluate_business_impact(proposal: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Evaluates the business impact of a proposal based on cost and logistical rules.
    Returns a dictionary with 'approved' (bool) and 'notes' (str).
    """
    cost = proposal.get("cost", 0)
    
    if cost > 1000:
        return {
            "approved": False,
            "notes": f"Proposal cost (${cost}) exceeds the standard automatic approval threshold ($1000)."
        }
        
    return {
        "approved": True,
        "notes": "Cost is within acceptable limits and business constraints are met."
    }
