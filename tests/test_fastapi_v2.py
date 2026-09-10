import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "active_dataset" in data

def test_dashboard_endpoint():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "active_risks" in data["metrics"]
    assert "inventory_at_risk" in data["metrics"]
    assert "delivery_risk" in data["metrics"]
    assert "ai_decisions" in data["metrics"]
    assert "priority_risks" in data

def test_data_status_and_demo():
    res = client.get("/api/data/status")
    assert res.status_code == 200
    data = res.json()
    assert "inventory_skus" in data
    assert "deliveries_loaded" in data

    res_demo = client.post("/api/data/activate-demo")
    assert res_demo.status_code == 200

def test_data_suggest_mapping():
    res = client.post("/api/data/suggest-mapping", json={
        "existing_columns": ["Product_Code", "StockOnHand", "ROP", "SafetyStock"],
        "schema_type": "inventory"
    })
    assert res.status_code == 200
    data = res.json()
    assert "suggested_mapping" in data
    assert "sku_id" in data["suggested_mapping"]
    assert "current_stock" in data["suggested_mapping"]

def test_decisions_options():
    res = client.get("/api/decisions/options")
    assert res.status_code == 200
    data = res.json()
    assert "target_types" in data
    assert "skus" in data
    assert "deliveries" in data
    assert len(data["skus"]) > 0

def test_decisions_preview():
    # Fetch first SKU from options
    opts = client.get("/api/decisions/options").json()
    target_sku = opts["skus"][0]
    res = client.post("/api/decisions/preview", json={
        "target_type": "Inventory / Demand Issue",
        "target_id": target_sku
    })
    assert res.status_code == 200
    data = res.json()
    assert "overall_severity" in data
    assert "bottleneck_type" in data
    assert "impact_urgency_hours" in data

def test_decisions_forecast_vs_actual():
    opts = client.get("/api/decisions/options").json()
    target_sku = opts["skus"][0]
    res = client.get(f"/api/decisions/forecast-vs-actual/{target_sku}")
    assert res.status_code == 200
    data = res.json()
    assert data["is_aligned"] is True
    assert "aligned_observations" in data
    assert len(data["aligned_observations"]) > 0

def test_simulations_options():
    res = client.get("/api/simulations/options")
    assert res.status_code == 200
    data = res.json()
    assert "skus" in data
    assert "deliveries" in data
    assert len(data["skus"]) > 0

def test_simulations_inventory():
    opts = client.get("/api/simulations/options").json()
    sku = opts["skus"][0]["sku_id"]
    res = client.post("/api/simulations/inventory", json={
        "sku_id": sku,
        "demand_multiplier": 1.5,
        "stock_override": 150.0,
        "lead_time_override": 10.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "before" in data
    assert "after" in data
    assert "deltas" in data
    assert "comparison_table" in data
    assert "decision_delta" in data

def test_simulations_delivery():
    opts = client.get("/api/simulations/options").json()
    del_id = opts["deliveries"][0]["delivery_id"]
    res = client.post("/api/simulations/delivery", json={
        "delivery_id": del_id,
        "traffic_delay_override": 4.5,
        "weather_condition_override": "RAIN"
    })
    assert res.status_code == 200
    data = res.json()
    assert "before" in data
    assert "after" in data
    assert "deltas" in data
    assert "decision_delta" in data

def test_simulations_logistics():
    opts = client.get("/api/simulations/options").json()
    del_ids = [d["delivery_id"] for d in opts["deliveries"][:3]]
    res = client.post("/api/simulations/logistics", json={
        "delivery_ids": del_ids,
        "num_vehicles": 2,
        "capacity_multiplier": 1.2
    })
    assert res.status_code == 200
    data = res.json()
    assert "before" in data
    assert "after" in data
    assert "deltas" in data

def test_history_and_export():
    res = client.get("/api/history")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    res_exp = client.get("/api/history/export")
    assert res_exp.status_code == 200
    assert "text/csv" in res_exp.headers["content-type"]
