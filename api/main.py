import os
import tempfile
import shutil
import uuid
import io
import csv
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import pandas as pd

from db.connection import get_db
from db.models import DecisionTrace, Recommendation, Approval
from agent.orchestrator import run_agent_loop
import agent.tools as agent_tools
from data_ingestion.csv_source import CSVDataSource
from data_ingestion.excel_source import ExcelDataSource
from data_ingestion.db_source import DBDataSource
from data_ingestion.active_dataset import active_dataset
from data_ingestion.validation import (
    validate_dataset,
    CANONICAL_SCHEMAS,
    COLUMN_ALIASES,
)
from core.forecasting import get_forecast_vs_actual
from core.unified_intelligence import build_unified_situation
from core.simulation import (
    simulate_inventory_scenario,
    simulate_delivery_scenario,
    simulate_logistics_scenario,
)

app = FastAPI(
    title="SupplyChain Sentinel AI API",
    description="SentinelFlow — AI-Powered Supply Chain Risk & Decision Intelligence REST API"
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
frontend_env = os.getenv("FRONTEND_URL")
if frontend_env:
    for url in frontend_env.split(","):
        clean_url = url.strip()
        if clean_url and clean_url not in allowed_origins:
            allowed_origins.append(clean_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------

class OrchestrateRequest(BaseModel):
    situation: str

class OrchestrateResponse(BaseModel):
    trace_id: str

class ApprovalRequest(BaseModel):
    status: str
    approver: Optional[str] = "Ops Lead"
    notes: Optional[str] = None

class TraceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: str
    created_at: datetime
    situation: str
    recommended_action: str
    llm_narration: Optional[str] = None
    status: str

class SuggestMappingRequest(BaseModel):
    existing_columns: List[str]
    schema_type: str  # "demand", "inventory", "deliveries"

class ValidateDatasetRequest(BaseModel):
    file_token: str
    filename: str
    schema_type: str
    column_mapping: Dict[str, str]
    sheet_name: Optional[str] = None

class ActivateDatasetRequest(BaseModel):
    file_token: str
    source_type: str  # "csv" or "excel"
    excel_sheet_mapping: Optional[Dict[str, str]] = None  # target_schema -> sheet_name

class ConnectDbRequest(BaseModel):
    connection_url: str

class CreateDecisionRequest(BaseModel):
    target_type: str  # "Inventory / Demand Issue" or "Delivery / Routing Issue"
    target_id: str
    situation_text: Optional[str] = ""

class PreviewSituationRequest(BaseModel):
    target_type: str
    target_id: str

class InventorySimRequest(BaseModel):
    sku_id: str
    demand_multiplier: float = 1.0
    stock_override: Optional[float] = None
    lead_time_override: Optional[float] = None

class DeliverySimRequest(BaseModel):
    delivery_id: str
    traffic_delay_override: Optional[float] = None
    weather_condition_override: Optional[str] = None

class LogisticsSimRequest(BaseModel):
    delivery_ids: List[str]
    num_vehicles: int = 2
    capacity_multiplier: float = 1.0

# ---------------------------------------------------------------------------
# Helper Mapping & Temporary Storage Utilities
# ---------------------------------------------------------------------------

UPLOAD_TEMP_BASE = os.path.join(tempfile.gettempdir(), "sentinel_uploads")
os.makedirs(UPLOAD_TEMP_BASE, exist_ok=True)

def sanitize_for_json(obj: Any) -> Any:
    """Recursively replaces NaN and Inf with None so output is strictly JSON compliant."""
    import math
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

def suggest_mapping(existing_cols: List[str], target_cols: List[str], schema_type: Optional[str] = None) -> Dict[str, str]:
    """Intelligently suggests default column mappings using exact match, canonical aliases, and substring heuristics."""
    mapping = {}
    existing_cols_clean = {str(c).strip().lower().replace("_", "").replace(" ", ""): c for c in existing_cols}
    existing_cols_lower = {str(c).strip().lower(): c for c in existing_cols}
    
    for tgt in target_cols:
        # 1. Exact match
        if tgt.lower() in existing_cols_lower:
            mapping[tgt] = existing_cols_lower[tgt.lower()]
            continue
            
        # 2. Exact alias match from canonical dictionary
        aliases = COLUMN_ALIASES.get(tgt, [tgt])
        found_alias = False
        for alias in aliases:
            cleaned_alias = alias.strip().lower()
            cleaned_no_sep = cleaned_alias.replace("_", "").replace(" ", "")
            if cleaned_alias in existing_cols_lower:
                mapping[tgt] = existing_cols_lower[cleaned_alias]
                found_alias = True
                break
            elif cleaned_no_sep in existing_cols_clean:
                mapping[tgt] = existing_cols_clean[cleaned_no_sep]
                found_alias = True
                break
                
        # 3. Substring alias match
        if not found_alias:
            for alias in aliases:
                cleaned_no_sep = alias.strip().lower().replace("_", "").replace(" ", "")
                if len(cleaned_no_sep) >= 3:
                    for ecol_clean, ecol_orig in existing_cols_clean.items():
                        if cleaned_no_sep in ecol_clean or ecol_clean in cleaned_no_sep:
                            mapping[tgt] = ecol_orig
                            found_alias = True
                            break
                if found_alias:
                    break

        if not found_alias:
            tgt_sub = tgt.replace("_id", "").replace("_", "").lower()
            for ecol_clean, ecol_orig in existing_cols_clean.items():
                if tgt_sub in ecol_clean or ecol_clean in tgt_sub:
                    mapping[tgt] = ecol_orig
                    break
    return mapping

# ---------------------------------------------------------------------------
# System & Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    try:
        meta = active_dataset.get_metadata()
    except Exception:
        agent_tools._get_active_source()
        meta = active_dataset.get_metadata()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_dataset": meta.name if meta else "Synthetic Data"
    }

# ---------------------------------------------------------------------------
# Command Center / Operational Dashboard
# ---------------------------------------------------------------------------

@app.get("/api/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Operational summary metrics and priority risks calculated directly from active dataset and database."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_decisions = db.query(DecisionTrace).count()
    week_decisions = db.query(DecisionTrace).filter(DecisionTrace.timestamp >= week_ago).count()
    pending_count = db.query(DecisionTrace).filter(DecisionTrace.human_approval["status"].astext == "pending").count() if hasattr(DecisionTrace.human_approval, "astext") else 0

    # If astext is unsupported in SQLite, filter in python
    if pending_count == 0:
        all_traces = db.query(DecisionTrace).all()
        pending_count = sum(1 for t in all_traces if t.human_approval and t.human_approval.get("status") == "pending")

    active_inventory_risks = 0
    exposure_val = 0.0
    exposure_str = "₹0"
    exposure_delta = "Buffer Healthy"
    high_delivery_risks = 0
    del_delta_str = "All On-Time"
    top_inv = None
    top_del = None

    inv_df = pd.DataFrame()
    del_df = pd.DataFrame()

    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "current_stock" in inv_df.columns and "reorder_point" in inv_df.columns:
            low_stock = inv_df[inv_df["current_stock"] < inv_df["reorder_point"]]
            active_inventory_risks = int(len(low_stock))
            if "unit_cost" in inv_df.columns and not low_stock.empty:
                deficit = (low_stock["reorder_point"] - low_stock["current_stock"]).clip(lower=0)
                exp_val = float((deficit * low_stock["unit_cost"]).sum())
                exposure_val = exp_val
                exposure_str = f"₹{exp_val:,.0f}"
                exposure_delta = f"Deficit on {len(low_stock)} SKUs"
            elif not low_stock.empty:
                exposure_str = f"{len(low_stock)} SKUs"
                exposure_delta = "Stock Deficit"

            if not low_stock.empty:
                low_stock_calc = low_stock.copy()
                low_stock_calc["ratio"] = low_stock_calc["current_stock"] / low_stock_calc["reorder_point"].replace(0, 1)
                top_inv_row = low_stock_calc.sort_values(by="ratio", ascending=True).iloc[0]
                top_sku = str(top_inv_row["sku_id"])
                inv_risk_res = agent_tools.get_inventory_risk(top_sku)
                top_inv = {
                    "sku_id": top_sku,
                    "location_id": str(top_inv_row.get("location_id", "Primary Facility")),
                    "unit_cost": float(top_inv_row.get("unit_cost", 0.0)),
                    "lead_time_days": float(top_inv_row.get("lead_time_days", 7.0)),
                    "current_stock": float(top_inv_row.get("current_stock", 0.0)),
                    "safety_stock": float(top_inv_row.get("safety_stock", 0.0)),
                    "reorder_point": float(top_inv_row.get("reorder_point", 0.0)),
                    "days_of_supply": float(inv_risk_res.get("days_of_supply", 0.0)),
                    "detail": inv_risk_res.get("detail", f"Current stock ({top_inv_row['current_stock']}) is below reorder point.")
                }
    except Exception as e:
        active_inventory_risks = 0
        exposure_str = "N/A"
        exposure_delta = "Data Unavailable"

    try:
        _, del_df = agent_tools._get_delivery_model()
        if not del_df.empty:
            if "is_late" in del_df.columns:
                late_mask = del_df["is_late"] == 1
                high_delivery_risks = int(late_mask.sum())
                del_delta_str = f"{high_delivery_risks} of {len(del_df)} shipments"
            elif "traffic_delay_hrs" in del_df.columns:
                delayed_mask = del_df["traffic_delay_hrs"] > 1.0
                high_delivery_risks = int(delayed_mask.sum())
                del_delta_str = f"{high_delivery_risks} delayed >1h"

            late_dels = del_df[del_df.get("is_late", 0) == 1] if "is_late" in del_df.columns else pd.DataFrame()
            if not late_dels.empty:
                top_del_row = late_dels.sort_values(by="traffic_delay_hrs", ascending=False).iloc[0] if "traffic_delay_hrs" in late_dels.columns else late_dels.iloc[0]
            else:
                top_del_row = del_df.sort_values(by="traffic_delay_hrs", ascending=False).iloc[0] if "traffic_delay_hrs" in del_df.columns else del_df.iloc[0]

            top_del_id = str(top_del_row["delivery_id"])
            del_risk_res = agent_tools.get_delivery_risk(top_del_id)
            score = float(del_risk_res.get("risk_score", 0.85 if top_del_row.get("is_late") == 1 else 0.15))
            risk_label = str(del_risk_res.get("risk_label", "HIGH" if top_del_row.get("is_late") == 1 else "LOW"))

            top_del = {
                "delivery_id": top_del_id,
                "carrier_id": str(top_del_row.get("carrier_id", "Assigned Carrier")),
                "origin": str(top_del_row.get("origin", "Origin Hub")),
                "destination": str(top_del_row.get("destination", "Destination")),
                "distance_km": float(top_del_row.get("distance_km", 0.0)),
                "traffic_delay_hrs": float(top_del_row.get("traffic_delay_hrs", 0.0)),
                "weather_condition": str(top_del_row.get("weather_condition", "CLEAR")),
                "late_probability": score,
                "risk_label": risk_label,
            }
    except Exception as e:
        high_delivery_risks = 0
        del_delta_str = "Data Unavailable"

    source_meta = active_dataset.get_metadata() if hasattr(active_dataset, "get_metadata") else None

    return {
        "metrics": {
            "active_risks": {
                "count": active_inventory_risks,
                "status": "Elevated" if active_inventory_risks > 0 else "Optimal",
                "detail": f"{active_inventory_risks} below ROP" if active_inventory_risks > 0 else "All Stock Healthy"
            },
            "inventory_at_risk": {
                "exposure_formatted": exposure_str,
                "exposure_numeric": exposure_val,
                "detail": exposure_delta,
                "alert": "Stockout Alert" if active_inventory_risks > 0 else "Normal"
            },
            "delivery_risk": {
                "late_count": high_delivery_risks,
                "exposure_percentage": round((high_delivery_risks / max(1, len(del_df))) * 100, 1) if not del_df.empty else 0.0,
                "detail": del_delta_str,
            },
            "ai_decisions": {
                "total_count": total_decisions,
                "week_count": week_decisions,
                "pending_approval_count": pending_count,
            }
        },
        "priority_risks": {
            "inventory": top_inv,
            "delivery": top_del
        },
        "active_datasource": {
            "name": source_meta.name if source_meta else "Company Supply Chain",
            "source_type": source_meta.source_type if source_meta else "demo",
            "status": source_meta.status if source_meta else "connected"
        }
    }

# ---------------------------------------------------------------------------
# Data Hub Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/data/status")
def get_data_status():
    """Returns active dataset details and live record counts."""
    inv_df = pd.DataFrame()
    del_df = pd.DataFrame()
    dem_df = pd.DataFrame()
    try:
        inv_df = agent_tools._get_inventory_df()
        _, del_df = agent_tools._get_delivery_model()
        _, dem_df = agent_tools._get_demand_model()
    except Exception:
        pass

    meta = active_dataset.get_metadata() if hasattr(active_dataset, "get_metadata") else None
    return {
        "active_dataset_type": meta.source_type if meta else "demo",
        "dataset_name": meta.name if meta else "Demo Synthetic Dataset",
        "status": meta.status if meta else "active",
        "connected_at": meta.connected_at if meta else datetime.now(timezone.utc).isoformat(),
        "inventory_skus": len(inv_df) if not inv_df.empty else 0,
        "deliveries_loaded": len(del_df) if not del_df.empty else 0,
        "demand_records": len(dem_df) if not dem_df.empty else 0,
    }

@app.post("/api/data/upload")
async def upload_data_files(files: List[UploadFile] = File(...)):
    """Upload CSV or Excel files, inspect columns, row count, and detected sheets."""
    token = str(uuid.uuid4())
    upload_dir = os.path.join(UPLOAD_TEMP_BASE, token)
    os.makedirs(upload_dir, exist_ok=True)

    file_summaries = []
    for f in files:
        target_path = os.path.join(upload_dir, f.filename)
        with open(target_path, "wb") as out:
            content = await f.read()
            out.write(content)

        summary = {
            "filename": f.filename,
            "size_bytes": len(content),
            "file_type": "excel" if f.filename.endswith((".xlsx", ".xls")) else "csv",
            "sheets": [],
            "columns": [],
            "row_count": 0,
            "preview_rows": []
        }

        try:
            if summary["file_type"] == "excel":
                xl = pd.ExcelFile(target_path)
                summary["sheets"] = xl.sheet_names
                if xl.sheet_names:
                    first_df = pd.read_excel(target_path, sheet_name=xl.sheet_names[0], nrows=5)
                    summary["columns"] = list(first_df.columns)
                    summary["preview_rows"] = first_df.head(3).to_dict(orient="records")
            else:
                df = pd.read_csv(target_path, nrows=5)
                full_df = pd.read_csv(target_path)
                summary["row_count"] = len(full_df)
                summary["columns"] = list(df.columns)
                summary["preview_rows"] = df.head(3).to_dict(orient="records")
        except Exception as e:
            summary["error"] = str(e)

        file_summaries.append(summary)

    return {
        "file_token": token,
        "files": file_summaries,
        "schemas": {k: v["required_columns"] for k, v in CANONICAL_SCHEMAS.items()}
    }

@app.post("/api/data/suggest-mapping")
def get_suggested_mapping(request: SuggestMappingRequest):
    """Suggests column mapping for uploaded file against a canonical schema."""
    target_schema = request.schema_type.lower()
    req_cols = CANONICAL_SCHEMAS.get(target_schema, {}).get("required_columns", [])
    opt_cols = CANONICAL_SCHEMAS.get(target_schema, {}).get("optional_columns", [])
    all_target_cols = req_cols + opt_cols

    suggested = suggest_mapping(request.existing_columns, all_target_cols, target_schema)
    return {
        "schema_type": target_schema,
        "required_columns": req_cols,
        "optional_columns": opt_cols,
        "suggested_mapping": suggested
    }

@app.post("/api/data/validate")
def validate_uploaded_dataset(request: ValidateDatasetRequest):
    """Validates uploaded file against canonical schema with user's explicit column mapping."""
    upload_dir = os.path.join(UPLOAD_TEMP_BASE, request.file_token)
    file_path = os.path.join(upload_dir, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file session not found. Please re-upload.")

    try:
        if request.filename.endswith((".xlsx", ".xls")):
            sheet = request.sheet_name or 0
            df = pd.read_excel(file_path, sheet_name=sheet)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    val_res = validate_dataset(df, schema_type=request.schema_type, explicit_mapping=request.column_mapping)
    return {
        "is_valid": val_res.is_valid,
        "errors": val_res.errors,
        "warnings": val_res.warnings,
        "profiling": val_res.profiling,
        "row_count": len(val_res.normalized_df) if val_res.normalized_df is not None else 0
    }

@app.post("/api/data/activate")
def activate_uploaded_dataset(request: ActivateDatasetRequest):
    """Activates the uploaded dataset, updating the global business state."""
    upload_dir = os.path.join(UPLOAD_TEMP_BASE, request.file_token)
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="File session expired or not found.")

    if request.source_type == "excel":
        files = [f for f in os.listdir(upload_dir) if f.endswith((".xlsx", ".xls"))]
        if not files:
            raise HTTPException(status_code=400, detail="No Excel workbook found in session.")
        excel_path = os.path.join(upload_dir, files[0])
        agent_tools.set_active_datasource(ExcelDataSource(excel_path=excel_path), name=files[0])
    else:
        # Check required CSV files: historical_demand.csv, inventory_snapshot.csv, deliveries.csv
        agent_tools.set_active_datasource(CSVDataSource(data_dir=upload_dir), name="Custom CSV Ingestion")

    return {"message": "Dataset successfully activated and connected to Sentinel AI pipeline.", "status": "active"}

@app.post("/api/data/connect-db")
def connect_database_source(request: ConnectDbRequest):
    """Tests relational database connection and activates it."""
    from sqlalchemy import create_engine
    try:
        engine = create_engine(request.connection_url)
        with engine.connect() as conn:
            pass
        source = DBDataSource(connection_url=request.connection_url)
        agent_tools.set_active_datasource(source, name="Enterprise Relational DB")
        # verify tables
        agent_tools._get_inventory_df()
        return {"message": "Database connection verified and activated.", "status": "active"}
    except Exception as e:
        agent_tools.set_active_datasource(CSVDataSource(data_dir="data"))
        raise HTTPException(status_code=400, detail=f"Database connection failed or required tables missing: {str(e)}")

@app.post("/api/data/activate-demo")
def activate_demo_dataset():
    """Switches active datasource back to bundled synthetic CSV dataset."""
    agent_tools.set_active_datasource(CSVDataSource(data_dir="data"), name="Demo Dataset — Synthetic")
    return {"message": "Switched to Synthetic Demo Dataset.", "status": "active"}

# ---------------------------------------------------------------------------
# Create a Decision Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/decisions/options")
def get_decision_options():
    """Dynamically fetches selectable SKUs and Deliveries from active data."""
    sku_list = []
    del_list = []
    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "sku_id" in inv_df.columns:
            sku_list = [str(s) for s in inv_df["sku_id"].dropna().unique().tolist()]
        if not sku_list:
            _, dem_df = agent_tools._get_demand_model()
            if dem_df is not None and not dem_df.empty and "sku_id" in dem_df.columns:
                sku_list = [str(s) for s in dem_df["sku_id"].dropna().unique().tolist()]
    except Exception:
        sku_list = []

    try:
        _, del_df = agent_tools._get_delivery_model()
        if del_df is not None and not del_df.empty and "delivery_id" in del_df.columns:
            del_list = [str(d) for d in del_df["delivery_id"].dropna().unique().tolist()]
    except Exception:
        del_list = []

    return {
        "target_types": ["Inventory / Demand Issue", "Delivery / Routing Issue"],
        "skus": sku_list,
        "deliveries": del_list
    }

@app.post("/api/decisions/preview")
def preview_situation_assessment(request: PreviewSituationRequest):
    """Pre-analysis Unified Situation Assessment computed directly by core.unified_intelligence."""
    sku_target = request.target_id if request.target_type == "Inventory / Demand Issue" else None
    del_target = request.target_id if request.target_type != "Inventory / Demand Issue" else None

    try:
        preview_state = build_unified_situation(sku_id=sku_target, delivery_id=del_target)
        return {
            "overall_severity": preview_state.overall_severity.value,
            "bottleneck_type": preview_state.bottleneck.bottleneck_type,
            "impact_urgency_hours": round(preview_state.bottleneck.impact_urgency_hours, 1),
            "description": preview_state.bottleneck.description,
            "cross_risk_dependencies": preview_state.cross_risk_dependencies,
            "mitigation_options": preview_state.bottleneck.mitigation_options,
        }
    except Exception as e:
        return {
            "overall_severity": "MEDIUM",
            "bottleneck_type": "Operational Risk",
            "impact_urgency_hours": 24.0,
            "description": f"Assessment generated: {str(e)}",
            "cross_risk_dependencies": [],
            "mitigation_options": ["Evaluate candidate actions"]
        }

@app.get("/api/decisions/forecast-vs-actual/{sku_id}")
def get_sku_forecast_vs_actual(sku_id: str):
    """Returns actual demand vs forecast alignment on matching dates from LightGBM model."""
    try:
        model, demand_df = agent_tools._get_demand_model()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model unavailable: {str(e)}")

    if demand_df is None or demand_df.empty:
        raise HTTPException(status_code=404, detail="Demand data not loaded.")

    res = get_forecast_vs_actual(model, demand_df, sku_id)
    if not res.get("is_aligned", False):
        raise HTTPException(status_code=404, detail="Forecast vs Actual alignment unavailable for this SKU.")

    aligned_df = res.get("aligned_df")
    aligned_records = []
    if aligned_df is not None:
        aligned_clean = aligned_df.where(pd.notnull(aligned_df), None)
        aligned_records = aligned_clean.to_dict(orient="records")

    full_df = res.get("full_history_df")
    history_records = []
    if full_df is not None:
        full_clean = full_df.where(pd.notnull(full_df), None)
        history_records = full_clean.to_dict(orient="records")

    import math
    def clean_float(val):
        if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
            return None
        return float(val)

    res_data = {
        "is_aligned": True,
        "sku_id": sku_id,
        "horizon_periods": int(res.get("horizon_periods", 0)),
        "actual_avg": res.get("actual_avg"),
        "forecast_avg": res.get("forecast_avg"),
        "mae": res.get("mae"),
        "mape": res.get("mape"),
        "rmse": res.get("rmse"),
        "aligned_observations": aligned_records,
        "history_series": history_records,
    }
    return sanitize_for_json(res_data)

@app.post("/api/decisions/create")
def create_decision(request: CreateDecisionRequest):
    """Runs the full multi-agent decision loop and returns the persisted trace ID."""
    sku_target = request.target_id if request.target_type == "Inventory / Demand Issue" else None
    del_target = request.target_id if request.target_type != "Inventory / Demand Issue" else None

    try:
        unified_state = build_unified_situation(sku_id=sku_target, delivery_id=del_target)
        briefing = unified_state.to_summary_markdown()
        situation = (
            f"{briefing}\n\n"
            f"#### 👤 Business Operator Context & Specific Question:\n"
            f"{request.situation_text if request.situation_text and request.situation_text.strip() else 'Evaluate the operational risk and provide the optimal recommended action.'}"
        )
    except Exception as e:
        situation = f"Target ID: {request.target_id}. Context: {request.situation_text}"

    try:
        trace_id = run_agent_loop(situation)
        return {"trace_id": trace_id, "message": "Decision created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent decision loop failed: {str(e)}")

# ---------------------------------------------------------------------------
# Approvals & Governance
# ---------------------------------------------------------------------------

@app.get("/api/approvals")
def get_pending_approvals(db: Session = Depends(get_db)):
    """Returns decision traces awaiting human sign-off."""
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
    pending = []
    for t in traces:
        if t.human_approval and t.human_approval.get("status") == "pending":
            severity = "HIGH"
            if t.predictions and isinstance(t.predictions, dict):
                severity = str(t.predictions.get("overall_severity", t.predictions.get("risk_level", "HIGH")))
            elif t.tools_used:
                for tc in t.tools_used:
                    res = tc.get("result", {})
                    if isinstance(res, dict) and "risk_level" in res:
                        severity = str(res["risk_level"])
                        break

            rec_action = t.consensus_result.get("recommendation", "Review needed") if t.consensus_result else "Review needed"
            if isinstance(rec_action, dict):
                rec_action = rec_action.get("action", str(rec_action))

            pending.append({
                "trace_id": t.trace_id,
                "timestamp": t.timestamp.isoformat(),
                "severity": severity,
                "situation_summary": str(t.inputs.get("situation", "Operational Issue"))[:120],
                "recommended_action": rec_action,
                "reviewer": t.human_approval.get("approver", "Ops Lead"),
                "status": "pending"
            })
    return pending

# ---------------------------------------------------------------------------
# Decision History & Audit Trail
# ---------------------------------------------------------------------------

@app.get("/api/history")
def get_decision_history(
    query: Optional[str] = None,
    status: Optional[str] = "ALL",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Returns historical approved/rejected decisions with audit metadata."""
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
    records = []
    for t in traces:
        h_status = t.human_approval.get("status", "").lower() if t.human_approval else ""
        if h_status not in ["approved", "rejected"]:
            continue

        if status and status.upper() != "ALL" and h_status != status.lower():
            continue

        rec_action = t.consensus_result.get("recommendation", "Unknown") if t.consensus_result else "Unknown"
        if isinstance(rec_action, dict):
            rec_action = rec_action.get("action", str(rec_action))

        sit_str = str(t.inputs.get("situation", ""))
        if query:
            q = query.lower()
            if q not in t.trace_id.lower() and q not in sit_str.lower() and q not in str(rec_action).lower():
                continue

        records.append({
            "trace_id": t.trace_id,
            "timestamp": t.timestamp.isoformat(),
            "status": h_status.upper(),
            "recommended_action": rec_action,
            "situation": sit_str,
            "approver": t.human_approval.get("approver", "Ops Lead"),
            "approval_timestamp": t.human_approval.get("timestamp"),
            "notes": t.human_approval.get("notes", ""),
            "consensus_status": t.consensus_result.get("status", "VALIDATED") if t.consensus_result else "VALIDATED"
        })

    return records[skip : skip + limit]

@app.get("/api/history/export")
def export_decision_history_csv(db: Session = Depends(get_db)):
    """Exports real audit trail data to CSV."""
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["trace_id", "timestamp", "status", "approver", "approval_timestamp", "recommended_action", "situation", "notes"])

    for t in traces:
        if t.human_approval and t.human_approval.get("status") in ["approved", "rejected"]:
            rec_action = t.consensus_result.get("recommendation", "") if t.consensus_result else ""
            if isinstance(rec_action, dict):
                rec_action = rec_action.get("action", str(rec_action))
            writer.writerow([
                t.trace_id,
                t.timestamp.isoformat(),
                t.human_approval.get("status", "").upper(),
                t.human_approval.get("approver", ""),
                t.human_approval.get("timestamp", ""),
                rec_action,
                str(t.inputs.get("situation", "")).replace("\n", " "),
                t.human_approval.get("notes", "").replace("\n", " ")
            ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sentinel_decision_history_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )

# ---------------------------------------------------------------------------
# What-If Scenario Simulation
# ---------------------------------------------------------------------------

@app.get("/api/simulations/options")
def get_simulation_options():
    """Baseline entity data for What-If scenario simulation controls."""
    sku_options = []
    del_options = []

    try:
        inv_df = agent_tools._get_inventory_df()
        if not inv_df.empty and "sku_id" in inv_df.columns:
            for _, row in inv_df.iterrows():
                sku_options.append({
                    "sku_id": str(row["sku_id"]),
                    "base_stock": float(row.get("current_stock", 100.0)),
                    "base_lead_time": float(row.get("lead_time_days", 7.0)),
                    "unit_cost": float(row.get("unit_cost", 50.0)),
                })
    except Exception:
        pass

    try:
        _, del_df = agent_tools._get_delivery_model()
        if del_df is not None and not del_df.empty and "delivery_id" in del_df.columns:
            for _, row in del_df.iterrows():
                del_options.append({
                    "delivery_id": str(row["delivery_id"]),
                    "carrier_id": str(row.get("carrier_id", "Carrier")),
                    "origin": str(row.get("origin", "Depot")),
                    "destination": str(row.get("destination", "Retail")),
                    "distance_km": float(row.get("distance_km", 100.0)),
                    "base_weather": str(row.get("weather_condition", "CLEAR")),
                    "base_traffic_delay": float(row.get("traffic_delay_hrs", 0.0)),
                })
    except Exception:
        pass

    return {
        "skus": sku_options,
        "deliveries": del_options,
        "weather_options": ["CLEAR", "RAIN", "FOG", "STORM"]
    }

@app.post("/api/simulations/inventory")
def run_inventory_simulation(request: InventorySimRequest):
    """Executes inventory stress test scenario using simulate_inventory_scenario."""
    inv_df = agent_tools._get_inventory_df()
    sku_row = inv_df[inv_df["sku_id"] == request.sku_id]
    if sku_row.empty:
        raise HTTPException(status_code=404, detail=f"SKU {request.sku_id} not found.")

    row = sku_row.iloc[0]
    base_stock = float(row.get("current_stock", 100.0))
    base_lead_time = float(row.get("lead_time_days", 7.0))
    unit_cost = float(row.get("unit_cost", 50.0))
    base_daily = max(1.0, base_stock / 15.0)
    base_forecast_14d = base_daily * 14.0

    res = simulate_inventory_scenario(
        sku_id=request.sku_id,
        base_current_stock=base_stock,
        base_avg_daily_demand=base_daily,
        base_forecast_demand=base_forecast_14d,
        base_forecast_period_days=14,
        base_lead_time_days=base_lead_time,
        base_safety_stock_days=14.0,
        demand_multiplier=request.demand_multiplier,
        stock_override=request.stock_override,
        lead_time_override=request.lead_time_override,
    )

    before = res["before"]
    after = res["after"]
    deltas = res["deltas"]

    comparison_table = [
        {"metric": "Current Stock (units)", "baseline": f"{before.get('current_stock', base_stock):.0f}", "scenario": f"{after.get('current_stock', base_stock):.0f}", "delta": f"{after.get('current_stock', base_stock) - before.get('current_stock', base_stock):+.0f}"},
        {"metric": "Lead Time (days)", "baseline": f"{before.get('lead_time_days', base_lead_time):.0f}", "scenario": f"{after.get('lead_time_days', base_lead_time):.0f}", "delta": f"{after.get('lead_time_days', base_lead_time) - before.get('lead_time_days', base_lead_time):+.0f}"},
        {"metric": "Avg Daily Demand (u/d)", "baseline": f"{before.get('avg_daily_demand', base_daily):.1f}", "scenario": f"{after.get('avg_daily_demand', base_daily * request.demand_multiplier):.1f}", "delta": f"{after.get('avg_daily_demand', base_daily * request.demand_multiplier) - before.get('avg_daily_demand', base_daily):+.1f}"},
        {"metric": "14-Day Demand Forecast (u)", "baseline": f"{before.get('forecasted_demand', base_forecast_14d):.1f}", "scenario": f"{after.get('forecasted_demand', base_forecast_14d * request.demand_multiplier):.1f}", "delta": f"{after.get('forecasted_demand', base_forecast_14d * request.demand_multiplier) - before.get('forecasted_demand', base_forecast_14d):+.1f}"},
        {"metric": "Days of Supply (days)", "baseline": f"{before.get('days_of_supply', 0.0):.1f}", "scenario": f"{after.get('days_of_supply', 0.0):.1f}", "delta": f"{deltas.get('days_of_supply_delta', 0.0):+.1f}"},
        {"metric": "Reorder Point (units)", "baseline": f"{before.get('reorder_point_units', 0.0):.1f}", "scenario": f"{after.get('reorder_point_units', 0.0):.1f}", "delta": f"{deltas.get('reorder_point_delta', 0.0):+.1f}"},
        {"metric": "Operational Risk Status", "baseline": str(before.get('risk_level', 'NORMAL')).upper(), "scenario": str(after.get('risk_level', 'NORMAL')).upper(), "delta": "CHANGED" if deltas.get("risk_level_changed", False) else "UNCHANGED"},
    ]

    reorder_qty = max(0.0, after.get('reorder_point_units', 0.0) - after.get('current_stock', base_stock))
    decision_delta = {
        "do_nothing": {
            "title": "Do Nothing Scenario",
            "impacts": [
                f"Buffer depleted within {after.get('days_of_supply', 0.0):.1f} days.",
                "Stockout penalty incurred; customer fulfillments backlogged.",
                f"Operational exposure of approx ₹{base_stock * unit_cost:,.0f}."
            ]
        },
        "recommended_action": {
            "title": "Recommended Action (AI Decision)",
            "impacts": [
                f"Issue replenishment PO for {reorder_qty:.0f} units.",
                f"Enforce expedited supplier dispatch to hold lead time to {after.get('lead_time_days', base_lead_time):.0f} days.",
                "Preserves service level stability and eliminates stockout penalty."
            ]
        }
    }

    return {
        "sku_id": request.sku_id,
        "before": before,
        "after": after,
        "deltas": deltas,
        "comparison_table": comparison_table,
        "decision_delta": decision_delta
    }

@app.post("/api/simulations/delivery")
def run_delivery_simulation(request: DeliverySimRequest):
    """Executes delivery delay stress test scenario using simulate_delivery_scenario."""
    model, del_df = agent_tools._get_delivery_model()
    try:
        sim_res = simulate_delivery_scenario(
            model=model,
            df_deliveries=del_df,
            delivery_id=request.delivery_id,
            traffic_delay_override=request.traffic_delay_override,
            weather_condition_override=request.weather_condition_override
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    before = sim_res["before"]
    after = sim_res["after"]
    deltas = sim_res["deltas"]

    top_feats = after.get("top_features", {})
    feat_list = [{"feature": k, "impact_score": f"{v:+.4f}"} for k, v in top_feats.items()] if isinstance(top_feats, dict) else []

    decision_delta = {
        "do_nothing": {
            "title": "Do Nothing Scenario",
            "impacts": [
                "Shipment stuck in severe weather / congestion corridor.",
                "Promised delivery window missed by estimated delay duration.",
                "On-time delivery SLA breach penalty applied."
            ]
        },
        "recommended_action": {
            "title": "Recommended Action (AI Decision)",
            "impacts": [
                "Reroute shipment via alternate regional bypass to circumvent bottlenecks.",
                "Pre-notify receiving facility for dynamic cross-dock priority staging.",
                "If delay estimate exceeds 4 hours, dispatch emergency courier unit."
            ]
        }
    }

    return {
        "delivery_id": request.delivery_id,
        "before": before,
        "after": after,
        "deltas": deltas,
        "top_features": feat_list,
        "decision_delta": decision_delta
    }

@app.post("/api/simulations/logistics")
def run_logistics_simulation(request: LogisticsSimRequest):
    """Executes logistics routing fleet scenario using simulate_logistics_scenario."""
    _, del_df = agent_tools._get_delivery_model()
    del_records = del_df[del_df["delivery_id"].isin(request.delivery_ids)].to_dict(orient="records")
    for d in del_records:
        if "weight" not in d:
            d["weight"] = 100

    base_constraints = {"num_vehicles": 2, "capacities": [500] * 2}
    sim_res = simulate_logistics_scenario(
        delivery_ids=request.delivery_ids,
        df_deliveries=del_records,
        base_vehicle_constraints=base_constraints,
        capacity_multiplier=request.capacity_multiplier,
        num_vehicles_override=request.num_vehicles
    )

    before = sim_res["before"]
    after = sim_res["after"]
    deltas = sim_res["deltas"]

    decision_delta = {
        "do_nothing": {
            "title": "Do Nothing (Fixed / Unoptimized Dispatch)",
            "impacts": [
                "Underutilized vehicles run redundant cross-city mileage.",
                "Overloaded vehicles risk breakdown or safety compliance breach."
            ]
        },
        "recommended_action": {
            "title": "Recommended Action (VRP Optimization)",
            "impacts": [
                "Re-cluster shipments into optimal density zones.",
                "Minimize total fleet transit kilometers and driver overtime expenses."
            ]
        }
    }

    return {
        "before": before,
        "after": after,
        "deltas": deltas,
        "decision_delta": decision_delta
    }

# ---------------------------------------------------------------------------
# Legacy API Endpoints (Preserved for backward compatibility)
# ---------------------------------------------------------------------------

@app.post("/api/orchestrate", response_model=OrchestrateResponse)
def orchestrate(request: OrchestrateRequest):
    """Run the multi-agent decision loop for a given situation."""
    try:
        trace_id = run_agent_loop(request.situation)
        return OrchestrateResponse(trace_id=trace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traces", response_model=List[TraceResponse])
def get_traces(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recent decision traces."""
    traces = db.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).offset(skip).limit(limit).all()
    return traces

@app.get("/api/traces/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Get a specific decision trace."""
    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace

@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(status: Optional[str] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recommendations, optionally filtered by status."""
    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)
    recommendations = query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
    return recommendations

@app.post("/api/traces/{trace_id}/approval")
def approve_trace(trace_id: str, request: ApprovalRequest, db: Session = Depends(get_db)):
    """Approve or reject a recommendation based on its trace ID."""
    if request.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    trace = db.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()

    # Insert approval record
    approval = Approval(
        trace_id=trace_id,
        status=request.status,
        approver=request.approver,
        timestamp=datetime.now(timezone.utc),
        notes=request.notes
    )
    db.add(approval)

    # Update Recommendation status if present
    if rec:
        rec.status = request.status

    # Update DecisionTrace human_approval dict
    current_approval = trace.human_approval or {}
    new_approval = current_approval.copy()
    new_approval["status"] = request.status
    new_approval["approver"] = request.approver
    new_approval["timestamp"] = datetime.now(timezone.utc).isoformat()
    new_approval["notes"] = request.notes
    trace.human_approval = new_approval

    db.commit()
    return {"message": f"Trace {trace_id} {request.status} successfully"}
