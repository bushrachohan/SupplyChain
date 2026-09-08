# PROGRESS.md — SupplyChain Sentinel AI
> Living document. Update only after verified, merged work.
> GitHub `main` is the authoritative source of truth — not any local AI project copy.

---

## Project Overview

**Name:** SupplyChain Sentinel AI — AI-Powered Supply Chain Risk & Decision Intelligence Platform
**Repo:** https://github.com/bushrachohan/SupplyChain
**Team:** Bushra (Team Leader) · Maryam · Shreeya · Samiya
**Stack:** Python · FastAPI · Streamlit · LightGBM · OR-Tools · ChromaDB · Groq · Neon PostgreSQL · uv

**What it does:**
An end-to-end AI decision intelligence platform for supply chains. It forecasts demand, detects inventory and delivery risk, optimizes routes, retrieves business policies via RAG, and runs a genuine multi-agent deliberation (primary agent + policy critic + business critic + consensus layer) before surfacing a recommendation to a human for approval.

**Core pipeline:**
```
Data → Prediction → Risk Detection → Scenario Analysis
→ AI Decision Agent → Multi-Agent Critique → Consensus
→ Human Approval → Simulation → Business Impact
```

---

## Current Status

**Last updated:** 2026-09-08
**Currently in progress:** None

### ✅ Completed (merged to main)
| Module | Notes |
|---|---|
| Phase 0 — Setup | Repo, `uv`, Neon Postgres, Groq key, `.gitignore`, folder structure, GitHub |
| `ml/evaluation.py` | Time-based split, leakage checks, metrics, naive/majority baselines, 13 tests |
| `data_ingestion/` — all 4 sources | `base.py`, `csv_source.py`, `excel_source.py`, `db_source.py`, `api_source.py` |
| Synthetic seed data + CSVs | Dev/test only — never treated as real company data |
| `policies/*.md` | Real business/procurement/inventory/logistics policy documents for RAG |
| `core/forecasting.py` | LightGBM, time-based split, baseline comparison, leakage checks, feature importance, 12 tests |
| `core/inventory_risk.py` | Rule-based stockout/overstock, contributing-factor explainability, 9 tests |
| `core/rag.py` | ChromaDB + sentence-transformers, section-aware chunking, safety-stock retrieval verified, 7 tests |
| `llm/explainer.py` | Groq narration-only wrapper (`explain_recommendation`, `summarize_text`), injectable test client, migrated to `openai/gpt-oss-120b`, 9 tests |
| `db/models.py` + `db/connection.py` | All 15 tables, SQLAlchemy models, Neon connection, `create_tables.py`, 2 tests passing |
| `data_pipeline/` | `generate_seed_data.py`, `load_seed_data.py` for Neon DB population |
| `core/delivery_risk.py` | Binary classifier, time-based split, baseline comparison, SHAP |
| `core/logistics_optimizer.py` | OR-Tools Capacitated VRP |
| `ml/explainability.py` | SHAP/feature importance helpers for delivery risk |
| `agent/tools.py` | Tool wrappers with Groq function-call schemas |
| `agent/orchestrator.py` | Genuine tool-calling agent loop |
| `agent/critics/policy_critic.py` | Policy compliance + safety check |
| `agent/critics/business_critic.py` | Cost + feasibility check |
| `agent/consensus.py` | Compares proposal + critics, records disagreements |
| `agent/decision_trace.py` | Builds and persists full trace to DB |
| `api/main.py` | FastAPI endpoints for orchestrator, traces, recommendations, approval |
| `app.py` | Streamlit dashboard for command center, create decision, approval queue |
| `core/simulation.py` | What-if simulation engine (inventory, delivery, logistics), 3 tests |
| Phase 4 Simulation UI in `app.py` | Interactive before/after stress test controls & action delta comparison |
| `requirements.txt` | pip-compatible dependency file for Streamlit Cloud (auto-generated from `uv.lock`) |
| `.streamlit/config.toml` | Production dark theme + server settings for Streamlit Cloud |
| `.env.example` | Secret key template for new contributors |
| `README.md` | Full setup, architecture, deployment, and project structure documentation |
| `pyproject.toml` | Added `[tool.pytest.ini_options]` section |
### 🔄 In Progress
None.

### ⛔ Blocked
None.

### 🟢 Next Available

No pending build/deployment tasks. The MVP is fully built, deployed, and verified.

---

## Tech Stack (Locked — $0 total cost)

| Layer | Choice |
|---|---|
| Env / packages | `uv` + `pyproject.toml` + `uv.lock` |
| Backend (local dev) | FastAPI + Uvicorn |
| ML | scikit-learn, LightGBM, SHAP |
| Optimization | OR-Tools (Google) |
| RAG | ChromaDB + sentence-transformers (local, no server) |
| Agent / LLM | Groq API — `openai/gpt-oss-120b` — tool/function calling |
| Database | Neon PostgreSQL (serverless, free tier) |
| Testing | pytest |
| Frontend / Deploy | Streamlit Community Cloud |
| IDE | VS Code |
| Version control | GitHub |

