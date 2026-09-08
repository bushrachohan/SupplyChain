"""
agent/orchestrator.py
Genuine tool-calling agent loop using Groq.
"""
import json
from typing import Dict, Any, List
from groq import Groq
from llm.explainer import get_groq_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from agent.tools import TOOLS, TOOL_FUNCTIONS
from agent.decision_trace import DecisionTraceBuilder
from agent.critics.policy_critic import evaluate_policy_compliance
from agent.critics.business_critic import evaluate_business_impact
from agent.consensus import resolve_consensus

SYSTEM_PROMPT = """
You are a supply chain decision agent. You have access to various tools to assess inventory, predict delivery risks, optimize routes, retrieve policies, and evaluate candidate actions.
When given a scenario, you MUST use the provided tools to gather data. 
For inventory and replenishment scenarios, you MUST call `get_candidate_actions` to evaluate deterministic options (do_nothing, reorder, expedite, transfer_inventory).
You MUST select your final proposal from the feasible candidate actions evaluated by `get_candidate_actions`. You must NOT invent arbitrary actions or numerical values outside the deterministic candidate set.

After you have gathered enough data, you MUST provide a final proposal as a JSON string matching this exact schema:
{"proposal": {"action": "description of the action to take", "cost": 0, "reason": "brief reason"}}

Do NOT output this JSON until you have used the tools and gathered enough data.
You can call multiple tools in a single turn or sequentially.
"""

def run_agent_loop(situation: str, client: Groq = None) -> str:
    """
    Runs the agent tool-calling loop for a given situation, then passes the 
    result through the critics and persists the trace.
    Returns the trace ID.
    """
    client = client or get_groq_client()
    builder = DecisionTraceBuilder(inputs={"situation": situation})
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": situation}
    ]
    
    final_proposal = None
    
    # Tool execution loop
    for _ in range(10):  # max 10 iterations
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=DEFAULT_TEMPERATURE
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = TOOL_FUNCTIONS.get(function_name)
                
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(**function_args)
                    
                    builder.add_tool_call(function_name, function_args, function_response)
                    
                    if function_name == "retrieve_policies":
                        builder.policies_retrieved.extend(function_response)
                    elif function_name == "get_candidate_actions":
                        builder.options_considered = function_response
                        
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response),
                        }
                    )
        else:
            # Check if there is a final proposal in the message content
            content = response_message.content
            if content and '"proposal":' in content:
                try:
                    # Attempt to parse JSON proposal
                    parsed = json.loads(content)
                    final_proposal = parsed.get("proposal")
                    if final_proposal:
                        break
                except json.JSONDecodeError:
                    # If not strict JSON, just store as text
                    pass
            
            if final_proposal is None:
                # Fallback proposal
                final_proposal = {"action": content, "cost": 0, "reason": "Extracted from text"}
                break
                
    if not final_proposal:
        final_proposal = {"action": "None", "cost": 0, "reason": "Agent failed to produce a proposal."}
        
    # Ensure options_considered is populated if an SKU was evaluated
    if not builder.options_considered:
        import re
        from agent.tools import get_candidate_actions
        sku_matches = re.findall(r"(SKU[-_][A-Za-z0-9]+)", situation)
        if sku_matches:
            target_sku = sku_matches[0]
            cand_res = get_candidate_actions(target_sku)
            if "error" not in cand_res:
                builder.options_considered = cand_res
                
    builder.set_primary_proposal(final_proposal)
    
    # Run critics
    policy_res = evaluate_policy_compliance(final_proposal, builder.policies_retrieved, client=client)
    builder.set_policy_critic_output(policy_res)
    
    business_res = evaluate_business_impact(final_proposal)
    builder.set_business_critic_output(business_res)
    
    # Consensus
    consensus_res = resolve_consensus(final_proposal, policy_res, business_res)
    builder.set_consensus_result(consensus_res)
    
    # Persist
    trace_id = builder.persist()
    return trace_id
