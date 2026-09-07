"""
tests/test_logistics_optimizer.py
Tests for core/logistics_optimizer.py (OR-Tools VRP)
"""

import pytest
from core.logistics_optimizer import optimize_routes, create_data_model

def test_create_data_model():
    deliveries = [
        {"delivery_id": "D1", "distance_km": 10, "weight": 50},
        {"delivery_id": "D2", "distance_km": 20, "weight": 30},
    ]
    data = create_data_model(deliveries, num_vehicles=2, vehicle_capacities=[100, 100])
    
    assert data["num_vehicles"] == 2
    assert data["vehicle_capacities"] == [100, 100]
    assert data["depot"] == 0
    # Demands should be [0 (depot), 50, 30]
    assert data["demands"] == [0, 50, 30]
    # Matrix should be 3x3
    assert len(data["distance_matrix"]) == 3
    assert len(data["distance_matrix"][0]) == 3

def test_optimize_routes_success():
    deliveries = [
        {"delivery_id": "D1", "distance_km": 10, "weight": 50},
        {"delivery_id": "D2", "distance_km": 15, "weight": 60},
        {"delivery_id": "D3", "distance_km": 20, "weight": 40},
    ]
    constraints = {"num_vehicles": 2, "capacities": [100, 100]}
    
    # We pass all IDs we want to route
    delivery_ids = ["D1", "D2", "D3"]
    
    result = optimize_routes(delivery_ids, constraints, df_deliveries=deliveries)
    
    assert result["status"] == "Success"
    assert result["total_distance_km"] > 0
    assert result["total_cost"] == result["total_distance_km"] * 2.0
    assert "routes" in result
    assert len(result["routes"]) <= 2  # Max 2 vehicles used
    
    # Total load should be 150
    assert result["total_load"] == 150
    
def test_optimize_routes_infeasible():
    deliveries = [
        {"delivery_id": "D1", "distance_km": 10, "weight": 200}, # Exceeds capacity
    ]
    constraints = {"num_vehicles": 1, "capacities": [100]}
    
    result = optimize_routes(["D1"], constraints, df_deliveries=deliveries)
    assert result["status"] != "Success"
    assert "No solution" in result["status"]
    
def test_optimize_routes_empty():
    result = optimize_routes([], {"num_vehicles": 1, "capacities": [100]}, df_deliveries=[])
    assert "No deliveries to route" in result["status"]