**Model note:** `llama-3.3-70b-versatile` is deprecated. Always use `openai/gpt-oss-120b`.

---

## Architecture

### Full Pipeline
```
Data Sources (CSV / Excel / Neon DB / API)
    ↓
Data Ingestion Layer (DataSource interface)
    ↓
Core ML Modules
  ├── core/forecasting.py         (LightGBM demand forecast)
  ├── core/inventory_risk.py      (rule-based stockout/overstock)
  ├── core/delivery_risk.py       (binary classifier)
  └── core/logistics_optimizer.py (OR-Tools VRP)
    ↓
RAG Layer (core/rag.py)
  └── retrieves relevant policy constraints for the situation
    ↓
AI Decision Agent (agent/orchestrator.py)
  └── genuine tool-calling agent — Groq decides which tools to call
    ↓
Multi-Agent Critique
  ├── agent/critics/policy_critic.py   (policy compliance + safety)
  └── agent/critics/business_critic.py (cost + feasibility)
    ↓
Consensus Layer (agent/consensus.py)
  └── compares proposal + critiques → final recommendation status
    ↓
Decision Trace (agent/decision_trace.py → decision_traces table)
    ↓
Human Approval Gate (Streamlit UI — Approve / Reject)
    ↓
Business Impact Simulation (before/after KPI delta)
```

### Deployment Architecture
Streamlit Community Cloud runs one process only — no separate FastAPI server. Therefore:
- `core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/` contain all logic — zero web-framework imports.
- `api/main.py` (FastAPI) imports from these for local dev and testing only.
- `app.py` (Streamlit) also imports from them directly — this is what runs in production.

One codebase, two front doors, nothing duplicated.

---

## Multi-Agent Design

A single agent must not be the only decision-maker. The architecture uses a primary Decision Agent plus two critic agents and a consensus layer.

### Agent Roles

**Primary Decision Agent (`agent/orchestrator.py`)**
- Receives the situation (SKU IDs, delivery IDs, context).
- Calls tools via Groq tool/function calling — not a hardcoded sequence.
- Assembles a structured options table from tool results and retrieved policies.
- Proposes a recommended action.

**Policy / Safety Critic (`agent/critics/policy_critic.py`)**
- Receives the proposed action + retrieved policy content.
- Checks: does the proposal comply with business policy constraints? Does it violate any safety or procurement rule?
- Returns a structured verdict with specific policy references.

**Business Impact Critic (`agent/critics/business_critic.py`)**
- Receives the proposed action + predicted cost/impact numbers.
- Checks: is this operationally feasible? Is the cost justifiable? Are there better alternatives on business impact?
- Returns a structured verdict with specific trade-off analysis.

**Consensus Layer (`agent/consensus.py`)**
- Receives: primary proposal + policy critic verdict + business critic verdict.
- Compares them. If critics agree → confirms recommendation. If critics raise valid objections → escalates or revises.
- Records any disagreements in the decision trace.
- Does **not** simply repeat the primary agent's answer.

**Human Approval Gate**
- The consensus result is written to `decision_traces` with `human_approval.status = "pending"`.
- Streamlit surfaces it with **Approve / Reject** buttons.
- Nothing is auto-executed. Ever.

### The LLM Grounding Constraint
The LLM (in any agent role) **only narrates, reasons about tool selection, and critiques structure** — it never computes or invents numbers. All numerical outputs (forecasts, risk scores, route costs, impact deltas) come from `core/*` code. If the LLM ever produces a number not present in its input, something is wrong.

### Agent File Structure
```
agent/
├── tools.py              # tool wrappers around core/* with Groq function-call schemas
├── orchestrator.py       # primary decision agent — Groq tool-calling loop
├── decision_trace.py     # builds + persists the full trace to Neon DB
├── critics/
│   ├── policy_critic.py  # policy compliance + safety check
│   └── business_critic.py# cost + feasibility check
└── consensus.py          # compares proposal + critiques → final status
```

### Tools Exposed to the Agent
| Tool | Wraps | When called |
|---|---|---|
| `get_demand_forecast(sku_id)` | `core/forecasting.py` | Inventory situation |
| `get_inventory_risk(sku_id)` | `core/inventory_risk.py` | Inventory situation |
| `get_delivery_risk(delivery_id)` | `core/delivery_risk.py` | Delivery situation |
| `optimize_routes(delivery_ids, vehicle_constraints)` | `core/logistics_optimizer.py` | Route/logistics situation |
| `retrieve_policies(query)` | `core/rag.py` | Always — policies constrain options |

