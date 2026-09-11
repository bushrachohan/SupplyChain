from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from db.connection import get_db
from db.models import DecisionTrace, Recommendation, Approval
from agent.orchestrator import run_agent_loop
import agent.tools as agent_tools

from core.unified_intelligence import build_unified_situation
from core.forecasting import get_forecast_vs_actual
from core.simulation import (
    simulate_inventory_scenario,
    simulate_delivery_scenario,
    simulate_logistics_scenario
)
from data_ingestion.csv_source import CSVDataSource

app = FastAPI(title="SupplyChain Sentinel AI API")

# Add CORS so React frontend can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep the existing Pydantic models
class OrchestrateRequest(BaseModel):
    situation: str

class OrchestrateResponse(BaseModel):
    trace_id: str

class ApprovalRequest(BaseModel):
    status: str
    approver: Optional[str] = None
    notes: Optional[str] = None

class TraceResponse(BaseModel):
    trace_id: str
    timestamp: datetime
    inputs: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None
    policies_retrieved: Optional[List[Dict[str, Any]]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    options_considered: Optional[Dict[str, Any]] = None
    primary_proposal: Optional[Dict[str, Any]] = None
    policy_critic_output: Optional[Dict[str, Any]] = None
    business_critic_output: Optional[Dict[str, Any]] = None
    consensus_result: Optional[Dict[str, Any]] = None
    human_approval: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendation_id: str
    created_at: datetime
    situation: str
    recommended_action: str
    llm_narration: Optional[str] = None
    status: str

    class Config:
        orm_mode = True
        from_attributes = True

# Helper for NaN/Infinity serialization
def clean_floats(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: clean_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_floats(i) for i in obj]
    return obj

# ----------------- Existing Endpoints ----------------- #

@app.post("/api/orchestrate", response_model=OrchestrateResponse)
def orchestrate(request: OrchestrateRequest):
    try:
        trace_id = run_agent_loop(request.situation)
        return OrchestrateResponse(trace_id=trace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traces", response_model=List[TraceResponse])
def get_traces(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).offset(skip).limit(limit).all()
    # Replace NaNs with None for JSON serialization
    for trace in traces:
        trace.inputs = clean_floats(trace.inputs)
        trace.predictions = clean_floats(trace.predictions)
        trace.tools_used = clean_floats(trace.tools_used)
        trace.options_considered = clean_floats(trace.options_considered)
    return traces

@app.get("/api/traces/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    trace.inputs = clean_floats(trace.inputs)
    trace.predictions = clean_floats(trace.predictions)
    trace.tools_used = clean_floats(trace.tools_used)
    trace.options_considered = clean_floats(trace.options_considered)
    return trace

@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(status: Optional[str] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)
    recommendations = query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
    return recommendations

@app.post("/api/traces/{trace_id}/approval")
def approve_trace(trace_id: str, request: ApprovalRequest, db: Session = Depends(get_db)):
    if request.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    approval = Approval(
        trace_id=trace_id,
        status=request.status,
        approver=request.approver,
        timestamp=datetime.utcnow(),
        notes=request.notes
    )
    db.add(approval)
    rec.status = request.status

    current_approval = trace.human_approval or {}
    new_approval = current_approval.copy()
    new_approval["status"] = request.status
    new_approval["approver"] = request.approver
    new_approval["timestamp"] = datetime.utcnow().isoformat()
    new_approval["notes"] = request.notes
    trace.human_approval = new_approval

    db.commit()
    return {"message": f"Trace {trace_id} {request.status} successfully"}


# ----------------- NEW ENDPOINTS FOR FRONTEND ----------------- #

@app.get("/api/dashboard_stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_decisions = db.query(DecisionTrace).count()
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_decisions = db.query(DecisionTrace).filter(DecisionTrace.timestamp >= week_ago).count()

    active_inventory_risks = 0
    exposure_val = 0.0
    exposure_skus = 0
    high_delivery_risks = 0
    total_deliveries = 0

    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "current_stock" in inv_df.columns and "reorder_point" in inv_df.columns:
            low_stock = inv_df[inv_df["current_stock"] < inv_df["reorder_point"]]
            active_inventory_risks = len(low_stock)
            
            if "unit_cost" in inv_df.columns and not low_stock.empty:
                deficit = (low_stock["reorder_point"] - low_stock["current_stock"]).clip(lower=0)
                exposure_val = float((deficit * low_stock["unit_cost"]).sum())
                exposure_skus = len(low_stock)
    except Exception:
        pass

    try:
        _, del_df = agent_tools._get_delivery_model()
        if not del_df.empty:
            total_deliveries = len(del_df)
            if "is_late" in del_df.columns:
                high_delivery_risks = int((del_df["is_late"] == 1).sum())
            elif "traffic_delay_hrs" in del_df.columns:
                high_delivery_risks = int((del_df["traffic_delay_hrs"] > 1.0).sum())
    except Exception:
        pass

    return {
        "total_decisions": total_decisions,
        "week_decisions": week_decisions,
        "active_inventory_risks": active_inventory_risks,
        "exposure_val": exposure_val,
        "exposure_skus": exposure_skus,
        "high_delivery_risks": high_delivery_risks,
        "total_deliveries": total_deliveries
    }

@app.get("/api/priority_risks")
def get_priority_risks():
    top_inv_risk = None
    top_del_risk = None

    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "current_stock" in inv_df.columns and "reorder_point" in inv_df.columns:
            low_stock = inv_df[inv_df["current_stock"] < inv_df["reorder_point"]]
            if not low_stock.empty:
                low_stock_calc = low_stock.copy()
                low_stock_calc["ratio"] = low_stock_calc["current_stock"] / low_stock_calc["reorder_point"].replace(0, 1)
                top_inv_row = low_stock_calc.sort_values(by="ratio", ascending=True).iloc[0]
                top_sku = str(top_inv_row["sku_id"])
                
                inv_risk_res = agent_tools.get_inventory_risk(top_sku)
                top_inv_risk = {
                    "sku_id": top_sku,
                    "location_id": str(top_inv_row.get("location_id", "Primary Facility")),
                    "unit_cost": float(top_inv_row.get("unit_cost", 0)),
                    "lead_time_days": float(top_inv_row.get("lead_time_days", 7)),
                    "days_of_supply": float(inv_risk_res.get("days_of_supply", 0.0)),
                    "detail": str(inv_risk_res.get("detail", ""))
                }
    except Exception:
        pass

    try:
        _, del_df = agent_tools._get_delivery_model()
        if not del_df.empty:
            late_dels = del_df[del_df.get("is_late", 0) == 1] if "is_late" in del_df.columns else pd.DataFrame()
            if not late_dels.empty:
                top_del_row = late_dels.sort_values(by="traffic_delay_hrs", ascending=False).iloc[0] if "traffic_delay_hrs" in late_dels.columns else late_dels.iloc[0]
            else:
                top_del_row = del_df.sort_values(by="traffic_delay_hrs", ascending=False).iloc[0] if "traffic_delay_hrs" in del_df.columns else del_df.iloc[0]
                    
            top_del_id = str(top_del_row["delivery_id"])
            del_risk_res = agent_tools.get_delivery_risk(top_del_id)
            
            top_del_risk = {
                "delivery_id": top_del_id,
                "carrier_id": str(top_del_row.get("carrier_id", "Assigned Carrier")),
                "origin": str(top_del_row.get("origin", "Origin Hub")),
                "destination": str(top_del_row.get("destination", "Destination")),
                "distance_km": float(top_del_row.get("distance_km", 0)),
                "traffic_delay_hrs": float(top_del_row.get("traffic_delay_hrs", 0.0)),
                "weather_condition": str(top_del_row.get("weather_condition", "CLEAR")),
                "risk_score": float(del_risk_res.get("risk_score", 0.85 if top_del_row.get("is_late") == 1 else 0.15)),
                "risk_label": str(del_risk_res.get("risk_label", "HIGH" if top_del_row.get("is_late") == 1 else "LOW"))
            }
    except Exception:
        pass

    return {
        "top_inventory_risk": top_inv_risk,
        "top_delivery_risk": top_del_risk
    }

@app.get("/api/forecast/{sku_id}")
def get_forecast(sku_id: str):
    try:
        model, demand_df = agent_tools._get_demand_model()
        res = get_forecast_vs_actual(model, demand_df, sku_id)
        if not res.get("is_aligned", False):
            return {"error": "Forecast unavailable"}
        
        aligned_df = res["aligned_df"]
        records = aligned_df.to_dict(orient="records")
        
        full_df_records = []
        if res.get("full_history_df") is not None:
            full_df_records = res["full_history_df"].to_dict(orient="records")

        records = clean_floats(records)
        full_df_records = clean_floats(full_df_records)

        return {
            "horizon_periods": res["horizon_periods"],
            "actual_avg": res.get("actual_avg"),
            "forecast_avg": res.get("forecast_avg"),
            "mae": res.get("mae"),
            "mape": res.get("mape"),
            "aligned_data": records,
            "full_history_data": full_df_records
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/data/status")
def get_data_status():
    try:
        inv_df = agent_tools._get_inventory_df()
        _, del_df = agent_tools._get_delivery_model()
        _, dem_df = agent_tools._get_demand_model()
        
        return {
            "inventory_skus": len(inv_df) if not inv_df.empty else 0,
            "deliveries": len(del_df) if not del_df.empty else 0,
            "demand_records": len(dem_df) if not dem_df.empty else 0
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/data/use_demo")
def use_demo_data():
    agent_tools.set_active_datasource(CSVDataSource(data_dir="data"))
    return {"status": "success"}

@app.get("/api/options")
def get_options():
    sku_list = []
    del_list = []
    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "sku_id" in inv_df.columns:
            sku_list = inv_df["sku_id"].dropna().unique().tolist()
        
        _, del_df = agent_tools._get_delivery_model()
        if not del_df.empty and "delivery_id" in del_df.columns:
            del_list = del_df["delivery_id"].dropna().unique().tolist()
    except Exception:
        pass
    
    return {"skus": sku_list, "deliveries": del_list}

class UnifiedSituationRequest(BaseModel):
    sku_id: Optional[str] = None
    delivery_id: Optional[str] = None

@app.post("/api/unified_situation")
def get_unified_situation(req: UnifiedSituationRequest):
    try:
        state = build_unified_situation(sku_id=req.sku_id, delivery_id=req.delivery_id)
        return {
            "overall_severity": state.overall_severity.value,
            "bottleneck_type": state.bottleneck.bottleneck_type,
            "impact_urgency_hours": state.bottleneck.impact_urgency_hours,
            "description": state.bottleneck.description,
            "cross_risk_dependencies": state.cross_risk_dependencies
        }
    except Exception as e:
        return {"error": str(e)}

class InventorySimRequest(BaseModel):
    sku_id: str
    demand_multiplier: float
    stock_override: Optional[float] = None
    lead_time_override: Optional[float] = None

@app.post("/api/simulate/inventory")
def simulate_inventory(req: InventorySimRequest):
    try:
        inv_df = agent_tools._get_inventory_df()
        sku_row = inv_df[inv_df["sku_id"] == req.sku_id].iloc[0]
        base_stock = float(sku_row.get("current_stock", 100.0))
        base_lead_time = float(sku_row.get("lead_time_days", 7.0))
        
        base_daily = max(1.0, base_stock / 15.0)
        base_forecast_14d = base_daily * 14.0
        
        sim_res = simulate_inventory_scenario(
            sku_id=req.sku_id,
            base_current_stock=base_stock,
            base_avg_daily_demand=base_daily,
            base_forecast_demand=base_forecast_14d,
            base_forecast_period_days=14,
            base_lead_time_days=base_lead_time,
            base_safety_stock_days=14.0,
            demand_multiplier=req.demand_multiplier,
            stock_override=req.stock_override,
            lead_time_override=req.lead_time_override,
        )
        return clean_floats(sim_res)
    except Exception as e:
        return {"error": str(e)}

class DeliverySimRequest(BaseModel):
    delivery_id: str
    weather_override: str
    traffic_override: float

@app.post("/api/simulate/delivery")
def simulate_delivery(req: DeliverySimRequest):
    try:
        delivery_model, del_df = agent_tools._get_delivery_model()
        sim_res = simulate_delivery_scenario(
            model=delivery_model,
            df_deliveries=del_df,
            delivery_id=req.delivery_id,
            traffic_delay_override=req.traffic_override,
            weather_condition_override=req.weather_override
        )
        return clean_floats(sim_res)
    except Exception as e:
        return {"error": str(e)}

class LogisticsSimRequest(BaseModel):
    delivery_ids: List[str]
    num_vehicles: int
    capacity_multiplier: float

@app.post("/api/simulate/logistics")
def simulate_logistics(req: LogisticsSimRequest):
    try:
        _, del_df = agent_tools._get_delivery_model()
        base_constraints = {"num_vehicles": req.num_vehicles, "capacities": [500] * req.num_vehicles}
        del_records = del_df[del_df["delivery_id"].isin(req.delivery_ids)].to_dict(orient="records")
        for d in del_records:
            if "weight" not in d:
                d["weight"] = 100
                
        sim_res = simulate_logistics_scenario(
            delivery_ids=req.delivery_ids,
            df_deliveries=del_records,
            base_vehicle_constraints=base_constraints,
            capacity_multiplier=req.capacity_multiplier,
            num_vehicles_override=req.num_vehicles
        )
        return clean_floats(sim_res)
    except Exception as e:
        return {"error": str(e)}
