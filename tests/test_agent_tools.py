"""
tests/test_agent_tools.py
Tests for agent/tools.py — verifying the tool wrappers and Groq schemas.
"""

import pytest
from agent.tools import (
    TOOLS,
    TOOL_FUNCTIONS,
    get_demand_forecast,
    get_inventory_risk,
    get_delivery_risk,
    optimize_routes,
    retrieve_policies
)

def test_tools_schema_format():
    """Verify that all tools in TOOLS follow the Groq/OpenAI function calling schema."""
    assert isinstance(TOOLS, list)
    assert len(TOOLS) == 5
    
    for tool in TOOLS:
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
        assert tool["function"]["parameters"]["type"] == "object"
        assert "properties" in tool["function"]["parameters"]

def test_tool_functions_mapping():
    """Verify all TOOLS are mapped in TOOL_FUNCTIONS."""
    schema_names = [tool["function"]["name"] for tool in TOOLS]
    assert set(schema_names) == set(TOOL_FUNCTIONS.keys())

# Note: Integration-style tests that actually call the underlying models 
# to ensure the wrappers pass data correctly.

def test_get_demand_forecast():
    res = get_demand_forecast("SKU_101")
    assert "error" not in res
    assert res["sku_id"] == "SKU_101"
    assert "predicted_quantities" in res

def test_get_inventory_risk():
    res = get_inventory_risk("SKU_101")
    assert "error" not in res
    assert "risk_level" in res
    assert "sku_id" in res

def test_get_delivery_risk():
    res = get_delivery_risk("DEL_050")
    assert "error" not in res
    assert "risk_score" in res
    assert "top_features" in res

def test_optimize_routes():
    res = optimize_routes(["DEL_001", "DEL_002"], {"num_vehicles": 1, "capacities": [500]})
    assert "error" not in res
    assert res["status"] == "Success"
    assert "routes" in res

def test_retrieve_policies():
    res = retrieve_policies("safety stock")
    assert isinstance(res, list)
    # the exact content depends on ChromaDB, so we just verify it doesn't crash