The agent skips tools irrelevant to the situation. A pure inventory alert should not trigger `optimize_routes`. This is what makes it a real agent — not a pipeline.

---

## RAG Design

- Policy documents live in `policies/*.md` — real written business/procurement/logistics policies, not generic text.
- ChromaDB + sentence-transformers embed documents locally at startup (no external server).
- Section-aware chunking: policies are split at markdown heading boundaries, not arbitrary character windows.
- Retrieved policy content must **constrain** options, not just be cited decoratively. If a policy says "never let Tier-1 SKUs fall below 2 weeks of safety stock," the options table must reflect that constraint.
- Retrieval is verified: a safety-stock query must rank the safety-stock policy section above unrelated sections.

---

## Phase Progress

### Phase 1 — Predictive Intelligence
| Task | Status |
|---|---|
| `data_ingestion/base.py` + `csv_source.py` | ✅ DONE |
| `data_ingestion/excel_source.py`, `db_source.py` | ✅ DONE |
| `data_ingestion/api_source.py` | ✅ DONE |
| `db/models.py` + `db/connection.py` | ✅ DONE |
| `data_pipeline/` — load data → Neon | ✅ DONE |
| `core/forecasting.py` | ✅ DONE |
| `core/inventory_risk.py` | ✅ DONE |
| `core/delivery_risk.py` | ✅ DONE |
| `core/logistics_optimizer.py` | ✅ DONE |
| `ml/evaluation.py` | ✅ DONE |
| `ml/explainability.py` | ✅ DONE |
| Tests for all above | ✅ DONE |

### Phase 2 — RAG + Agentic AI
| Task | Status |
|---|---|
| `policies/*.md` — real policy documents | ✅ DONE |
| `core/rag.py` | ✅ DONE |
| `llm/explainer.py` | ✅ DONE |
| `agent/tools.py` | ✅ DONE |
| `agent/orchestrator.py` | ✅ DONE |
| `agent/critics/policy_critic.py` | ✅ DONE |
| `agent/critics/business_critic.py` | ✅ DONE |
| `agent/consensus.py` | ✅ DONE |
| `agent/decision_trace.py` | ✅ DONE |
| Tests for all above | ✅ DONE |

### Phase 3 — Human-in-the-Loop UI
| Task | Status |
|---|---|
| `api/main.py` — FastAPI endpoints (local dev) | ✅ DONE |
| `app.py` — Streamlit dashboard + Approve/Reject + decision trace view | ✅ DONE |

### Phase 4 — What-If Simulation & Business Demonstration
| Task | Status |
|---|---|
| Scenario parameter controls (demand, stock, lead time, delivery risk, capacity, disruption) | ✅ DONE |
| Before/after prediction comparison | ✅ DONE |
| Recommended action delta (do nothing vs. act) | ✅ DONE |
| Non-technical visual explanation UI | ✅ DONE |

**Purpose of Phase 4:** The final system must be understandable to non-technical judges and business users. The simulation reuses actual ML/risk/optimization/agent outputs — it does not invent independent numbers. Users change business conditions and see the resulting change in stockout risk, delivery risk, inventory level, route cost, and recommended action.

```
BEFORE  →  [change parameter]  →  AFTER
"What problem did AI find?" → "What options were considered?" → "What is recommended?" → "What happens if we do nothing?"
```

### Phase 5 — Deploy
| Task | Status |
|---|---|
| `pyproject.toml` / `uv.lock` finalized, clean `uv sync` in fresh clone | ✅ DONE |
| `requirements.txt` generated and committed (for Streamlit Cloud pip install) | ✅ DONE |
| Full `uv run pytest` suite passing (90/90) | ✅ DONE |
| `.streamlit/config.toml` committed (dark theme + server config) | ✅ DONE |
| `.env.example` committed (secret key template) | ✅ DONE |
| `README.md` updated with full setup, deploy, and architecture docs | ✅ DONE |
| Repo pushed to GitHub (`main`) | ✅ DONE |
| Neon Postgres production DB confirmed reachable | ✅ DONE — verified from deployed app |
| Streamlit Cloud app created, connected to repo, `app.py` as entry point | ✅ DONE — deployed |
| `GROQ_API_KEY` + `NEON_DATABASE_URL` added to Streamlit Secrets | ✅ DONE — verified on deployment |
| ChromaDB cold-start rebuild verified | auto-rebuilds via `core/rag.py` — no action needed |
| End-to-end demo scenario runs on live deploy including human approval | ✅ DONE — deployed and tested end-to-end |

---

## Build Checklist

Every phase requires confirming terminal output and passing tests before committing. Do not mark a box checked unless the implementation is verified by your actual terminal output and tests pass.

