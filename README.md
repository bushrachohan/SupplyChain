# 🛡️ SupplyChain Sentinel AI

> **Autonomous Supply Chain Risk Intelligence & Multi-Agent Decision Platform**  
> An end-to-end system that forecasts demand, detects compounding inventory & delivery risks, optimizes routes, retrieves enterprise policies via RAG, and runs multi-agent deliberation before surfacing recommendations for human approval.

[![Live Demo](https://img.shields.io/badge/Live-SupplyChain%20Sentinel-FF4B4B?style=flat&logo=streamlit)](https://supplychain-m6ormyh8hus3tvuep4b5st.streamlit.app/)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-00E599?style=flat&logo=postgresql)](https://neon.tech)
[![LLM](https://img.shields.io/badge/LLM-Groq%20API-f55036?style=flat)](https://groq.com)
[![Tests](https://img.shields.io/badge/Tests-116%2F116%20passing-22c55e?style=flat&logo=pytest)](./tests)
[![Python](https://img.shields.io/badge/Python-3.13%2B-3b82f6?style=flat&logo=python)](https://python.org)
[![Branch](https://img.shields.io/badge/Branch-Bushra-8b5cf6?style=flat&logo=git)](https://github.com/bushrachohan/SupplyChain/tree/Bushra)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat)](./LICENSE)

---

## The Problem

When modern enterprise supply chains face disruptions, conventional software fails:

- **Siloed Risk Awareness**: Inventory planners and freight dispatchers work in isolation — a delayed inbound shipment is rarely cross-analyzed with warehouse stockout probability in real time.
- **Black-Box Alerts**: Legacy ERP systems flag alerts with zero attribution — operators can't tell if an order is late due to traffic, rain, carrier capacity, or routing.
- **Hallucinatory AI Assistants**: Generic LLM chatbots invent operational numbers and suggest actions that break corporate compliance rules.
- **Unverified Autonomous Execution**: Automated systems risk costly failures when executing without critic consensus and human governance.

**SupplyChain Sentinel AI solves all four.**

---

## Live Product

🌐 **[Launch Live Demo on Streamlit Cloud](https://supplychain-m6ormyh8hus3tvuep4b5st.streamlit.app/)**  
*(Connected live to Neon PostgreSQL serverless database and Groq LLM inference).*

---

## Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/54d7b715-72e6-4c83-a794-ab4f4c31ee47"
       alt="SupplyChain Sentinel AI Architecture"
       width="720">
</p>

```
┌─────────────────────────────────────────────────────────────────┐
│               DATA INGESTION & LIFECYCLE LAYER                  │
│   Active Dataset Manager ◄── CSV / Excel / Neon DB / Kaggle     │
│   (Schema Validation ──► Alias Auto-Mapping ──► Live Profiler)  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Normalized DataFrames
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICS & ML ENGINE                        │
│   LightGBM Demand Forecast ──► SHAP Delivery Risk Classifier    │
│   Inventory Safety Buffer  ──► OR-Tools VRP Logistics Optimizer │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Predictions & Metrics
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  POLICY RAG & UNIFIED STATE                     │
│   ChromaDB Vector Store (all-MiniLM-L6-v2) ◄── policies/*.md    │
│   Cross-Risk Compounding ──► Enterprise Severity Calculation    │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Grounded Context
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                MULTI-AGENT DELIBERATION SWARM                   │
│   Orchestrator (Groq) ◄──► Policy Critic ◄──► Business Critic   │
│   (Consensus Guardrails ──► Deterministic Feature Attribution)  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Immutable Trace Record
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               PERSISTENCE & HUMAN-IN-THE-LOOP                   │
│   Neon PostgreSQL (15 Tables) ──► Streamlit Command Center UI   │
│   One-Click Human Approval / Rejection ──► Status Ledger        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 📈 Dynamic Demand Forecasting & Inventory Risk
LightGBM quantile regression models future SKU demand by warehouse. The inventory engine cross-references lead times and current stock levels to compute stockout risks, safety-stock deficits, and holding penalties.

### 🚚 Delivery Delay Classification with SHAP TreeExplainer
Predicts delivery failure probabilities across 300+ shipments based on distance, traffic delay, carrier performance, and weather conditions. TreeExplainer provides local SHAP attribution scores (`+5.24 SHAP traffic delay`, `-0.57 carrier efficiency`) so operators know precisely *why* risk is elevated.

### 🌐 Cross-Risk Compounding & Unified Intelligence
Combines warehouse inventory deficits and transit carrier delays into a single enterprise state. Automatically identifies compounding bottlenecks (e.g., SKU stockout compounded by delayed inbound delivery `DEL_037`) and calculates multi-dimensional severity scores (CRITICAL / HIGH / MEDIUM / LOW).

### 📚 Policy RAG Knowledge Retrieval
ChromaDB vector database indexed with corporate logistics policies (`policies/*.md`) using `all-MiniLM-L6-v2` embeddings. Informs the agent of expediting cost limits, carrier SLAs, and penalty thresholds. Automatically rebuilds missing indices on cloud cold starts.

### 🤖 Multi-Agent Deliberation & Dual-Critic Verification
- **Orchestrator Agent (Groq)**: Analyzes the operational situation and formulates proposed resolutions using deterministic tool calls.
- **Policy Critic**: Validates the recommendation against strict regulatory boundaries and budget caps.
- **Business Critic**: Evaluates cost trade-offs, holding costs, and implementation feasibility.
- **Consensus Guardrail**: Requires unanimous approval before presenting actionable recommendations.

### 📦 Universal Data Ingestion & Kaggle Auto-Aliasing
Supports CSV, Excel (.xlsx), and PostgreSQL/SQLite sources. Automatically detects and aliases Kaggle Supply Chain dataset headers (`order_date`, `shipping_status`, `inventory_quantity`), presents an interactive schema mapper, and generates a live Dataset Understanding Profile card.

### 🛡️ Immutable Audit Trails & Human-in-the-Loop Governance
Every deliberation produces a complete JSON decision trace stored in Neon PostgreSQL. Operational actions require explicit human sign-off with permanent approval ledgers.

---

## Tech Stack

| Layer | Technology | Purpose & Rationale |
|---|---|---|
| **Frontend & UI** | Streamlit 1.63 | Rapid enterprise dashboard with interactive mapping and live analytics |
| **LLM & Reasoning** | Groq (`openai/gpt-oss-120b`) | Sub-second inference for multi-turn agent tool deliberation |
| **ML & Explainability** | LightGBM + scikit-learn + SHAP | Fast gradient-boosted trees + exact TreeExplainer feature attribution |
| **Route Optimisation** | Google OR-Tools | Industrial-grade Capacitated Vehicle Routing Problem (CVRP) solver |
| **Vector Database & RAG** | ChromaDB + sentence-transformers | In-memory semantic policy search using `all-MiniLM-L6-v2` |
| **Relational Database** | Neon PostgreSQL (15 tables) | Serverless PostgreSQL with connection pooling for immutable traces |
| **Data Ingestion** | Pandas + OpenPyXL + SQLAlchemy | Multi-source ingestion (CSV, Excel, DB) with schema validation |
| **Packaging & Dev Tools**| `uv` + `pytest` | Deterministic dependency management and automated test runner |

---

## Why Sentinel AI vs Alternatives

| Capability | Traditional ERP (SAP/Oracle) | Generic LLM Chatbots | Standalone ML Scripts | SupplyChain Sentinel AI |
|---|:---:|:---:|:---:|:---:|
| **Grounded LLM Reasoning (Zero Hallucinations)** | ❌ | ⚠️ High Risk | ❌ | ✅ **100% Tool-Grounded** |
| **Multi-Agent Dual-Critic Verification** | ❌ | ❌ | ❌ | ✅ **Policy + Business Critics** |
| **SHAP Feature-Level Attribution** | ❌ | ❌ | ✅ | ✅ **Interactive SHAP Visuals** |
| **Dynamic Kaggle/CSV Column Auto-Mapping** | ❌ Complex ETL | ❌ | ❌ | ✅ **Live Alias Profiler** |
| **Cross-Risk Compounding Assessment** | ❌ Siloed | ⚠️ Unreliable | ❌ | ✅ **Unified State Engine** |
| **Capacitated Vehicle Routing (CVRP)** | ⚠️ Expensive Add-on | ❌ | ⚠️ Standalone | ✅ **Built-in Google OR-Tools** |
| **Policy RAG Vector Retrieval** | ❌ | ⚠️ Ad-hoc | ❌ | ✅ **ChromaDB + MiniLM** |
| **Immutable Decision Audit Trails** | ⚠️ Complex Logs | ❌ | ❌ | ✅ **Neon Postgres Traces** |
| **Human-in-the-Loop Approval Gate** | ⚠️ Manual | ❌ | ❌ | ✅ **One-Click Ledger UI** |

---

## Database Schema (Core Tables)

```sql
-- Comprehensive agent decision trace audit log
CREATE TABLE decision_traces (
    trace_id             VARCHAR(64) PRIMARY KEY,
    timestamp            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    situation_assessment TEXT,
    recommendations      JSONB,
    critic_evaluations   JSONB,
    policies_retrieved   JSONB,
    status               VARCHAR(30) -- PENDING_APPROVAL | APPROVED | REJECTED
);

-- Human-in-the-loop executive approvals ledger
CREATE TABLE approvals (
    approval_id VARCHAR(64) PRIMARY KEY,
    trace_id    VARCHAR(64) REFERENCES decision_traces(trace_id),
    decision    VARCHAR(20), -- APPROVED | REJECTED
    notes       TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real-time delivery risk scores and SHAP explanations
CREATE TABLE delivery_risk_predictions (
    delivery_id          VARCHAR(64) PRIMARY KEY,
    risk_score           FLOAT,
    risk_category        VARCHAR(20), -- LOW | MEDIUM | HIGH
    top_shap_factors     JSONB,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Quick Start (Local)

### Prerequisites
- Python 3.13+ (or 3.12)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/bushrachohan/SupplyChain.git
cd SupplyChain

# 2. Install all dependencies (including dev and test suites)
uv sync

# 3. Create your environment configuration
cp .env.example .env
# Edit .env with your real GROQ_API_KEY and NEON_DATABASE_URL

# 4. Launch the Streamlit application
uv run streamlit run app.py
```

### Run Tests

```bash
uv run pytest
# Expected: 116 passed in ~60s (100% passing)
```

### Run FastAPI (Dev / API Mode)

```bash
uv run uvicorn api.main:app --reload
# Interactive API documentation: http://localhost:8000/docs
```

---

## Secrets Required

| Key | Where to get it | Purpose |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Powers multi-agent deliberation and reasoning |
| `NEON_DATABASE_URL` | [neon.tech](https://neon.tech) | Connects to serverless PostgreSQL database (15 tables) |

For local development, store these in `.env` (automatically ignored by git).

---

## Deployment — Streamlit Cloud

1. **Push your code to GitHub** on the **`Bushra`** branch.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repository: `bushrachohan/SupplyChain`.
4. Set **Branch** to: `Bushra`.
5. Set **Main file path** to: `app.py`.
6. Set **Python version** to: `3.13` (or `3.12`).
7. Click **Advanced settings → Secrets** and paste using TOML double-quote syntax:

```toml
GROQ_API_KEY = "gsk_..."
NEON_DATABASE_URL = "postgresql://neondb_owner:password@ep-host.aws.neon.tech/neondb?sslmode=require"
```

8. Click **Deploy!**

### ChromaDB on Cloud
The `chroma_db/` folder is git-ignored. On cold starts, `core/rag.py` automatically detects missing indices and re-indexes all documents in `policies/*.md`.

### Dependency Export Rule
Streamlit Community Cloud installs dependencies via `pip install -r requirements.txt`. To regenerate the requirements file from `uv.lock`, **always include `--no-emit-project`** so editable root packages (`-e .`) are excluded:
```bash
uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt
```

> [!NOTE]
> Do not add `packages.txt` with `apt-get` packages; pre-compiled manylinux wheels already bundle required C++ runtimes, avoiding Debian archive expiration errors during cloud builds.

---

## Roadmap

- [x] LightGBM demand forecasting with quantile intervals
- [x] Delivery delay binary classifier with TreeExplainer SHAP attribution
- [x] Capacitated Vehicle Routing Problem (CVRP) via Google OR-Tools
- [x] ChromaDB RAG with corporate policy documents (`policies/*.md`)
- [x] Multi-agent deliberation with Policy and Business Critics
- [x] Immutable decision traces stored in Neon PostgreSQL (15 tables)
- [x] Human-in-the-loop approval & rejection ledger UI
- [x] Multi-source ingestion (CSV, Excel `.xlsx`, Database)
- [x] Kaggle Supply Chain schema auto-aliasing & live profiler
- [x] Cross-risk compounding engine (`core/unified_intelligence.py`)
- [x] 116 unit and integration tests (100% passing)
- [ ] Enterprise ERP (SAP / Oracle WMS) live REST/GraphQL connector
- [ ] Multi-depot, time-windowed fleet routing (VRPTW)
- [ ] Real-time weather and traffic API webhooks

---

## Project Structure

```
SupplyChain/
├── app.py                     # Streamlit production application entry point
├── api/main.py                # FastAPI endpoints (local dev / testing)
├── agent/
│   ├── orchestrator.py        # Primary decision agent (Groq tool-calling)
│   ├── tools.py               # Tool wrappers + Groq function schemas
│   ├── critics/
│   │   ├── policy_critic.py   # Policy compliance & safety verification
│   │   └── business_critic.py # Cost-benefit & feasibility verification
│   ├── consensus.py           # Multi-agent consensus protocol
│   └── decision_trace.py      # Trace builder & DB persistence
├── core/
│   ├── forecasting.py         # LightGBM demand forecast engine
│   ├── inventory_risk.py      # Rule-based stockout & safety stock analysis
│   ├── delivery_risk.py       # Delay classifier with SHAP attribution
│   ├── logistics_optimizer.py # Google OR-Tools Capacitated VRP solver
│   ├── rag.py                 # ChromaDB vector store over business policies
│   ├── simulation.py          # What-if scenario simulation engine
│   └── unified_intelligence.py# Cross-risk compounding & bottleneck detection
├── ml/
│   ├── evaluation.py          # Time-based train/test splits & baselines
│   └── explainability.py      # SHAP tree explainer feature attribution
├── llm/
│   └── explainer.py           # Grounded Groq narrative synthesis
├── db/
│   ├── models.py              # SQLAlchemy models (15 relational tables)
│   └── connection.py          # Neon Postgres engine & connection pool
├── data_ingestion/
│   ├── base.py                # Abstract DataSource interface
│   ├── active_dataset.py      # Dynamic dataset manager & cache invalidation
│   ├── validation.py          # Schema validator, Kaggle auto-mapping, profiler
│   ├── csv_source.py          # CSV source (300 shipments, Kaggle compatibility)
│   ├── excel_source.py        # Excel (.xlsx) data ingestion
│   ├── db_source.py           # Neon DB & SQLite relational source
│   └── api_source.py          # REST API ingestion stub
├── policies/                  # Corporate policy markdown files for RAG
├── data/                      # Standard synthetic supply chain datasets (300 deliveries)
├── data_pipeline/             # Seed data generator & Neon DB loader
├── tests/                     # 116 unit & integration tests (100% passing)
├── .streamlit/config.toml     # Theme styling & 200MB file upload limits
├── pyproject.toml             # uv package and dependency configuration
├── requirements.txt           # pip-compatible manifest for Streamlit Cloud
└── .env.example               # Environment variable secrets template
```

---

## Team

**Bushra** (Team Leader) · **Maryam** · **Shreeya** · **Samiya**

See [`progress.md`](progress.md) for the complete task board, sprint milestones, and session log.

---

## Key Design Rules

1. **LLM Grounding Constraint**: The LLM only narrates and reasons over verified numbers. Every figure traces back to a deterministic `core/*` tool calculation — never hallucinated.
2. **Human-in-the-Loop**: High-impact supply chain interventions require executive sign-off before downstream execution.
3. **True Agentic Deliberation**: The orchestrator dynamically chooses tools based on situational context rather than a rigid linear pipeline.
4. **Transparent Explainability**: Operational risk is always accompanied by exact SHAP factor contributions (traffic, distance, weather, carrier).
5. **Data Integrity**: All synthetic sample datasets (`data/*.csv`) are labeled for testing and never misrepresented as proprietary production records.

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
