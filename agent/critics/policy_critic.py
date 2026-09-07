"""
agent/critics/policy_critic.py
Checks proposal against RAG policy docs using Groq.
"""
import json
from typing import Dict, Any, List, Optional
from llm.explainer import get_groq_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

def evaluate_policy_compliance(
    proposal: Dict[str, Any], 
    retrieved_policies: List[Dict[str, Any]], 
    client=None, 
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Evaluates whether the given proposal complies with the provided policies.
    Returns a dictionary with 'compliant' (bool) and 'notes' (str).
    """
    if not retrieved_policies:
        return {"compliant": True, "notes": "No specific policies retrieved to check against."}
        
    client = client or get_groq_client()
    
    prompt = f"""
You are a policy compliance critic. Read the proposal and the policies below, and determine if the proposal violates any of the policies.

Proposal:
{proposal}

Policies:
{retrieved_policies}

Respond strictly in JSON format with exactly these two keys:
"compliant": true if the proposal complies with all policies, false if it violates any.
"notes": A brief 1-2 sentence explanation of your decision.
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a policy critic. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=DEFAULT_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        # Ensure correct keys
        return {
            "compliant": bool(result.get("compliant", False)),
            "notes": str(result.get("notes", ""))
        }
    except Exception as e:
        return {"compliant": False, "notes": f"Critic evaluation failed: {str(e)}"}