### Phase 0 — Setup
- [x] VS Code + extensions installed
- [x] `uv init` run, `pyproject.toml` created
- [x] Initial dependencies added via `uv add ...`, `uv.lock` generated
- [x] Groq API key obtained, Neon Postgres database created, both stored in `.env`
- [x] Folder structure created (`core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/`, `db/`, `policies/`, `api/`, `tests/`, `data/`)
- [x] Git repo initialized, `.gitignore` in place, first commit pushed to GitHub
- [x] Claude Project created, this file uploaded, custom instructions pasted
- [x] **Confirmed:** `git log` shows commits; `git remote -v` shows GitHub origin; `uv run python -c "print('ok')"` runs cleanly

### Phase 1 — Data Layer & Core ML Logic
- [x] `data_ingestion/base.py` — abstract `DataSource` interface defined
- [x] `data_ingestion/csv_source.py` — synthetic dataset loaded via this interface (dev/test only)
- [x] `data_ingestion/excel_source.py`, `db_source.py` — working sample implementations
- [x] `data_ingestion/api_source.py` — extensible interface/example only (not a production connector)
- [x] `db/models.py`, `db/connection.py` — Neon Postgres schema created and connected
- [x] `data_pipeline/` scripts: source data → Neon Postgres
- [x] `core/forecasting.py` — LightGBM, time-based split, baseline comparison, 12 tests passing
- [x] `core/inventory_risk.py` — stockout/overstock logic, 9 tests passing
- [x] `core/delivery_risk.py` — binary classifier, time-based split, baseline comparison, SHAP
- [x] `core/logistics_optimizer.py` — OR-Tools Capacitated VRP, tested standalone
- [x] `ml/evaluation.py` — split/leakage-check/baseline-comparison utilities, 13 tests passing
- [x] `ml/explainability.py` — SHAP/feature importance helpers for delivery risk
- [x] `tests/test_evaluation.py`, `tests/test_forecasting.py`, `tests/test_inventory_risk.py`, `tests/test_data_ingestion.py` — passing
- [x] `tests/test_delivery_risk.py`, `tests/test_logistics_optimizer.py` — passing
- [x] **Confirmed:** each module runs independently, terminal output shows expected results, `uv run pytest` is green

### Phase 2 — RAG, Multi-Agent, and Decision Trace
- [x] Real business/procurement/inventory/logistics policy documents written and placed in `policies/`
- [x] `core/rag.py` — ChromaDB + sentence-transformers, section-aware chunking, safety-stock retrieval verified, 7 tests passing
- [x] `llm/explainer.py` — Groq narration-only wrapper, injectable test client, 9 tests passing
- [x] `agent/tools.py` — tool wrappers around `core/*` with Groq function-call schemas
- [x] `agent/orchestrator.py` — genuine Groq tool-calling agent loop; tested for at least two scenarios that call *different* tool subsets (pure inventory alert must not trigger `optimize_routes`)
- [x] `agent/critics/policy_critic.py` — receives proposed action + retrieved policies, returns structured verdict with specific policy references
- [x] `agent/critics/business_critic.py` — receives proposed action + cost/impact numbers, returns structured trade-off verdict
- [x] `agent/consensus.py` — compares primary proposal + both critic verdicts, records disagreements, does not simply echo the primary agent
- [x] `agent/decision_trace.py` — builds and persists full trace to `decision_traces` table; `human_approval.status` starts as `"pending"`
- [x] `tests/test_rag.py` — safety-stock query retrieves safety-stock policy section above unrelated sections
- [x] `tests/test_agent_tools.py` — each tool returns correct schema for a given input
- [x] `tests/test_decision_trace.py` — completed run produces trace with all required fields; approval status starts `"pending"`
- [x] **Confirmed:** orchestrator run end-to-end from terminal produces a full trace (inputs → predictions → policies → tools used → primary proposal → critic verdicts → consensus result → recommendation) for at least two distinct test scenarios

### Phase 3 — Human-in-the-Loop UI
- [x] `api/main.py` — FastAPI endpoints wired to `agent/`/`core/`, tested locally via `uv run uvicorn api.main:app --reload` and the `/docs` page
- [x] `app.py` — Streamlit dashboard: pending recommendations with full decision trace visible, **Approve / Reject** buttons, business-impact simulation shown after approval
- [x] Rejecting a recommendation does not mark it executed; approving does
- [x] Decision trace view shows: inputs → predictions → policies retrieved → tools called → primary proposal → critic verdicts → consensus result
- [x] **Confirmed:** both the FastAPI `/docs` page and the Streamlit dashboard show correct results for the same test case

