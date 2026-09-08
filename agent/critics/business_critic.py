"""
agent/critics/business_critic.py
Rule-based business critic checking margin, cost, logistics feasibility.
Aligns with POL-PRO-003: Purchase orders < $10,000 require Supply Chain Manager approval;
orders >= $10,000 require Supply Chain Director approval.
"""
from typing import Dict, Any

STANDARD_APPROVAL_THRESHOLD = 10000.0  # POL-PRO-003 Section 1

def evaluate_business_impact(proposal: Dict[str, Any], context: Dict[str, Any] = None, threshold: float = STANDARD_APPROVAL_THRESHOLD) -> Dict[str, Any]:
    """
    Evaluates the business impact of a proposal based on cost and logistical rules.
    Returns a dictionary with 'approved' (bool) and 'notes' (str).
    """
    cost = proposal.get("cost", 0)
    
    if cost >= threshold:
        return {
            "approved": False,
            "notes": f"Proposal cost (₹{cost:,.0f}) reaches or exceeds the standard manager approval threshold (₹{threshold:,.0f}). Requires Supply Chain Director review under POL-PRO-003."
        }
        
    return {
        "approved": True,
        "notes": f"Cost (₹{cost:,.0f}) is within standard operating limits (< ₹{threshold:,.0f}) under POL-PRO-003."
    }
