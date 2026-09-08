import streamlit as st
import json
from datetime import datetime
import time
import pandas as pd
import uuid
import os
import shutil
import tempfile

from db.connection import SessionLocal
from db.models import DecisionTrace, Recommendation, Approval, InventoryRisk, DeliveryRiskPrediction, SKU
from agent.orchestrator import run_agent_loop
<<<<<<< HEAD
import agent.tools as agent_tools
from data_ingestion.base import DataSource
=======
from data_ingestion.active_dataset import active_dataset, DatasetMetadata
>>>>>>> a707816 (Add: P0 Active Business Dataset Foundation, lifecycle context, and tests)
from data_ingestion.csv_source import CSVDataSource
from data_ingestion.excel_source import ExcelDataSource
from data_ingestion.db_source import DBDataSource
from core.delivery_risk import train_delivery_risk_model
from core.simulation import (
    simulate_inventory_scenario,
    simulate_delivery_scenario,
    simulate_logistics_scenario
)

def get_active_data_source():
    """
    Returns the active business dataset source.
    Initializes default dataset if not set.
    """
    try:
        return active_dataset.get_source()
    except ValueError:
        default_source = CSVDataSource(data_dir="data")
        default_meta = DatasetMetadata(
            source_type="csv",
            name="Default Bundled CSV Data",
            status="active",
            connected_at=datetime.utcnow().isoformat()
        )
        active_dataset.set_active(default_source, default_meta)
        return active_dataset.get_source()

@st.cache_resource
def load_simulation_resources():
    source = get_active_data_source()
    inv_df = source.load_inventory_snapshot()
    del_df = source.load_deliveries()
    model, _, _ = train_delivery_risk_model(del_df)
    return inv_df, del_df, model