### Phase 4 — What-If Simulation & Business Demonstration
- [x] Scenario parameter controls in Streamlit UI — adjustable: demand level, current inventory, supplier lead time, delivery risk, vehicle capacity, disruption scenario
- [x] Before/after prediction comparison — same ML/risk/optimization outputs, different input conditions
- [x] Recommended action delta — "do nothing" outcome vs. recommended action outcome, side by side
- [x] Non-technical visual explanation — clearly shows: "What problem did AI find?" → "What options were considered?" → "What is recommended?" → "What happens if we do nothing?"
- [x] Simulation reuses actual `core/*` model outputs — does not invent independent numbers
- [x] **Confirmed:** a non-technical user can follow the BEFORE → simulate → AFTER flow without explanation

### Phase 5 — Deploy
- [x] `pyproject.toml` / `uv.lock` finalized and confirmed to install cleanly via `uv sync` in a fresh clone
- [x] `requirements.txt` generated and committed for Streamlit Cloud
- [x] `.streamlit/config.toml` committed (dark theme + production server settings)
- [x] `.env.example` committed with GROQ and Neon key placeholders
- [x] `README.md` updated with full deploy instructions
- [x] Repo pushed to GitHub, fully up to date
- [x] Full `uv run pytest` suite passing (90/90) before deploy commit
- [x] Neon Postgres production database confirmed reachable from Streamlit Cloud
- [x] Streamlit Community Cloud app created, connected to GitHub repo, entry point set to `app.py`
- [x] `GROQ_API_KEY` and `NEON_DATABASE_URL` added to Streamlit Cloud → App settings → Secrets
- [x] ChromaDB index rebuild on cold start confirmed working (`build_policy_index` auto-rebuilds if `chroma_db/` missing)
- [x] **Confirmed:** deployed app loads, runs a full demo scenario end-to-end including multi-agent critique, human approval, and what-if simulation — matches local behavior

## Final Verification Status

**Status: ✅ COMPLETE**

All planned phases (Phase 1 through Phase 5) are complete. The application has been deployed to Streamlit Community Cloud, connected to the production Neon PostgreSQL database and Groq API, and tested end-to-end on the live deployment.

Verified live flow:
`Data → Prediction → Risk Detection → Scenario Analysis → AI Decision Agent → Multi-Agent Critique → Consensus → Human Approval → Simulation → Business Impact`

No implementation, deployment, or testing tasks are currently pending.

---

## What's Fully Built ✅

- **Data ingestion layer** — `DataSource` abstract interface + CSV, Excel, Neon DB, and API (stub) implementations. Plug a new real company data source in by writing one new implementation.
- **ML evaluation utilities** — time-based split, leakage detection, naive/majority-class baselines, MAPE/RMSE/AUC/precision-recall metrics.
- **Demand forecasting** — LightGBM, SKU-level, 4–12 weeks ahead, time-based train/val/test, baseline comparison, feature importance.
- **Inventory risk** — rule-based stockout/overstock detection, contributing-factor explainability output.
- **RAG** — ChromaDB + sentence-transformers over real policy documents, section-aware chunking, retrieval verified.
- **LLM explainer** — Groq narration-only wrapper, injectable test client, grounding constraint enforced.
- **Synthetic seed data** — dev/test only, clearly identified as synthetic in all outputs.
- **Policy documents** — real written business/procurement/logistics/inventory policies in `policies/*.md`.
- **Database layer** — all 15 Neon Postgres tables defined via SQLAlchemy, connection pooling, `create_tables.py`, 2 tests passing.
- **What-If Simulation layer** — multi-scenario parameter engine (Inventory, Delivery Risk, Logistics) with Before vs. After metrics comparison.
- **Cloud Deployment** — Live production Streamlit Community Cloud app connected to Neon Postgres and Groq API.

---

## What Needs to Be Built (Priority Order)

*None — All phases (Phase 1 through Phase 5) are fully completed and verified!* 🎉

---

## File Structure

```
supplychain-sentinel-ai/
├── core/
│   ├── forecasting.py             ✅ LightGBM demand forecast
│   ├── inventory_risk.py          ✅ stockout/overstock detection
│   ├── delivery_risk.py           ✅
│   ├── logistics_optimizer.py     ✅
│   └── rag.py                     ✅ ChromaDB + sentence-transformers
├── ml/
│   ├── evaluation.py              ✅ split / leakage / baselines / metrics
│   └── explainability.py          ✅
├── agent/
│   ├── tools.py                   ✅
│   ├── orchestrator.py            ✅
│   ├── decision_trace.py          ✅
│   ├── critics/
│   │   ├── policy_critic.py       ✅
│   │   └── business_critic.py     ✅
│   └── consensus.py               ✅
├── llm/
│   └── explainer.py               ✅ Groq narration-only wrapper
├── data_ingestion/
│   ├── base.py                    ✅ abstract DataSource interface
│   ├── csv_source.py              ✅
│   ├── excel_source.py            ✅ working sample
│   ├── db_source.py               ✅ working sample
│   └── api_source.py              ✅ extensible stub (not production)
├── db/
│   ├── models.py                  ✅ 15 tables, SQLAlchemy models
│   └── connection.py              ✅ Neon connection, session 
├── policies/                      ✅ real policy markdown documents
├── api/
│   └── main.py                    ✅
├── app.py                         ✅
├── data_pipeline/                 ✅
├── data/                          ✅ synthetic seed CSVs (dev/test only)
├── tests/
│   ├── test_forecasting.py        ✅ 12 passing
│   ├── test_inventory_risk.py     ✅ 9 passing
│   ├── test_evaluation.py         ✅ 13 passing
│   ├── test_data_ingestion.py     ✅ passing
│   ├── test_rag.py                ✅ 7 passing
│   ├── test_delivery_risk.py      ✅ passing
│   ├── test_logistics_optimizer.py ✅ passing
│   ├── test_agent_tools.py        ✅ passing
│   └── test_decision_trace.py     ✅ passing
├── pyproject.toml                 ✅
├── uv.lock                        ✅
├── .env                           ✅ local secrets (never committed)
├── .gitignore                     ✅
└── README.md
```

---

## Database Schema (Neon PostgreSQL)

```sql
skus                   (sku_id, name, category, tier, lead_time_days, ...)
historical_demand      (id, sku_id, date, quantity)
inventory_snapshots    (id, sku_id, snapshot_date, quantity_on_hand, ...)
forecast_results       (id, sku_id, forecast_date, predicted_quantity, model, ...)
inventory_risk         (id, sku_id, risk_flag, days_remaining, contributing_factors, ...)
deliveries             (delivery_id, sku_id, carrier, distance_km, scheduled_date, ...)
delivery_risk_predictions (id, delivery_id, risk_score, risk_label, top_features, ...)
vehicles               (vehicle_id, capacity_kg, ...)
routes                 (route_id, vehicle_id, total_distance_km, total_cost, ...)
route_stops            (id, route_id, stop_order, delivery_id, ...)
policies               (id, doc_name, section, content, embedding_ref)
recommendations        (id, trace_id, recommended_action, status, ...)
impact_simulations     (id, trace_id, before_kpis, after_kpis, delta, ...)

decision_traces        (
  trace_id, timestamp,
  inputs,               -- situation description, SKU/delivery IDs
  predictions,          -- forecast values, risk scores, route costs from tools
  policies_retrieved,   -- policy snippets used + how they constrained options
  tools_used,           -- ordered list of tool calls with args + results
  options_considered,   -- structured table of candidate actions + trade-offs
  primary_proposal,     -- Decision Agent's proposed action
  policy_critic_output, -- Policy Critic's structured verdict
  business_critic_output,-- Business Critic's structured verdict
  consensus_result,     -- final recommendation + any recorded disagreements
  human_approval,       -- {status: pending|approved|rejected, approver, timestamp, notes}
  outcome               -- post-action result / simulated business impact
)

approvals              (id, trace_id, decision, approver_id, timestamp, notes)
```

---

## Key Module Interfaces

### `data_ingestion/base.py`
```python
class DataSource(ABC):
    def load_historical_demand(self) -> pd.DataFrame: ...
    def load_inventory_snapshot(self) -> pd.DataFrame: ...
    def load_deliveries(self) -> pd.DataFrame: ...
    def load_vehicles(self) -> pd.DataFrame: ...
```

### `core/forecasting.py`
```python
def train_forecast_model(df: pd.DataFrame) -> tuple[model, metrics_dict]: ...
def get_demand_forecast(sku_id: str, model, df: pd.DataFrame) -> dict:
    # returns: {sku_id, forecast_horizon_weeks, predicted_quantities: list[float], feature_importance: dict}
```

### `core/inventory_risk.py`
```python
def assess_inventory_risk(sku_id: str, stock_df: pd.DataFrame, forecast: dict) -> dict:
    # returns: {sku_id, risk_flag: "stockout"|"overstock"|"ok", days_remaining: float, contributing_factors: list[str]}
```

### `core/rag.py`
```python
def retrieve_policies(query: str, top_k: int = 3) -> list[dict]:
    # returns: [{source, section, content, relevance_score}]
```

### `agent/tools.py` (Groq function-call schemas + wrappers)
```python
TOOLS = [
    {"name": "get_demand_forecast",    "description": "...", "parameters": {...}},
    {"name": "get_inventory_risk",     "description": "...", "parameters": {...}},
    {"name": "get_delivery_risk",      "description": "...", "parameters": {...}},
    {"name": "optimize_routes",        "description": "...", "parameters": {...}},
    {"name": "retrieve_policies",      "description": "...", "parameters": {...}},
]
```

---

## ML Engineering Rules (Non-Negotiable)