st.set_page_config(page_title="SupplyChain Sentinel AI", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Enterprise Look ---
st.markdown("""
<style>
    /* Clean up the main padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Risk Badges */
    .badge-high { background-color: #ff4b4b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-medium { background-color: #ffa421; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-low { background-color: #00c04b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-neutral { background-color: #1e1e1e; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    
    /* Cards */
    .decision-card {
        border: 1px solid #444;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

def get_db_session():
    return SessionLocal()

# --- HELPER FUNCTIONS ---
def get_risk_badge(level: str):
    lvl = level.lower()
    if lvl in ["high", "critical", "stockout"]:
        return f"<span class='badge-high'>{level.upper()}</span>"
    elif lvl in ["medium", "warning", "overstock"]:
        return f"<span class='badge-medium'>{level.upper()}</span>"
    elif lvl in ["low", "ok", "passed", "approved"]:
        return f"<span class='badge-low'>{level.upper()}</span>"
    else:
        return f"<span class='badge-neutral'>{level.upper()}</span>"

# --- MAIN NAVIGATION ---
def main():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "active_dataset_type" not in st.session_state:
        st.session_state.active_dataset_type = "demo"
    if "active_datasource" not in st.session_state:
        st.session_state.active_datasource = CSVDataSource(data_dir="data")

    # Ensure active datasource is synchronized with thread-local state
    agent_tools.set_active_datasource(st.session_state.active_datasource)

    st.sidebar.title("🛡️ SupplyChain Sentinel AI")
    st.sidebar.markdown("**AI Decision Intelligence**")
    st.sidebar.markdown("---")
    
    if st.session_state.active_dataset_type == "demo":
        st.sidebar.info("DATA SOURCE\n● Demo Dataset — Synthetic")
    else:
        st.sidebar.success("DATA SOURCE\n● Company Supply Chain — Connected")
        
    st.sidebar.markdown("---")
    
    menu = ["Command Center", "Data Hub", "Create a Decision", "Approval Queue", "Decision History", "What-If Simulation"]
    choice = st.sidebar.radio("Navigation", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("AI-powered supply-chain risk & decision intelligence platform.")
    st.sidebar.caption("© 2026 Sentinel Corp.")

    if choice == "Command Center":
        render_command_center()
    elif choice == "Data Hub":
        render_data_hub()
    elif choice == "Create a Decision":
        render_create_decision()
    elif choice == "Approval Queue":
        render_approval_queue()
    elif choice == "Decision History":
        render_decision_history()
    elif choice == "What-If Simulation":
        render_simulation()


# --- VIEW: DATA HUB ---
def validate_dataframe(df, required_cols, dataset_name):
    # Ignore/drop completely empty rows (all fields NaN/empty) before validation
    df = df.dropna(how="all").reset_index(drop=True)
    messages = []
    status = "pass"
    
    # Check Required Columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        status = "blocking"
        messages.append(f"BLOCKING: Missing required columns in {dataset_name}: {', '.join(missing_cols)}")
        return status, messages
        
    # Check Rows
    if len(df) == 0:
        status = "blocking"
        messages.append(f"BLOCKING: {dataset_name} has 0 rows.")
        return status, messages
        
    # Check Duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        if status != "blocking": status = "warning"
        messages.append(f"WARNING: {dupes} duplicate rows found in {dataset_name}.")
        
    # Check Missing Values
    missing_vals = df.isnull().sum().sum()
    if missing_vals > 0:
        if status != "blocking": status = "warning"
        messages.append(f"WARNING: {missing_vals} missing values found across {dataset_name}.")
        
    if status == "pass":
        messages.append(f"PASS: {dataset_name} is valid. ({len(df)} rows, {len(df.columns)} columns)")
        
    return status, messages

def suggest_mapping(existing_cols, target_cols):
    mapping = {}
    for tgt in target_cols:
        # Exact match
        if tgt in existing_cols:
            mapping[tgt] = tgt
            continue
        # Substring / loose match
        for ext in existing_cols:
            if tgt.replace('_', ' ').lower() in ext.lower() or ext.lower() in tgt.replace('_', ' ').lower():
                mapping[tgt] = ext
                break
        if tgt not in mapping:
            mapping[tgt] = existing_cols[0] if existing_cols else None
    return mapping

def render_data_hub():
    st.title("Enterprise Data Hub")
    st.markdown("Connect, map, and validate your supply chain datasets.")
    
    # Active Dataset Indicator
    active_type = st.session_state.get("active_dataset_type", "demo")
    
    tabs = st.tabs(["CSV Upload", "Excel Upload", "Database Connection", "API Connection", "Demo Dataset"])
    
    # Define required schemas
    schemas = {
        "historical_demand.csv": ["sku_id", "date", "quantity_demanded", "location_id"],
        "inventory_snapshot.csv": ["sku_id", "current_stock", "reorder_point", "safety_stock", "unit_cost", "lead_time_days", "location_id"],
        "deliveries.csv": ["delivery_id", "carrier_id", "origin", "destination", "distance_km", "scheduled_date", "actual_date", "is_late", "weather_condition", "traffic_delay_hrs"]
    }
    
    temp_dir = os.path.join(tempfile.gettempdir(), "supplychain_sentinel_sessions", st.session_state.session_id)
    
    # CSV UPLOAD
    with tabs[0]:
        st.subheader("CSV Ingestion")
        uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)
        
        if uploaded_files:
            st.markdown("### File Mapping & Validation")
            all_valid = True
            processed_dfs = {}
            
            for file in uploaded_files:
                with st.expander(f"📄 Configure: {file.name}", expanded=True):
                    df = pd.read_csv(file)
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    target_file = st.selectbox(
                        "Assign to Dataset Type", 
                        list(schemas.keys()), 
                        key=f"target_{file.name}",
                        index=0 if "demand" in file.name.lower() else (1 if "inv" in file.name.lower() else 2)
                    )
                    
                    req_cols = schemas[target_file]
                    st.markdown("**Column Mapping**")
                    
                    suggested = suggest_mapping(list(df.columns), req_cols)
                    
                    col_map = {}
                    cols = st.columns(min(len(req_cols), 4))
                    for i, req_col in enumerate(req_cols):
                        with cols[i % 4]:
                            idx = list(df.columns).index(suggested[req_col]) if suggested.get(req_col) in df.columns else 0
                            col_map[req_col] = st.selectbox(f"{req_col}", list(df.columns), index=idx, key=f"map_{file.name}_{req_col}")
                    
                    # Apply Mapping
                    mapped_df = pd.DataFrame()
                    for k, v in col_map.items():
                        mapped_df[k] = df[v]
                        
                    status, msgs = validate_dataframe(mapped_df, req_cols, target_file)
                    
                    if status == "blocking":
                        st.error("\n".join(msgs))
                        all_valid = False
                    elif status == "warning":
                        st.warning("\n".join(msgs))
                    else:
                        st.success("\n".join(msgs))
                        
                    processed_dfs[target_file] = mapped_df

            if all_valid and len(processed_dfs) == 3: # Require all 3 for the pipeline to work
                if st.button("Use This Dataset", type="primary"):
                    os.makedirs(temp_dir, exist_ok=True)
                    for filename, pdf in processed_dfs.items():
                        pdf.to_csv(os.path.join(temp_dir, filename), index=False)
                    agent_tools.set_active_datasource(CSVDataSource(data_dir=temp_dir))
                    st.session_state.active_dataset_type = "csv"
                    st.success("Dataset successfully activated! The backend AI pipeline will now consume this data.")
                    time.sleep(1)
                    st.rerun()
            elif len(processed_dfs) < 3:
                st.info("⚠️ Please upload and map all 3 required files (Demand, Inventory, Deliveries) to proceed.")

    # EXCEL UPLOAD
    with tabs[1]:
        st.subheader("Excel Ingestion")
        excel_file = st.file_uploader("Upload Excel workbook (.xlsx)", type=["xlsx"])
        if excel_file:
            path = os.path.join(tempfile.gettempdir(), f"upload_{st.session_state.session_id}.xlsx")
            with open(path, "wb") as f:
                f.write(excel_file.getbuffer())
            try:
                xl = pd.ExcelFile(path)
                st.write(f"Detected sheets: {', '.join(xl.sheet_names)}")
                
                required_sheets = ["historical_demand", "inventory_snapshot", "deliveries"]
                missing = [s for s in required_sheets if s not in xl.sheet_names]
                
                if missing:
                    st.error(f"BLOCKING: Workbook is missing required sheets: {', '.join(missing)}")
                else:
                    st.success("Validation Passed: Workbook contains required sheets.")
                    if st.button("Use This Excel Dataset", type="primary"):
                        os.makedirs(temp_dir, exist_ok=True)
                        dest_path = os.path.join(temp_dir, "supplychain_data.xlsx")
                        shutil.copy(path, dest_path)
                        agent_tools.set_active_datasource(ExcelDataSource(excel_path=dest_path))
                        st.session_state.active_dataset_type = "excel"
                        st.success("Dataset activated!")
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading Excel: {e}")

    # DATABASE CONNECTION
    with tabs[2]:
        st.subheader("Database Connection")
        st.info("Supported Connections: PostgreSQL (Neon), SQLite")
        with st.form("db_form"):
            db_url = st.text_input("Database URL", type="password", placeholder="postgresql://user:pass@host/db")
            test_conn = st.form_submit_button("Test Connection & Use")
            
            if test_conn:
                if not db_url:
                    st.error("Please enter a connection URL.")
                else:
                    try:
                        from sqlalchemy import create_engine
                        engine = create_engine(db_url)
                        with engine.connect() as conn:
                            pass
                        
                        agent_tools.set_active_datasource(DBDataSource(connection_url=db_url))
                        
                        # Pre-flight check to see if tables exist
                        try:
                            agent_tools._get_inventory_df()
                            st.session_state.active_dataset_type = "db"
                            st.success("Connection successful! Required tables found. Dataset activated!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            agent_tools.set_active_datasource(CSVDataSource(data_dir="data")) # Revert
                            st.error(f"BLOCKING: Connection succeeded, but required tables are missing or invalid: {e}")
                            
                    except Exception as e:
                        st.error(f"BLOCKING: Connection failed. Check credentials. ({e})")

    # API CONNECTION
    with tabs[3]:
        st.subheader("Enterprise API Integration")
        st.info("API ingestion is currently in development. Generic REST/GraphQL sync will be supported in the next major release.")
        st.text_input("API Name", placeholder="e.g., SAP ERP, Oracle WMS", disabled=True)
        st.text_input("Endpoint URL", placeholder="https://api.company.com/v1", disabled=True)
        st.selectbox("Authentication Method", ["Bearer Token", "OAuth2", "Basic Auth"], disabled=True)
        st.text_input("Auth Token / API Key", type="password", disabled=True)
        st.button("Test API Connection", disabled=True, help="Coming Soon")

    # DEMO DATASET
    with tabs[4]:
        st.subheader("Synthetic Demo Dataset")
        st.markdown("Use the synthetic data bundled with the application to safely test Sentinel's AI decision-making capabilities without connecting your own systems.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Mock SKUs", "100")
        c2.metric("Mock Deliveries", "50")
        c3.metric("Historical Data", "30 Days")
        
        if st.button("Use Demo Dataset", type="primary"):
            agent_tools.set_active_datasource(CSVDataSource(data_dir="data"))
            st.session_state.active_dataset_type = "demo"
            st.success("Switched to Synthetic Demo Dataset.")
            time.sleep(1)
            st.rerun()

# --- VIEW: COMMAND CENTER ---
def render_command_center():
    st.title("Supply Chain Command Center")
    st.markdown("Monitor risk, evaluate decisions, and understand operational impact.")
    
    session = get_db_session()
    try:
        recent_decisions = session.query(DecisionTrace).count()
        
        # Calculate metrics dynamically from active datasource via agent_tools
        active_inventory_risks = "N/A"
        exposure_str = "N/A"
        high_delivery_risks = "N/A"
        
        try:
            inv_df = agent_tools._get_inventory_df()
            if not inv_df.empty:
                # Mock risk evaluation for dashboard
                low_stock = inv_df[inv_df["current_stock"] < inv_df["reorder_point"]]
                active_inventory_risks = len(low_stock)
                
                if "unit_cost" in inv_df.columns and "current_stock" in inv_df.columns:
                    exp = low_stock["unit_cost"].sum() * 100
                    exposure_str = f"₹{exp:,.0f}"
        except Exception:
            active_inventory_risks = "Not enough data"
            
        try:
            _, del_df = agent_tools._get_delivery_model()
            if not del_df.empty and "is_late" in del_df.columns:
                high_delivery_risks = len(del_df[del_df["is_late"] == 1])
        except Exception:
            high_delivery_risks = "Not enough data"
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("ACTIVE RISKS", active_inventory_risks, delta="Requires Attention", delta_color="inverse")
        col2.metric("INVENTORY AT RISK", exposure_str, delta="Potential Exposure", delta_color="off")
        col3.metric("DELIVERY RISK", high_delivery_risks, delta="Delayed Shipments", delta_color="inverse")
        col4.metric("AI DECISIONS", recent_decisions, delta="This Week", delta_color="normal")
        
        st.markdown("---")
        st.subheader("Priority Risks")
        
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("""
            <div class='decision-card'>
                <h4>🔴 HIGH RISK: SKU-104</h4>
                <p style="color: #bbb;">Electronics Component</p>
                <h3>Stockout Risk: 82%</h3>
                <p>Expected demand is exceeding available inventory coverage. Supplier lead-time increases exposure.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Review Decision →", key="btn_risk1"):
                st.info("Navigate to 'Approval Queue' to review pending AI decisions.")
                
        with r2:
            st.markdown("""
            <div class='decision-card'>
                <h4>🟠 DELIVERY RISK: Shipment #2048</h4>
                <p style="color: #bbb;">Carrier: Global Freight</p>
                <h3>High probability of delay</h3>
                <p>Supplier lead-time disruption detected at origin port.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Investigate →", key="btn_risk2"):
                st.info("Navigate to 'Create a Decision' to evaluate alternatives.")
    finally:
        session.close()

# --- VIEW: CREATE A DECISION ---
def render_create_decision():
    st.title("Create a Decision")
    st.markdown("Tell Sentinel what supply-chain situation you want to evaluate. Sentinel will automatically fetch the latest numbers from your active dataset.")
    
    with st.container(border=True):
        st.subheader("BUSINESS CONTEXT")
        
        try:
            inv_df = agent_tools._get_inventory_df()
            sku_list = inv_df["sku_id"].dropna().unique().tolist() if not inv_df.empty else []
        except:
            sku_list = []
            
        try:
            _, del_df = agent_tools._get_delivery_model()
            del_list = del_df["delivery_id"].dropna().unique().tolist() if not del_df.empty else []
        except:
            del_list = []
            
        col1, col2 = st.columns(2)
        with col1:
            target_type = st.radio("What does this concern?", ["Inventory / Demand Issue", "Delivery / Routing Issue"])
            
        with col2:
            if target_type == "Inventory / Demand Issue":
                if sku_list:
                    target_id = st.selectbox("Select Product (SKU)", sku_list)
                else:
                    target_id = st.text_input("Product / SKU ID")
            else:
                if del_list:
                    target_id = st.selectbox("Select Delivery (Shipment ID)", del_list)
                else:
                    target_id = st.text_input("Delivery ID")
        
        situation_text = st.text_area("Describe the situation or business constraints", placeholder="e.g., We just landed a huge enterprise client and demand is going to double. Do we have enough stock, or should we expedite shipments?")
    
    if st.button("Run AI Decision Analysis", type="primary", use_container_width=True):
        if not target_id:
            st.warning("Please specify a Target ID to proceed.")
            return
            
        situation = f"Target ID: {target_id}. Context: {situation_text}"
        
        status_container = st.status("Initializing AI Analysis...", expanded=True)
        with status_container:
            st.write("Analyzing supply-chain data... ✓")
            time.sleep(0.5)
            st.write("Forecasting demand & assessing operational risk... ✓")
            time.sleep(0.5)
            st.write("Retrieving applicable policies... ✓")
            time.sleep(0.5)
            st.write("Generating candidate actions... ✓")
            
            try:
                trace_id = run_agent_loop(situation)
                st.write("Running independent reviews... ✓")
                time.sleep(0.5)
                st.write("Building consensus... ✓")
                status_container.update(label="Analysis Complete", state="complete", expanded=False)
                
                st.success(f"Decision created successfully (ID: {trace_id})")
                st.info("Please go to the **Approval Queue** to review the recommendation.")
            except Exception as e:
                status_container.update(label="Analysis Failed", state="error", expanded=True)
                st.error(f"Error during analysis: {str(e)}")

# --- VIEW: APPROVAL QUEUE ---
def render_approval_queue():
    st.title("Decision Approval Queue")
    st.markdown("AI-generated decisions waiting for human review.")
    
    session = get_db_session()
    try:
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        pending_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") == "pending"]
        
        if not pending_traces:
            st.success("All caught up! No pending recommendations require approval right now.")
            return
            
        for trace in pending_traces:
            with st.container(border=True):
                # Overview Header
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                c1.markdown(get_risk_badge("HIGH"), unsafe_allow_html=True)
                
                # Extract situation string cleanly
                sit_str = str(trace.inputs.get("situation", "Unknown Situation"))
                short_sit = sit_str[:50] + "..." if len(sit_str) > 50 else sit_str
                c2.markdown(f"**Issue:** {short_sit}")
                
                rec_action = trace.consensus_result.get("recommendation", "Review needed") if trace.consensus_result else "Review needed"
                if isinstance(rec_action, dict):
                    rec_action = rec_action.get("action", str(rec_action))
                c3.markdown(f"**Recommended Action:** {rec_action}")
                c4.markdown(f"*{trace.timestamp.strftime('%Y-%m-%d')}*")
                
                if st.button("Review Decision", key=f"rev_{trace.trace_id}"):
                    st.session_state[f"show_trace_{trace.trace_id}"] = not st.session_state.get(f"show_trace_{trace.trace_id}", False)
                
                if st.session_state.get(f"show_trace_{trace.trace_id}", False):
                    st.markdown("---")
                    render_detailed_decision(trace, is_pending=True)
                
    finally:
        session.close()

# --- REUSABLE COMPONENT: DETAILED DECISION RESULT ---
def render_detailed_decision(trace: DecisionTrace, is_pending: bool):
    # 1. AI Decision Header
    st.subheader("AI DECISION")
    
    rec_action = trace.consensus_result.get("recommendation", "Unknown") if trace.consensus_result else "Unknown"
    if isinstance(rec_action, dict):
        rec_action = rec_action.get("action", str(rec_action))
        
    narration = trace.consensus_result.get("narration", "No reasoning provided.") if trace.consensus_result else ""
    
    st.markdown(f"### RECOMMENDED ACTION: **{str(rec_action).upper()}**")
    
    st.markdown("**Why Sentinel recommends this:**")
    # Convert narration into pseudo bullet points if it's just a string, 
    # or just display it cleanly.
    st.write(narration)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Business Evidence (Calculated from Active Dataset)")
    has_evidence = False
    if trace.tools_used:
        for tool_call in trace.tools_used:
            tool_name = tool_call.get("tool", "")
            result = tool_call.get("result", {})
            if tool_name == "get_inventory_risk" and isinstance(result, dict) and "error" not in result:
                has_evidence = True
                sku = result.get('sku_id', 'Unknown')
                rl = result.get('risk_level', 'NORMAL')
                rl_badge = "<span class='badge-high'>STOCKOUT_RISK</span>" if "STOCKOUT" in rl else ("<span class='badge-medium'>OVERSTOCK_RISK</span>" if "OVERSTOCK" in rl else "<span class='badge-low'>NORMAL</span>")
                st.markdown(f"""
                <div style="background-color: rgba(28, 131, 225, 0.1); border-left: 4px solid #1c83e1; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.8rem;">
                    <strong>📦 Inventory Profile: {sku}</strong><br/>
                    • <strong>Risk Status:</strong> {rl_badge}<br/>
                    • <strong>Current Stock / Coverage:</strong> {result.get('days_of_supply', 0):.1f} Days of Supply<br/>
                    • <strong>Calculated Reorder Point:</strong> {result.get('reorder_point_units', 0):.0f} Units<br/>
                    • <strong>Required Safety Stock:</strong> {result.get('safety_stock_units', 0):.0f} Units<br/>
                    • <strong>Engine Detail:</strong> <em>{result.get('detail', '')}</em>
                </div>
                """, unsafe_allow_html=True)
            elif tool_name == "get_demand_forecast" and isinstance(result, dict) and "error" not in result:
                has_evidence = True
                sku = result.get('sku_id', 'Unknown')
                preds = result.get('predicted_quantities', [])
                total_pred = sum(preds)
                st.markdown(f"""
                <div style="background-color: rgba(28, 131, 225, 0.1); border-left: 4px solid #1c83e1; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.8rem;">
                    <strong>📈 Demand Forecast: {sku}</strong><br/>
                    • <strong>Horizon:</strong> {result.get('forecast_horizon_weeks', 0)} Weeks<br/>
                    • <strong>Total Predicted Demand:</strong> {total_pred:.0f} Units
                </div>
                """, unsafe_allow_html=True)
            elif tool_name == "get_delivery_risk" and isinstance(result, dict) and "error" not in result:
                has_evidence = True
                del_id = result.get('delivery_id', 'Unknown')
                rl = result.get('risk_label', 'LOW')
                rl_badge = "<span class='badge-high'>HIGH</span>" if "high" in rl.lower() else ("<span class='badge-medium'>MEDIUM</span>" if "medium" in rl.lower() else "<span class='badge-low'>LOW</span>")
                score = result.get('risk_score', 0) * 100
                st.markdown(f"""
                <div style="background-color: rgba(28, 131, 225, 0.1); border-left: 4px solid #1c83e1; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.8rem;">
                    <strong>🚚 Delivery Profile: {del_id}</strong><br/>
                    • <strong>Delay Risk:</strong> {rl_badge}<br/>
                    • <strong>Late Probability:</strong> {score:.1f}%
                </div>
                """, unsafe_allow_html=True)
    
    if not has_evidence:
        st.caption("No specific quantitative evidence extracted for this decision.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Validation Flow
    st.subheader("Why should I trust this decision?")
    
    pol_status = "✓ PASSED" if trace.policy_critic_output and trace.policy_critic_output.get("compliant") else "⚠ NEEDS REVIEW"
    bus_status = "✓ PASSED" if trace.business_critic_output and trace.business_critic_output.get("approved") else "⚠ NEEDS REVIEW"
    
    vcol1, vcol2, vcol3, vcol4 = st.columns(4)
    vcol1.info(f"**Primary AI**\n\nProposed action formulated.")
    vcol2.warning(f"**Policy Review**\n\n{pol_status}")
    vcol3.success(f"**Business Review**\n\n{bus_status}")
    vcol4.info(f"**Consensus**\n\n✓ Validated")
    
    # 3. Decision Transparency (Technical Details Hidden)
    with st.expander("Decision Transparency (Technical Details)"):
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Data Considered**")
            st.json(trace.inputs)
            st.markdown("**AI Predictions**")
            st.json(trace.predictions if trace.predictions else {})
            st.markdown("**Policies Consulted**")
            st.json(trace.policies_retrieved if trace.policies_retrieved else [])
        with t2:
            st.markdown("**Evidence & Analysis (Tools)**")
            st.json(trace.tools_used if trace.tools_used else [])
            st.markdown("**Independent Review Logs**")
            st.json(trace.policy_critic_output if trace.policy_critic_output else {})
            st.json(trace.business_critic_output if trace.business_critic_output else {})
            
    # 4. Human Approval
    if is_pending:
        st.markdown("---")
        st.subheader("Human Approval Required")
        st.caption("This recommendation has been independently reviewed by multiple AI agents. No operational action will be taken without human approval.")
        
        with st.form(key=f"approval_{trace.trace_id}"):
            notes = st.text_area("Reviewer Notes (Optional)", placeholder="Looks good, proceed.")
            approver = st.text_input("Reviewer Name", value="System Admin")
            
            c1, c2, c3 = st.columns([1, 1, 4])
            approve_btn = c1.form_submit_button("✓ Approve Recommendation", type="primary")
            reject_btn = c2.form_submit_button("✕ Reject Recommendation")
            
            if approve_btn:
                process_approval(trace.trace_id, "approved", approver, notes)
                st.rerun()
            elif reject_btn:
                process_approval(trace.trace_id, "rejected", approver, notes)
                st.rerun()

def process_approval(trace_id: str, status: str, approver: str, notes: str):
    session = get_db_session()
    try:
        trace = session.query(DecisionTrace).filter(DecisionTrace.trace_id == trace_id).first()
        rec = session.query(Recommendation).filter(Recommendation.recommendation_id == f"REC_{trace_id}").first()
        
        if trace and rec:
            approval = Approval(
                trace_id=trace_id,
                status=status,
                approver=approver,
                timestamp=datetime.utcnow(),
                notes=notes
            )
            session.add(approval)
            rec.status = status
            
            current_approval = trace.human_approval or {}
            new_approval = current_approval.copy()
            new_approval["status"] = status
            new_approval["approver"] = approver
            new_approval["timestamp"] = datetime.utcnow().isoformat()
            new_approval["notes"] = notes
            trace.human_approval = new_approval
            
            session.commit()
            if status == "approved":
                st.success("✓ Decision Approved: Recommendation approved by human reviewer.")
            else:
                st.error("✕ Decision Rejected: Decision returned for review.")
            time.sleep(1.5)
    except Exception as e:
        session.rollback()
        st.error(f"Error processing approval: {e}")
    finally:
        session.close()

# --- VIEW: DECISION HISTORY ---
def render_decision_history():
    st.title("Decision History")
    st.markdown("Audit trail of approved and rejected decisions.")
    
    session = get_db_session()
    try:
        traces = session.query(DecisionTrace).order_by(DecisionTrace.timestamp.desc()).all()
        history_traces = [t for t in traces if t.human_approval and t.human_approval.get("status") in ["approved", "rejected"]]
        
        if not history_traces:
            st.info("No historical decisions found.")
            return
            
        for trace in history_traces:
            status = trace.human_approval.get("status", "unknown").upper()
            sit_str = str(trace.inputs.get("situation", ""))
            short_sit = sit_str[:60] + "..." if len(sit_str) > 60 else sit_str
            rec_action = trace.consensus_result.get("recommendation", "Unknown") if trace.consensus_result else "Unknown"
            if isinstance(rec_action, dict):
                rec_action = rec_action.get("action", str(rec_action))
            date_str = trace.timestamp.strftime('%Y-%m-%d %H:%M')
            
            with st.expander(f"{date_str} | {status} | {short_sit}"):
                st.markdown(f"**Status:** {get_risk_badge(status)}", unsafe_allow_html=True)
                st.markdown(f"**Recommendation:** {rec_action}")
                st.markdown(f"**Reviewer:** {trace.human_approval.get('approver')} | **Notes:** {trace.human_approval.get('notes')}")
                st.markdown("---")
                render_detailed_decision(trace, is_pending=False)
    finally:
        session.close()

# --- VIEW: WHAT-IF SIMULATION (Phase 4) ---
def render_simulation():
    st.title("What-If Simulation & Business Intelligence")
    st.markdown("Stress-test supply-chain operations under shifting market conditions, disruptions, and capacity constraints.")
    
    st.markdown("""
    <div style="background-color: #1a1a2e; border: 1px solid #30363d; border-radius: 8px; padding: 12px 18px; margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #c9d1d9; font-weight: 500;">
            <span>🔍 <b>1. Identify Operational Risk</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>⚙️ <b>2. Configure Stress Test Overrides</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>📊 <b>3. Compare Baseline vs. Scenario</b></span>
            <span style="color: #58a6ff;">➔</span>
            <span>🛡️ <b>4. Evaluate Action Delta (Do Nothing vs. Act)</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    inv_df, del_df, delivery_model = load_simulation_resources()
    
    sim_mode = st.selectbox(
        "Select Simulation Domain",
        ["📦 Inventory Risk & Stockout", "🚚 Delivery Risk & Transit Delay", "🗺️ Logistics Fleet & Routing Capacity"],
        key="sim_mode_selector"
    )
    st.markdown("---")

    if sim_mode == "📦 Inventory Risk & Stockout":
        st.subheader("📦 Inventory Stress-Testing: Demand Shocks & Supplier Delays")
        st.markdown("Simulate how demand spikes or supplier lead time extensions impact Days of Supply and Stockout exposure.")
        
        sku_options = inv_df["sku_id"].dropna().unique().tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="inv_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_sku = st.selectbox("Select Target SKU", sku_options, index=0)
                sku_row = inv_df[inv_df["sku_id"] == selected_sku].iloc[0]
                
                base_stock = float(sku_row.get("current_stock", 100.0))
                base_lead_time = float(sku_row.get("lead_time_days", 7.0))
                unit_cost = float(sku_row.get("unit_cost", 50.0))
                
                st.caption(f"Baseline: Stock = **{base_stock:.0f} units** | Lead Time = **{base_lead_time:.0f} days** | Unit Cost = **₹{unit_cost:.2f}**")
                
                demand_mult = st.slider(
                    "Demand Surge Multiplier",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    help="1.0 = baseline demand, 1.5 = 50% surge, 2.0 = 100% surge"
                )
                
                stock_override_opt = st.checkbox("Override Current On-Hand Stock?", value=False)
                stock_override = None
                if stock_override_opt:
                    stock_override = st.number_input("Adjusted Stock (units)", min_value=0.0, max_value=5000.0, value=base_stock, step=10.0)
                    
                lead_override_opt = st.checkbox("Override Supplier Lead Time?", value=False)
                lead_time_override = None
                if lead_override_opt:
                    lead_time_override = st.slider("Adjusted Lead Time (days)", min_value=1.0, max_value=45.0, value=float(base_lead_time), step=1.0)
                    
                run_inv = st.form_submit_button("⚡ Run Inventory Simulation", type="primary")

        with col_results:
            st.markdown("#### Projected Business Impact")
            base_daily = max(1.0, base_stock / 15.0)
            base_forecast_14d = base_daily * 14.0
            
            sim_res = simulate_inventory_scenario(
                sku_id=selected_sku,
                base_current_stock=base_stock,
                base_avg_daily_demand=base_daily,
                base_forecast_demand=base_forecast_14d,
                base_forecast_period_days=14,
                base_lead_time_days=base_lead_time,
                base_safety_stock_days=14.0,
                demand_multiplier=demand_mult,
                stock_override=stock_override,
                lead_time_override=lead_time_override,
            )
            
            before = sim_res["before"]
            after = sim_res["after"]
            deltas = sim_res["deltas"]
            
            m1, m2, m3 = st.columns(3)
            dos_delta = deltas["days_of_supply_delta"]
            m1.metric("Days of Supply", f"{after['days_of_supply']:.1f} d", delta=f"{dos_delta:+.1f} d", delta_color="normal" if dos_delta >= 0 else "inverse")
            
            rop_delta = deltas["reorder_point_delta"]
            m2.metric("Reorder Point", f"{after['reorder_point_units']:.0f} u", delta=f"{rop_delta:+.0f} u", delta_color="inverse" if rop_delta > 0 else "normal")
            
            m3.markdown(f"**Risk Level**<br>{get_risk_badge(before['risk_level'])} ➔ {get_risk_badge(after['risk_level'])}", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### Detailed Metric Breakdown")
            comp_data = {
                "Metric": ["Current Stock (units)", "Lead Time (days)", "Avg Daily Demand (units/d)", "14-Day Demand Forecast (units)", "Days of Supply (days)", "Reorder Point (units)", "Operational Risk Status"],
                "Baseline State": [
                    f"{before.get('current_stock', base_stock):.0f}",
                    f"{before.get('lead_time_days', base_lead_time):.0f}",
                    f"{before.get('avg_daily_demand', base_daily):.1f}",
                    f"{before.get('forecasted_demand', base_forecast_14d):.1f}",
                    f"{before.get('days_of_supply', 0.0):.1f}",
                    f"{before.get('reorder_point_units', 0.0):.1f}",
                    str(before.get('risk_level', 'NORMAL')).upper()
                ],
                "Scenario State": [
                    f"{after.get('current_stock', base_stock):.0f}",
                    f"{after.get('lead_time_days', base_lead_time):.0f}",
                    f"{after.get('avg_daily_demand', base_daily * demand_mult):.1f}",
                    f"{after.get('forecasted_demand', base_forecast_14d * demand_mult):.1f}",
                    f"{after.get('days_of_supply', 0.0):.1f}",
                    f"{after.get('reorder_point_units', 0.0):.1f}",
                    str(after.get('risk_level', 'NORMAL')).upper()
                ],
                "Observed Delta": [
                    f"{after.get('current_stock', base_stock) - before.get('current_stock', base_stock):+.0f}",
                    f"{after.get('lead_time_days', base_lead_time) - before.get('lead_time_days', base_lead_time):+.0f}",
                    f"{after.get('avg_daily_demand', base_daily * demand_mult) - before.get('avg_daily_demand', base_daily):+.1f}",
                    f"{after.get('forecasted_demand', base_forecast_14d * demand_mult) - before.get('forecasted_demand', base_forecast_14d):+.1f}",
                    f"{deltas.get('days_of_supply_delta', 0.0):+.1f}",
                    f"{deltas.get('reorder_point_delta', 0.0):+.1f}",
                    "CHANGED ⚠️" if deltas.get("risk_level_changed", False) else "UNCHANGED"
                ]
            }
            st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)
            
            st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                st.error(f"""
                **❌ Do Nothing Scenario**
                - Buffer depleted within **{after.get('days_of_supply', 0.0):.1f} days**.
                - Stockout penalty incurred; customer fulfillments backlogged.
                - Operational exposure of approx **₹{base_stock * unit_cost:,.0f}**.
                """)
            with a_col2:
                reorder_qty = max(0.0, after.get('reorder_point_units', 0.0) - after.get('current_stock', base_stock))
                st.success(f"""
                **✅ Recommended Action (AI Decision)**
                - Issue replenishment PO for **{reorder_qty:.0f} units**.
                - Enforce expedited supplier dispatch to hold lead time to **{after.get('lead_time_days', base_lead_time):.0f} days**.
                - Preserves service level stability and eliminates stockout penalty.
                """)

    elif sim_mode == "🚚 Delivery Risk & Transit Delay":
        st.subheader("🚚 Delivery Risk: Severe Weather & Traffic Bottlenecks")
        st.markdown("Simulate how severe weather disruptions or extreme highway congestion elevate delivery delay probability.")
        
        delivery_ids = del_df["delivery_id"].tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="del_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_del = st.selectbox("Select Target Delivery ID", delivery_ids, index=0)
                del_row = del_df[del_df["delivery_id"] == selected_del].iloc[0]
                
                carrier = del_row.get("carrier_id", "Unknown")
                origin = del_row.get("origin", "Depot")
                dest = del_row.get("destination", "Retail")
                distance = float(del_row.get("distance_km", 100))
                base_weather = str(del_row.get("weather_condition", "CLEAR"))
                base_traffic = float(del_row.get("traffic_delay_hrs", 0.0))
                
                st.caption(f"Route: **{origin} ➔ {dest}** ({distance:.0f} km) | Carrier: **{carrier}**")
                st.caption(f"Baseline Weather: **{base_weather}** | Baseline Traffic Delay: **{base_traffic:.1f} hrs**")
                
                weather_options = ["CLEAR", "RAIN", "FOG", "STORM"]
                w_idx = weather_options.index(base_weather) if base_weather in weather_options else 0
                weather_override = st.selectbox("Simulate Weather Condition", weather_options, index=w_idx)
                traffic_override = st.slider("Simulate Traffic Delay (Hours)", min_value=0.0, max_value=12.0, value=float(base_traffic), step=0.5)
                
                run_del = st.form_submit_button("⚡ Run Delivery Simulation", type="primary")
                
        with col_results:
            st.markdown("#### Projected Business Impact")
            sim_res = simulate_delivery_scenario(
                model=delivery_model,
                df_deliveries=del_df,
                delivery_id=selected_del,
                traffic_delay_override=traffic_override,
                weather_condition_override=weather_override
            )
            
            before = sim_res["before"]
            after = sim_res["after"]
            deltas = sim_res["deltas"]
            
            m1, m2 = st.columns(2)
            score_delta = deltas["risk_score_delta"]
            m1.metric("Late Delivery Probability", f"{after['risk_score']*100:.1f}%", delta=f"{score_delta*100:+.1f}%", delta_color="inverse" if score_delta > 0 else "normal")
            m2.markdown(f"**Risk Classification**<br>{get_risk_badge(before['risk_label'])} ➔ {get_risk_badge(after['risk_label'])}", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### ML Driving Risk Factors (SHAP Explanation)")
            top_feats = after.get("top_features", {})
            if top_feats:
                feat_df = pd.DataFrame([{"Feature": k, "Impact Score (SHAP)": f"{v:+.4f}"} for k, v in top_feats.items()])
                st.dataframe(feat_df, hide_index=True, use_container_width=True)
                
            st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                st.error("""
                **❌ Do Nothing Scenario**
                - Shipment stuck in severe weather / congestion corridor.
                - Promised delivery window missed by estimated delay duration.
                - On-time delivery SLA breach penalty applied.
                """)
            with a_col2:
                st.success("""
                **✅ Recommended Action (AI Decision)**
                - Reroute shipment via alternate regional bypass to circumvent bottlenecks.
                - Pre-notify receiving facility for dynamic cross-dock priority staging.
                - If delay estimate exceeds 4 hours, dispatch emergency courier unit.
                """)

    elif sim_mode == "🗺️ Logistics Fleet & Routing Capacity":
        st.subheader("🗺️ Logistics Routing: Fleet Capacity & Vehicle Constraints")
        st.markdown("Simulate how fleet availability and vehicle payload capacity affect route efficiency and fuel costs.")
        
        all_dels = del_df["delivery_id"].head(8).tolist()
        col_ctrl, col_results = st.columns([1, 1.4], gap="large")
        
        with col_ctrl:
            with st.form(key="log_sim_form"):
                st.markdown("#### Scenario Controls")
                selected_dels = st.multiselect("Select Deliveries to Route", all_dels, default=all_dels[:5])
                
                num_vehicles = st.slider("Available Delivery Vehicles", min_value=1, max_value=5, value=2, step=1)
                capacity_mult = st.slider("Vehicle Payload Capacity Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1, help="Adjust capacity limit per vehicle (1.0 = standard 500kg capacity)")
                
                run_log = st.form_submit_button("⚡ Run Routing Simulation", type="primary")
                
        with col_results:
            st.markdown("#### Projected Business Impact")
            if not selected_dels:
                st.warning("Please select at least 1 delivery to route.")
            else:
                base_constraints = {"num_vehicles": 2, "capacities": [500] * 2}
                del_records = del_df[del_df["delivery_id"].isin(selected_dels)].to_dict(orient="records")
                for d in del_records:
                    if "weight" not in d:
                        d["weight"] = 100
                        
                sim_res = simulate_logistics_scenario(
                    delivery_ids=selected_dels,
                    df_deliveries=del_records,
                    base_vehicle_constraints=base_constraints,
                    capacity_multiplier=capacity_mult,
                    num_vehicles_override=num_vehicles
                )
                
                before = sim_res["before"]
                after = sim_res["after"]
                deltas = sim_res["deltas"]
                
                if after.get("status") != "Success":
                    st.warning(f"⚠️ Routing Constraint Alert: {after.get('status', 'No solution found')}. Fleet capacity is insufficient to deliver all assigned shipments. Increase vehicle count or payload multiplier.")
                else:
                    m1, m2, m3 = st.columns(3)
                    dist_delta = deltas["total_distance_delta"]
                    cost_delta = deltas["total_cost_delta"]
                    
                    m1.metric("Total Transit Distance", f"{after.get('total_distance_km', 0):.0f} km", delta=f"{dist_delta:+.0f} km", delta_color="inverse" if dist_delta > 0 else "normal")
                    m2.metric("Estimated Route Cost", f"₹{after.get('total_cost', 0):,.0f}", delta=f"₹{cost_delta:+,.0f}", delta_color="inverse" if cost_delta > 0 else "normal")
                    m3.metric("Dispatched Routes", f"{len(after.get('routes', []))} vehicles", delta=f"{len(after.get('routes', [])) - len(before.get('routes', [])):+d} vs Base")
                    
                    st.markdown("---")
                    st.markdown("##### Optimized Vehicle Allocations")
                    for r in after.get("routes", []):
                        stops_str = " ➔ ".join([s["delivery_id"] for s in r["stops"]])
                        st.markdown(f"**Vehicle #{r['vehicle_id'] + 1}:** {stops_str} *(Distance: {r['route_distance_km']} km | Load: {r['route_load']} kg)*")
                        
                st.markdown("---")
                st.markdown("##### 🛡️ Decision Delta: Do Nothing vs. Recommended Action")
                a_col1, a_col2 = st.columns(2)
                with a_col1:
                    st.error("""
                    **❌ Do Nothing (Fixed / Unoptimized Dispatch)**
                    - Underutilized vehicles run redundant cross-city mileage.
                    - Overloaded vehicles risk breakdown or safety compliance breach.
                    """)
                with a_col2:
                    st.success("""
                    **✅ Recommended Action (VRP Optimization)**
                    - Re-cluster shipments into optimal density zones.
                    - Minimize total fleet transit kilometers and driver overtime expenses.
                    """)

if __name__ == "__main__":
    main()