**Time-based split** — never randomly shuffle time-series data. Train on earliest period, validate on next, test on most recent. This mirrors real deployment conditions.

**No data leakage** — no feature may use information unavailable at prediction time. Check: rolling aggregates over future dates, using a delivery's actual outcome to predict its own risk.

**Baseline comparison (mandatory)** — every model is compared against a naive baseline before it's "done":
- Forecasting: naive (last observed value) or seasonal naive
- Delivery risk: majority-class predictor
If the trained model doesn't clearly beat the baseline on the test set, that's a finding to report — not a failure to hide.

**Evaluation metrics** — reported on the test split only. Validation metrics are for tuning, not claims.

**Explainability** — LightGBM feature importance for forecasting; SHAP (or built-in importance) for delivery risk. This output feeds the LLM's narration so explanations are grounded in what the model actually learned.

**Synthetic data** — always identified as synthetic in any output, claim, or demo. Never presented as real company data.

---

## Coding Rules (Follow Every Session)

1. **Read `progress.md` and inspect relevant repository files before coding.** Never assume a file's schema or column names.
2. **One file at a time.** Build and test before the next file.
3. **Never use `&&` in PowerShell** — always separate lines.
4. **Always prefix Python with `uv run`** — no raw `python` calls.
5. **No file is committed without its tests passing.**
6. **Run tests before every commit:** `uv run pytest`
7. **The LLM never computes numbers.** Every figure in a recommendation traces to a `core/*` tool call.
8. **Human approval gate is required** for any recommendation with real business consequence. Never auto-execute.
9. **Never commit `.env`, `.venv/`, or secrets.**
10. **Commit message convention:** `Add:` new files · `Fix:` bugs · `Update:` logic changes.

---

## AI Coding Assistant Rules (Claude / Antigravity)

Before starting any session:
1. Read the latest `progress.md` on `main`.
2. Inspect the actual repository files relevant to the task — never assume contents or schema.
3. Check the live task board for `IN PROGRESS` tasks and avoid them.

Step-by-step workflow every session:
1. Identify the current task and explain what is being built and why, tied to the phase progress table.
2. Make only the required code changes — one file/component at a time.
3. Give the exact terminal command(s) to run.
4. **STOP and WAIT for the developer's actual terminal output.** Do not assume anything works until output is provided.
5. Analyze the actual output. If there is an error, fix it and give the command again — repeat until verified.
6. Only after the developer confirms the implementation works should Git/PR instructions be provided.

Never:
- Assume a file is correct because it was written.
- Mark a task `DONE` before its PR is merged (status is at most `REVIEW` until then).
- Silently change architecture, dependencies, or MVP scope.
- Invent a file's schema, column names, or contents.
- Tell the developer to commit/push/open a PR immediately after writing code.
- Auto-proceed after writing code — always wait for the developer's confirmed output first.

After a task is verified and merged, provide the exact text to paste into `progress.md` — ready to copy-paste. Never just remind the developer to update it.

---

## Gotchas (Bugs Fixed — Never Re-introduce)

| # | Bug | Fix |
|---|---|---|
| 1 | PowerShell doesn't support `&&` | Always write commands on separate lines |
| 2 | `llama-3.3-70b-versatile` deprecated (Aug 16, 2026) | Use `openai/gpt-oss-120b` in all Groq calls |
| 3 | Committing `.env` or `.venv/` | `.gitignore` must be in place before first commit |
| 4 | LLM invents a number in its output | Verify every figure in LLM output traces to a tool result — if not, it's a bug |
| 5 | Agent calls all tools in a fixed order regardless of situation | Test with scenarios that should skip tools; if it doesn't skip, it's a pipeline not an agent |
| 6 | Random train/test split on time-series data | Always split by time — never shuffle |
| 7 | ChromaDB index lost on cold start | Rebuild on startup or persist separately before deploy |
| 8 | Forgetting `uv add` when importing a new package | Always add to `pyproject.toml` via `uv add` — fresh clone/deploy will fail otherwise |
| 9 | Marking task DONE before PR is merged | DONE only after PR is merged and verified by Team Leader |

---

## Project Prioritization (Scope Control)

| Priority | Scope | Status |
|---|---|---|
| **Primary MVP** | Project 17 — Inventory Forecasting & Stockout Prevention | In scope now |
| **Secondary MVP** | Project 18 — Logistics / Delivery Risk / Route Optimization | In scope — built after primary MVP is solid |
| **Phase 2 / Future** | Project 10 — Supplier Risk Monitoring / External Disruption Intelligence | Out of scope for 1-month MVP |

**Rule:** the AI Decision Agent, RAG, multi-agent critique, and human-approval layers are built to serve Project 17 first, then extended to cover Project 18. Project 10 is not touched until both work end-to-end and are deployed. If a session drifts toward Project 10 features, stop and check this table.

---

## Team Workflow

**Team:** Bushra (Team Leader) · Maryam · Shreeya · Samiya
**No permanent technical roles.** Tasks are chosen dynamically based on current progress + available dependencies.
**Coordination:** WhatsApp for task selection · GitHub for implementation history

### How to Start a Session
1. `git pull origin main`
2. Read `progress.md` — Current Status section.
3. Check GitHub for active branches/PRs.
4. Confirm no one else is already working on your intended task (WhatsApp).
5. Create a task branch: `git checkout -b feature/<task-name>`
6. Begin work.

### Branch Names
```
feature/database
feature/delivery-risk
feature/route-optimizer
feature/agent-tools
feature/orchestrator
feature/policy-critic
feature/business-critic
feature/consensus
feature/decision-trace
feature/dashboard
feature/simulation
```

### When a Task is Done
1. Verify locally — run `uv run pytest`, confirm output.
2. Push branch → open Pull Request.
3. Share in WhatsApp: PR link + what changed + files modified + test results + any issues.
4. Team Leader reviews and merges.
5. **After merge only:** Team Leader updates `progress.md` — marks task `DONE`, updates Current Status, marks any newly available tasks as `TODO`, pushes to `main`.
6. All members pull `main` before choosing the next task.

### Definition of Done
A task is DONE only when all of the following are true:
1. Code is implemented.
2. Real (not mocked) test input has been used.
3. Relevant automated tests pass.
4. Errors and invalid inputs are handled.
5. Output is correct and explainable where applicable.
6. Existing functionality still works (no regressions).
7. `progress.md` is updated with verified merged state.
8. PR is merged to `main`.

### High-Conflict Files (Coordinate Before Editing)
- `progress.md`
- `pyproject.toml` / `uv.lock`
- `db/models.py`
- `agent/tools.py` (tool schemas)
- `data_ingestion/base.py`
- `api/main.py` route signatures

### `progress.md` Merge Rule
- Never overwrite newer progress with an older branch copy.
- Never mark work `DONE` before its PR is merged.
- Resolve conflicts by preserving the actual latest merged state.
- Team Leader pushes updated `progress.md` to `main` after every merge.

### Integration Tags
Tag stable milestones: `v0.1-foundation` · `v0.2-ml` · `v0.3-agent` · `v0.4-mvp`

---

## Key Concepts Reference

**Embeddings** — text converted to a vector of numbers capturing meaning. "Safety stock policy" and "minimum inventory buffer" land near each other even with no shared words. Used so RAG finds *relevant* policies, not just keyword matches.

**Cosine similarity** — measures how similar the *direction* of two vectors is. Score near 1 = very similar meaning. The math behind "find the most relevant policy for this situation."

**RAG** — embed policy documents ahead of time, embed the current situation, retrieve the most relevant policy snippets, pass them to the agent to actually use — not just mention.

**Tool-using agent vs. pipeline** — a real agent lets the LLM *decide* which tools to call based on the situation. A hardcoded `forecast() → risk() → optimize()` that always runs in the same order is a pipeline wearing an agent label. The test: does it skip tools when they're not relevant?

**SHAP / feature importance** — explains *why* the model made a prediction. This grounds the LLM's explanation in actual model reasoning, not a plausible-sounding guess.

**Decision trace** — the full structured record of every decision: input → predictions → retrieved policies → tools called → primary proposal → critic verdicts → consensus result → human approval → outcome. Makes the system auditable.

**Human-in-the-loop** — any action with real business consequence (purchase order, reroute, expedite) must be recommended by the agent and approved by a human before execution. Non-negotiable.

**The LLM grounding constraint** — the most important engineering rule: the LLM explains, narrates, critiques, and reasons about tool selection. It never calculates. Every number in the output traces to a tool call.

---

## Learning Log

Fill in after every session — non-negotiable.

```
### Session: [date]
Developer:
Task worked on:
What was built:
What broke (and how fixed, or not yet):
What was actually learned:
Questions for next session:
```

---

## Session Log

| Date | Developer | Task | Outcome |
|------|-----------|------|---------|
| pre-2026-09-02 | Team | Phase 0, data ingestion, evaluation, forecasting, inventory risk, RAG, LLM explainer | All merged to main |
| 2026-09-06 | — | `db/models.py` + `db/connection.py` + `tests/test_db.py` | 62/62 passing, merged to main |
| 2026-09-08 | Team | Phase 4 What-If Simulation (`core/simulation.py`, `app.py`, 90/90 tests passing) | Verified & merged |
| 2026-09-08 | Team | Phase 5 Deployment — Streamlit Community Cloud + Neon PostgreSQL + Groq; live end-to-end testing including multi-agent critique, human approval, and what-if simulation | Deployed, tested, and verified successfully |