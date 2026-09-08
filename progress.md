# PROGRESS.md — SupplyChain Sentinel AI
> Living document. Update only after verified, merged work.
> GitHub `main` is the authoritative source of truth — not any local AI project copy.
> **AI AGENT ENTRY RULE:** Any AI coding agent entering this repository must read this file before modifying code. This file contains both the verified historical state and the active productization execution queue. Never assume prior conversation context exists.

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

**Product Stage:** MVP COMPLETE → PRODUCTIZATION IN PROGRESS

**Currently in progress:** P0 — Active Business Dataset Foundation (`data_ingestion/active_dataset.py`).

**Current execution rule:** The first unchecked task in the Productization Roadmap is the next task for the AI coding agent to work on.

**Important:** The MVP is complete and deployed, but the PRODUCT is not considered complete until the Productization Definition of Done is satisfied.

### 🔄 Current Working State (Local Verification Complete / Push Pending)

The current developer session has completed **P0 — Active Business Dataset Foundation**.

Work implemented and verified locally (100/100 tests passing):
- `data_ingestion/active_dataset.py`:
  - `DatasetMetadata` & `ActiveDatasetContext`
  - Lifecycle states (`uploaded/connected`, `validated`, `active`, `failed`, `replaced`)
  - Cache invalidation subscriptions (`subscribe`, `unsubscribe`, `_notify`)
  - Delegation methods (`load_historical_demand`, `load_inventory_snapshot`, `load_deliveries`)
- `tests/test_active_dataset.py`:
  - 5 comprehensive tests covering lifecycle, invalidation listeners, CSV delegation, Excel/DB source integration, and downstream cache invalidation.
- `app.py`:
  - Enterprise Data Hub UI (integrated from branch `Maryam`): CSV, Excel, DB, API, and Demo tabs with interactive column mapping, pre-validation, and dynamic active dataset metrics.
- `agent/tools.py`:
  - Consumes `active_dataset` with automatic cache invalidation on dataset changes, and `set_active_datasource` bridge for UI synchronization.
- `data_ingestion/api_source.py`:
  - Production contract defined with client injection and transparent connection declarations.
- `tests/test_multi_date_sku_demand.py`:
  - 5 tests verifying multi-date time series demand, unique SKU dropdowns, chronological history, and lack of cross-SKU leakage.

**Status:** Verified locally across all 100 tests. Committed to branch `Bushra`.


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

Productization work is pending.

The next task must be selected from:

`## Productization Roadmap — Active Execution Queue`

The AI coding agent must start with the highest-priority unchecked task and must not skip ahead unless the current task is blocked.

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

## MVP Verification Status

**Status: ✅ MVP COMPLETE**

The original MVP phases are complete, deployed, and verified.

This does NOT mean the final productization roadmap is complete.

The project is now in:

**MVP COMPLETE → PRODUCTIZATION IN PROGRESS**

The productization roadmap below is the authoritative source for remaining implementation work.

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

# Productization Roadmap — Active Execution Queue

> This is the active task board for AI coding agents.
>
> Before coding, the agent MUST:
> 1. Read this entire `progress.md`.
> 2. Inspect the actual repository.
> 3. Understand what is already completed.
> 4. Find the first unchecked task below.
> 5. Work on that task.
> 6. Test it.
> 7. Verify it.
> 8. Only then mark it complete.
>
> Do not rebuild completed MVP modules.
> Do not invent schemas.
> Do not silently change architecture.
> Do not implement features outside the current product scope.

## P0 — Active Business Dataset

- [x] Create a single active-dataset context used by the backend — implementation exists locally; verification/merge pending.
- [x] Ensure selected CSV/Excel/DB/API data reaches downstream modules.
- [x] Remove hidden dependency on bundled synthetic CSVs.
- [x] Prevent silent fallback to synthetic data.
- [x] Track dataset source, identity, status, and lifecycle.
- [x] Add tests proving the selected dataset is actually consumed.

> Upload/select UI implemented on branch `Maryam` (Enterprise Data Hub with CSV, Excel, DB, and API selection tabs, schema mapping, and validation).
> Backend support for the active dataset context completed on branch `Bushra`.

## P1 — Data Validation & Understanding

- [ ] Define canonical schemas for demand, inventory, deliveries, and vehicles.
- [ ] Validate required columns.
- [ ] Validate datatypes.
- [ ] Validate missing values.
- [ ] Validate duplicates.
- [ ] Validate dates.
- [ ] Validate numeric/business values.
- [ ] Validate cross-table relationships.
- [ ] Produce structured validation results.
- [ ] Distinguish errors from warnings.
- [ ] Add schema mapping/normalization.
- [ ] Add tests for valid and invalid real-data-shaped inputs.

## P2 — Unified Supply Chain Intelligence

- [ ] Create a unified supply-chain situation/state.
- [ ] Combine demand, inventory, delivery, and logistics intelligence.
- [ ] Identify affected SKUs/orders/deliveries.
- [ ] Identify severity and operational bottlenecks.
- [ ] Preserve source attribution for numerical outputs.
- [ ] Feed unified intelligence into the Decision Agent.
- [ ] Add integration tests.

## P3 — Candidate Action Engine

- [ ] Define structured candidate actions.
- [ ] Generate actions from detected risks.
- [ ] Include `do_nothing`.
- [ ] Calculate supported consequences deterministically.
- [ ] Apply hard business constraints.
- [ ] Remove infeasible actions.
- [ ] Compare feasible actions and trade-offs.
- [ ] Ensure the agent selects from evidence-backed actions.
- [ ] Add tests for invalid/policy-violating actions.

## P4 — Productized AI Decision Agent

- [ ] Connect unified situation to the agent.
- [ ] Ensure situation-dependent tool selection.
- [ ] Ensure all numerical values originate from deterministic tools.
- [ ] Improve structured recommendation schema.
- [ ] Include evidence, alternatives, constraints, impact, and uncertainty where supported.
- [ ] Handle LLM timeout/API failure safely.
- [ ] Ensure LLM failure cannot create a fake recommendation.

## P5 — Policy Enforcement / RAG

- [ ] Ensure relevant policies are retrieved for decisions.
- [ ] Attach policy source/section to recommendations.
- [ ] Convert applicable hard policies into decision constraints.
- [ ] Block policy-violating candidate actions.
- [ ] Distinguish hard constraints from guidelines.
- [ ] Add tests proving policies can change the available actions.
- [ ] Store policy constraints in the decision trace.

## P6 — Independent Multi-Agent Validation

- [ ] Verify Policy Critic independently evaluates recommendations.
- [ ] Verify Business Critic independently evaluates recommendations.
- [ ] Ensure critics can challenge the primary agent.
- [ ] Define deterministic escalation rules.
- [ ] Handle critic disagreement.
- [ ] Handle insufficient evidence.
- [ ] Handle hard policy violations.
- [ ] Ensure consensus cannot blindly copy the primary agent.
- [ ] Add adversarial tests.

## P7 — Human Approval & Governance

- [ ] Ensure consequential recommendations require approval.
- [ ] Record approval/rejection.
- [ ] Record approver.
- [ ] Record timestamp.
- [ ] Record notes/reason.
- [ ] Prevent duplicate approval/rejection.
- [ ] Preserve rejected decisions in history.
- [ ] Preserve trace linkage.

## P8 — What-If Simulation Integration

- [ ] Start simulation from actual recommendations.
- [ ] Automatically calculate `do_nothing`.
- [ ] Compare recommended action vs baseline.
- [ ] Reuse deterministic ML/risk/optimization outputs.
- [ ] Show relevant KPI deltas.
- [ ] Show assumptions.
- [ ] Handle unsupported scenarios safely.
- [ ] Persist simulation against the decision trace.
- [ ] Add integration tests.

## P9 — Business Impact

- [ ] Define supported business KPIs.
- [ ] Calculate baseline KPIs from actual data.
- [ ] Calculate recommended-action KPIs.
- [ ] Calculate deterministic deltas.
- [ ] Show expected benefit/cost/trade-offs.
- [ ] Clearly distinguish estimates from measured results.
- [ ] Never invent financial savings.
- [ ] Add business-impact tests.

## P10 — Complete Audit Trail

- [ ] Record dataset identity/source.
- [ ] Record validation.
- [ ] Record situation.
- [ ] Record predictions.
- [ ] Record risks.
- [ ] Record optimization.
- [ ] Record candidate actions.
- [ ] Record policies and constraints.
- [ ] Record tools and results.
- [ ] Record primary proposal.
- [ ] Record both critics.
- [ ] Record consensus.
- [ ] Record human decision.
- [ ] Record simulation.
- [ ] Record business impact.
- [ ] Record final outcome.
- [ ] Ensure traces are reconstructable.
- [ ] Ensure secrets are never persisted.

## P11 — Product Dashboard

> Coordinate with the teammate implementing data-source/upload UI.

- [ ] Replace hardcoded dashboard metrics with active-dataset results.
- [ ] Remove misleading static demo metrics from production views.
- [ ] Show dataset status.
- [ ] Show data-quality status.
- [ ] Show current supply-chain situation.
- [ ] Show major risks.
- [ ] Show recommendation.
- [ ] Show evidence.
- [ ] Show policy constraints.
- [ ] Show independent reviews.
- [ ] Show decision validation.
- [ ] Show approval state.
- [ ] Show simulation.
- [ ] Show business impact.
- [ ] Show decision history.

Use business-facing terminology:

`Analyze Situation`
`AI Recommendation`
`Independent Review`
`Decision Validation`
`Evidence & Analysis`
`Policies & Business Rules`
`Decision Transparency`
`What-If Simulation`
`Business Impact`
`Decision History`

## P12 — End-to-End Real Data Flow

- [ ] CSV → validation → canonical data → intelligence → decision.
- [ ] Excel → validation → canonical data → intelligence → decision.
- [ ] Database → validation → canonical data → intelligence → decision.
- [ ] API → validation → canonical data → intelligence → decision when production connector exists.
- [ ] Verify no synthetic fallback.
- [ ] Verify all displayed numbers come from actual computation.
- [ ] Verify approval persistence.
- [ ] Verify complete trace.

## P13 — Testing & Reliability

- [ ] Unit tests for new components.
- [ ] Integration tests for data → ML.
- [ ] Integration tests for ML → agent.
- [ ] Integration tests for agent → critics → consensus.
- [ ] Integration tests for approval → simulation → impact.
- [ ] Invalid dataset tests.
- [ ] Empty dataset tests.
- [ ] Missing-column tests.
- [ ] LLM failure tests.
- [ ] Database failure tests.
- [ ] RAG failure tests.
- [ ] Optimization failure tests.
- [ ] Conflicting-critic tests.
- [ ] Approval/rejection edge cases.
- [ ] Full `uv run pytest`.
- [ ] No regression from existing 90/90 baseline.

## P14 — Production Hardening

- [ ] Fresh-clone installation verified.
- [ ] Dependencies verified.
- [ ] Streamlit deployment verified.
- [ ] Neon connectivity verified.
- [ ] Groq connectivity verified.
- [ ] Cold-start behavior verified.
- [ ] Policy index rebuild verified.
- [ ] Real-data flow verified on deployment.
- [ ] Safe user-facing errors.
- [ ] No secret exposure.
- [ ] No developer-machine dependencies.
- [ ] Complete live end-to-end verification.

## P15 — Documentation

- [ ] Update README for the productized system.
- [ ] Document supported data sources.
- [ ] Document canonical schemas.
- [ ] Document validation.
- [ ] Document architecture.
- [ ] Document AI/ML responsibilities.
- [ ] Document multi-agent review.
- [ ] Document RAG/policy enforcement.
- [ ] Document human approval.
- [ ] Document simulation.
- [ ] Document business impact.
- [ ] Document auditability.
- [ ] Document limitations.
- [ ] Clearly label synthetic demo data.
- [ ] Remove outdated MVP-only claims.

## P16 — Final Product Verification

- [ ] Real business dataset can drive the system.
- [ ] Dataset is validated.
- [ ] Dataset becomes the active dataset.
- [ ] No hidden synthetic fallback exists.
- [ ] Forecasting uses active data.
- [ ] Inventory intelligence uses active data.
- [ ] Delivery intelligence uses active data.
- [ ] Logistics uses active data.
- [ ] Unified situation is created.
- [ ] Candidate actions are evidence-backed.
- [ ] Policies constrain decisions.
- [ ] AI agent reasons over actual evidence.
- [ ] Critics independently challenge the proposal.
- [ ] Consensus validates the decision.
- [ ] Deterministic constraints cannot be overridden by the LLM.
- [ ] Human approval is mandatory for consequential actions.
- [ ] Simulation uses actual outputs.
- [ ] Business impact is measurable.
- [ ] Complete audit trail exists.
- [ ] Integration tests pass.
- [ ] Deployment works.
- [ ] Documentation matches implementation.
- [ ] Non-technical users can understand the complete decision flow.

---

## CURRENT ACTIVE TASK

### P0 — ActiveDataset Context

**Task:** P0 — Active Business Dataset Foundation

**Current state:** Verified locally with 95/95 passing tests; ready to push to branch `Bushra`.

**Verified local files:**
- `data_ingestion/active_dataset.py`
- `tests/test_active_dataset.py`
- `agent/tools.py`
- `app.py`
- `data_ingestion/api_source.py`

AI coding agents must begin with the current active task unless it is blocked.

After completing a task:

1. Implement.
2. Test.
3. Verify using actual terminal output ask permission to run the commands and check the output.
4. Fix any failures and retest.
5. Update the roadmap state.
6. Record what changed.
7. Identify the next unchecked task.

Do not mark a task `DONE` before it is verified and pushed to branch Bushra.

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
- Recreate a file that already exists locally without first inspecting it.
- Treat unverified local changes described in `Current Working State` as merged/completed.
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

## Product Scope Control

SupplyChain Sentinel AI is treated as ONE unified product.

The product combines:

- Demand Forecasting
- Inventory Risk Intelligence
- Delivery Risk Intelligence
- Route Optimization
- Unified Supply Chain Intelligence
- Candidate Action Generation
- AI Decision Agent
- Policy/RAG Grounding
- Independent Multi-Agent Review
- Decision Validation
- Human Approval
- What-If Simulation
- Business Impact
- Decision History & Auditability
- Real Business Data Onboarding

### Out of Current Scope

The following are future expansion areas and must NOT be implemented during the current productization cycle:

- Supplier Risk Intelligence
- External Disruption Intelligence
- External News Intelligence
- Advanced supplier monitoring

Do not introduce unrelated AI features simply because they appear technically interesting.

The current objective is to make the existing capabilities operate together as one complete, reliable, explainable, and measurable product.
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

### Unmerged Work Rule

- `Current Working State` may describe local work that has been created but is not yet verified or merged.
- Such work must never appear under `Completed (merged to main)`.
- Only the Team Leader changes that work to `REVIEW`/`DONE` after actual verification and merge.
- A fresh AI session must inspect the existing local files before making further changes.

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

---

# 🚀 PRODUCTIZATION ROADMAP — ACTIVE DEVELOPMENT

> This section is the active execution source of truth for AI coding agents.
>
> IMPORTANT:
> - Read the entire `progress.md` before making changes.
> - The sections above describe the verified existing system and historical work.
> - Do NOT rebuild completed functionality.
> - Work only on the earliest/highest-priority incomplete task.
> - Inspect the actual repository before editing any file.
> - A task is not complete because code was written. It is complete only after implementation, testing, verification, and successful integration.
> - Update this checklist only from verified repository/test/deployment evidence.
>
> Current goal:
>
> **Transform the working MVP into a coherent, production-quality SupplyChain Sentinel AI product where real business data can flow through the complete decision-intelligence pipeline.**

## Product Goal

The final product should provide this complete experience:

```text
Business Data
    ↓
Data Validation & Understanding
    ↓
Canonical Supply Chain Dataset
    ↓
Demand Forecasting
    ↓
Inventory Risk
    ↓
Delivery Risk
    ↓
Route Optimization
    ↓
Unified Supply Chain Situation
    ↓
Candidate Actions
    ↓
AI Decision Agent
    ↓
Policy / RAG Grounding
    ↓
Independent AI Critics
    ↓
Decision Validation / Consensus
    ↓
Human Approval
    ↓
What-If Simulation
    ↓
Business Impact
    ↓
Decision History / Audit Trace

The product must answer:

What is happening?
What is likely to happen?
How serious is the risk?
What actions are available?
Which action is best?
Why is it recommended?
What policies constrain the decision?
What happens if we take the action?
What happens if we do nothing?
What was finally approved/rejected and why?
ACTIVE PRODUCTIZATION CHECKLIST
P0 — Active Business Dataset Foundation
Backend dataset lifecycle
 [x] Define a single ActiveDataset / dataset-context abstraction for the currently selected business dataset.
 [x] Ensure the active dataset can be passed consistently from the application layer into backend/core services.
 [x] Remove hidden assumptions that data/ synthetic CSV files are always the active source.
 [x] Ensure every downstream module receives the selected dataset explicitly.
 [x] Prevent silent fallback to synthetic demo data when a real dataset is selected.
 [x] Add clear dataset lifecycle states:
uploaded/connected
validated
active
failed
replaced
 [x] Store enough metadata to identify the active dataset and its source.
 [x] Ensure replacing the active dataset invalidates/rebuilds dependent derived results when necessary.
 [x] Add tests proving that the selected dataset is actually consumed downstream.
Data source integration
 [x] Verify CSV source works with the active-dataset architecture.
 [x] Verify Excel source works with the active-dataset architecture.
 [x] Verify database source works with the active-dataset architecture.
 [x] Define the production contract for API ingestion.
 [x] Keep API ingestion extensible without pretending the current stub is production-ready.
 [x] Ensure the backend can consume all supported source types through the same canonical interface.

UI for selecting/uploading CSV, Excel, API, and Database is handled separately by another team member.
- [x] Upload/select UI verified on branch `Maryam` (Enterprise Data Hub with CSV, Excel, DB, and API selection tabs, schema mapping, and validation).

Backend integration with the selected dataset IS part of this roadmap (completed on branch `Bushra`).

P1 — Data Understanding & Canonical Data Model
 Define canonical schemas for:
demand
inventory
deliveries
vehicles/routes
 Add required-column validation.
 Add datatype validation.
 Add missing-value validation.
 Add duplicate detection.
 Add invalid-date detection.
 Add invalid numeric-value detection.
 Add identifier consistency checks.
 Add cross-table relationship validation.
 Add business-rule validation.
 Produce structured validation results.
 Clearly distinguish fatal errors from warnings.
 Add safe handling for invalid datasets.
 Build schema mapping/normalization where practical.
 Ensure real-world column names can be mapped into the canonical model without modifying core ML logic.
 Add tests for valid and invalid datasets.
 Verify synthetic/demo data also passes through the same canonical pipeline.
Data Understanding Output

The product should be able to summarize:

Dataset source
Rows / columns
Date range
SKUs
Locations
Deliveries
Missing values
Data quality warnings
Available operational signals
Detected limitations

This must come from actual loaded data, not hardcoded values.

P2 — Unified Supply Chain Intelligence

Current modules already exist individually.

The next goal is to make them behave as one intelligence system.

 Create a unified supply-chain situation/state object.
 Combine demand forecast outputs with inventory state.
 Combine inventory state with delivery risk where relevant.
 Combine delivery risk with route/logistics information.
 Preserve source attribution for every numerical output.
 Define a consistent risk representation.
 Define overall supply-chain situation severity.
 Identify affected SKUs/orders/deliveries.
 Identify the operational bottleneck.
 Identify dependencies between risks.
 Ensure the agent receives this unified situation rather than manually assembled disconnected values.
 Add tests for combined inventory + logistics situations.
 Ensure irrelevant intelligence layers are not invoked unnecessarily.
Required principle
Forecast → Risk → Situation

NOT

Forecast
Inventory
Delivery
Routes

as four disconnected features.
P3 — Candidate Action & Decision Intelligence

The system currently identifies risks and produces recommendations.

Productization requires an explicit decision layer.

 Define structured candidate actions.
 Generate actions from actual detected risks.
 Examples:
reorder
expedite
transfer inventory
adjust allocation
reroute delivery
prioritize shipment
do nothing
 Attach measurable consequences to each candidate action where supported by deterministic logic.
 Attach applicable policy constraints to each action.
 Reject actions violating hard business rules.
 Compare feasible actions.
 Represent trade-offs explicitly.
 Include a do_nothing baseline.
 Ensure the primary AI agent selects from evidence-backed candidate actions rather than inventing arbitrary actions.
 Add tests proving infeasible/policy-violating actions cannot become the final recommendation.
P4 — AI Decision Agent Productization

Existing agent/tool-calling functionality is already complete at MVP level.

Now harden it for the product.

 Feed the unified supply-chain situation into the agent.
 Ensure tool selection is situation-dependent.
 Ensure all tool results are structured and traceable.
 Ensure the agent cannot invent numerical values.
 Ensure recommendation references actual evidence.
 Ensure candidate actions are grounded in deterministic outputs.
 Improve structured recommendation schema.
 Include:
situation
risk
recommended action
alternatives
evidence
policy constraints
expected impact
confidence/uncertainty where legitimately supported
 Add graceful handling for LLM/API failure.
 Add retry/time-out handling where appropriate.
 Ensure an LLM failure never produces a fake recommendation.
P5 — RAG & Policy Enforcement

RAG already exists and retrieval is tested.

Productization requires policies to actually affect decisions.

 Ensure relevant policies are retrieved for each decision.
 Attach policy source/section to recommendations.
 Convert applicable policy constraints into structured decision constraints where possible.
 Ensure candidate actions violating hard policies are rejected.
 Ensure the agent cannot override deterministic policy constraints.
 Distinguish:
hard constraints
recommendations/guidelines
informational policy context
 Add tests where policy changes the available action set.
 Add tests where the agent proposes a policy-violating action and the system blocks/escalates it.
 Ensure policy references appear in the decision trace.
P6 — Independent Multi-Agent Review & Decision Validation

Existing critics and consensus exist.

Now make them a reliable product control layer.

Policy/Safety Review
 Verify Policy Critic independently evaluates the proposal.
 Verify it can reject/escalate unsafe or policy-invalid recommendations.
 Ensure it receives the relevant policy evidence.
Business Impact Review
 Verify Business Critic independently evaluates cost/feasibility.
 Ensure it receives actual deterministic impact numbers.
 Ensure it can challenge the primary agent.
Consensus
 Ensure consensus compares all structured outputs.
 Ensure disagreements are explicitly recorded.
 Ensure consensus cannot blindly copy the primary agent.
 Define deterministic escalation rules.
 Define what happens when critics disagree.
 Define what happens when evidence is insufficient.
 Define what happens when a hard policy violation exists.
 Add adversarial tests where critics challenge the primary proposal.

Required architecture:

Primary Agent
      ↓
 ┌────┴────┐
 ↓         ↓
Policy    Business
Critic    Critic
 └────┬────┘
      ↓
 Consensus
      ↓
Validated Recommendation
P7 — Human Approval & Governance
 Ensure every consequential recommendation enters pending state.
 Ensure approval/rejection is explicit.
 Ensure no consequential action is automatically executed.
 Record approver.
 Record timestamp.
 Record approval/rejection reason or notes.
 Ensure rejected decisions remain auditable.
 Ensure approved decisions remain linked to their original trace.
 Handle duplicate approval/rejection safely.
 Add authorization/error handling where applicable.
P8 — What-If Simulation Product Integration

Simulation already exists at MVP level.

Now connect it directly to decision intelligence.

 Start simulation from the actual recommendation.
 Automatically establish the do_nothing baseline.
 Automatically establish the recommended-action scenario.
 Reuse actual model/risk/optimization logic.
 Ensure simulation does not invent unsupported numbers.
 Compare:
stockout risk
inventory level
delivery risk
route distance/cost
operational impact
relevant business KPIs
 Show action delta.
 Show downside/upside.
 Clearly communicate assumptions.
 Handle unsupported simulations safely.
 Store simulation results against the decision trace.
 Add tests connecting recommendation → simulation.
P9 — Business Impact Layer

Turn technical outputs into measurable business outcomes.

 Define supported business KPIs.
 Calculate KPI values from actual dataset/model outputs.
 Define baseline KPIs.
 Define recommended-action KPIs.
 Calculate deterministic deltas.
 Show:
expected benefit
expected cost
risk reduction
operational trade-off
 Never claim financial savings unless supported by actual inputs/assumptions.
 Clearly label estimates vs measured outcomes.
 Add business-impact tests.
 Ensure the Business Critic consumes the same impact calculations.
P10 — Complete Decision Trace & Auditability

The existing decision trace must become a complete product audit record.

 Record dataset/source identity.
 Record dataset validation result.
 Record input situation.
 Record predictions.
 Record risk outputs.
 Record route/optimization outputs.
 Record candidate actions.
 Record policies retrieved.
 Record policy constraints applied.
 Record tools called.
 Record tool inputs/outputs.
 Record primary proposal.
 Record policy critic.
 Record business critic.
 Record consensus.
 Record human decision.
 Record simulation.
 Record business impact.
 Record final outcome.
 Make the trace reconstructable without relying on transient UI state.
 Ensure sensitive credentials/secrets are never stored in traces.
 Add trace integrity/completeness tests.
P11 — Product Dashboard & User Experience

Coordinate with the teammate implementing the data-source/upload UI.
Do not duplicate their work.

 Replace hardcoded/demo dashboard metrics with active-dataset results.
 Remove misleading static SKU/shipment examples from production views.
 Show dataset status.
 Show data-quality status.
 Show current supply-chain situation.
 Show major risks.
 Show recommended actions.
 Show evidence behind recommendations.
 Show policy constraints.
 Show independent reviews.
 Show validation result.
 Show approval state.
 Show simulation.
 Show business impact.
 Show decision history.
 Make the UI understandable to a non-technical business user.

Use business-facing terminology:

Analyze Situation
AI Recommendation
Independent Review
Decision Validation
Evidence & Analysis
Policies & Business Rules
Decision Transparency
What-If Simulation
Business Impact
Decision History

Avoid exposing implementation terminology as the primary UX:

Run Orchestrator
Critic Agent
Consensus Engine
Tool Calls
RAG Context
Trace JSON
P12 — End-to-End Product Flow

The complete flow must work using the active dataset:

Select / Upload / Connect Data
        ↓
Validate Dataset
        ↓
Understand Dataset
        ↓
Build Canonical Data
        ↓
Analyze Supply Chain
        ↓
Forecast Demand
        ↓
Detect Inventory Risk
        ↓
Detect Delivery Risk
        ↓
Optimize Logistics
        ↓
Create Unified Situation
        ↓
Generate Candidate Actions
        ↓
AI Recommendation
        ↓
Policy Grounding
        ↓
Independent Reviews
        ↓
Decision Validation
        ↓
Human Approval
        ↓
What-If Simulation
        ↓
Business Impact
        ↓
Decision History / Audit Trace
 Verify complete flow locally.
 Verify complete flow using CSV.
 Verify complete flow using Excel.
 Verify complete flow using database source.
 Verify API path when production connector is implemented.
 Verify no synthetic fallback occurs when a real dataset is active.
 Verify all displayed numbers originate from actual computation.
 Verify approval state persists.
 Verify trace contains the entire lifecycle.
P13 — Testing & Reliability
 Add unit tests for every new productization component.
 Add integration tests across data → ML → agent.
 Add integration tests across agent → critics → consensus.
 Add integration tests across approval → simulation → impact.
 Add real-data-shaped fixtures.
 Test malformed datasets.
 Test empty datasets.
 Test missing columns.
 Test missing values.
 Test unexpected column names.
 Test impossible business values.
 Test LLM failure.
 Test database failure.
 Test policy retrieval failure.
 Test optimization failure.
 Test simulation failure.
 Test conflicting critic outputs.
 Test policy violations.
 Test approval/rejection edge cases.
 Run complete uv run pytest.
 Confirm no regression against the existing 90/90 baseline.
P14 — Deployment & Production Hardening
 Verify fresh-clone installation.
 Verify required dependencies are declared.
 Verify Streamlit deployment.
 Verify Neon connectivity.
 Verify Groq connectivity.
 Verify cold-start behavior.
 Verify policy index rebuild behavior.
 Verify real dataset flow on deployment.
 Verify errors are user-safe.
 Verify secrets are never exposed.
 Verify no local-only paths are required.
 Verify production app does not depend on developer machine state.
 Perform complete live end-to-end test after productization changes.
P15 — Documentation & Product Readiness
 Update README to describe the final product rather than only the MVP.
 Document supported data sources.
 Document canonical schemas.
 Document validation behavior.
 Document architecture.
 Document AI/ML responsibilities.
 Document multi-agent review.
 Document policy grounding.
 Document human approval.
 Document simulation.
 Document business impact.
 Document decision trace.
 Document limitations.
 Clearly label synthetic demo data.
 Remove outdated MVP/project-number terminology.
 Ensure README matches actual implementation.
 Ensure no documentation claims an unimplemented capability.
P16 — Final Product Verification

The product is COMPLETE only when every statement below can be verified:

 A user can provide/select a business dataset.
 The system validates the dataset.
 The system understands the dataset.
 The selected dataset becomes the active dataset.
 No hidden synthetic fallback occurs.
 Demand forecasting uses the active data.
 Inventory intelligence uses the active data.
 Delivery risk uses the active data.
 Logistics optimization uses actual operational data.
 All intelligence is combined into a unified situation.
 Candidate actions are generated from actual risks.
 Policies constrain decisions.
 The primary agent reasons over actual evidence.
 Independent critics challenge the recommendation.
 Consensus validates the recommendation.
 Hard deterministic constraints cannot be overridden by the LLM.
 Human approval is required for consequential actions.
 Simulation uses actual decision outputs.
 Business impact is calculated from supported data.
 Complete decision history is persisted.
 Every important number is traceable to deterministic computation.
 End-to-end integration tests pass.
 Deployment works.
 Documentation matches reality.
 The product can be demonstrated to a non-technical judge without explaining the internal architecture first.
🔴 CURRENT ACTIVE TASK

AI coding agents must start here.

Current task: [SET AUTOMATICALLY TO FIRST UNCHECKED TASK]

Status: TODO

Rule:
The first unchecked item in the highest-priority incomplete section is the next task to implement.

Do not skip ahead unless:

the current task is blocked, or
its dependency is incomplete.

If blocked, record the reason directly beside the task.

🤖 VIBE CODING OPERATING PROTOCOL

Every AI coding session MUST follow this protocol.

STEP 1 — Read Context

Before touching code:

Read progress.md completely.
Read the current repository structure.
Inspect the files relevant to the current unchecked task.
Check Git status.
Check whether another branch/PR is already modifying the same area.

Never assume implementation details from this document alone.

STEP 2 — Select Task

Find the first unchecked task in:

P0 → P1 → P2 → P3 → ... → P16

Work on that task unless it is blocked.

Do not randomly choose a later task.

STEP 3 — Understand Before Editing

Before changing code, identify:

existing implementation
existing interfaces
existing tests
dependencies
downstream consumers
potential regressions

Do not rebuild working modules.

Prefer integration/refactoring over duplication.

STEP 4 — Implement

Make the smallest coherent change required.

Rules:

inspect before editing
preserve existing architecture
deterministic code owns numerical truth
LLM does not calculate numbers
RAG must influence decisions
critics must be genuinely independent
consensus must validate
human approval remains mandatory
synthetic data is only development/demo/test data
no secrets in code
no hardcoded production metrics
no silent fallback to synthetic data
STEP 5 — Test

Run the relevant tests.

Then run:

uv run pytest

Never claim success without actual test output.

STEP 6 — Verify

Verify the implementation against the actual requirement.

Check:

expected behavior
edge cases
regression risk
actual data flow
database persistence where applicable
UI behavior where applicable
trace completeness where applicable
STEP 7 — Update Progress

Only after verified completion:

mark the task [x]
add a short implementation note if useful
update Current Status
identify the next available task

Never mark a task complete merely because code exists.

STEP 8 — Commit / Merge State

A task is officially DONE only after:

Implementation
    ↓
Tests pass
    ↓
Verification
    ↓
PR
    ↓
Merge to main
    ↓
progress.md updated
🚫 DO NOT BUILD NOW

The following are intentionally outside the current productization scope:

Supplier Risk Intelligence
External Disruption Intelligence
External news intelligence
Advanced supplier monitoring
New unrelated AI features
Unnecessary microservices
Kubernetes/container orchestration unless genuinely required
Rebuilding existing ML models without evidence that they need replacement
Rebuilding the existing agent from scratch
Rebuilding existing RAG
Rebuilding existing simulation
Duplicating the teammate's ingestion/upload UI

These can be considered only after the core product is complete.

PRODUCTIZATION STATUS
Area	Status
MVP foundation	✅ COMPLETE
Predictive intelligence	✅ COMPLETE
Inventory intelligence	✅ COMPLETE
Delivery risk	✅ COMPLETE
Route optimization	✅ COMPLETE
RAG	✅ COMPLETE
AI Decision Agent	✅ MVP COMPLETE
Multi-agent critique	✅ MVP COMPLETE
Consensus	✅ MVP COMPLETE
Human approval	✅ MVP COMPLETE
What-if simulation	✅ MVP COMPLETE
Deployment	✅ COMPLETE
Active business dataset	⬜ TODO
Data validation & understanding	⬜ TODO
Canonical data model	⬜ TODO
Unified supply-chain intelligence	⬜ TODO
Candidate action engine	⬜ TODO
Productized decision intelligence	⬜ TODO
Policy enforcement	⬜ TODO
Multi-agent hardening	⬜ TODO
Business impact	⬜ TODO
Complete auditability	⬜ TODO
Product dashboard integration	⬜ TODO
End-to-end real-data flow	⬜ TODO
Production hardening	⬜ TODO
Final product verification	⬜ TODO
FINAL PRODUCT DEFINITION

SupplyChain Sentinel AI is complete when it is no longer just a collection of forecasting, risk, optimization, RAG, and agent modules.

It must operate as one decision-intelligence product:

Real supply-chain data → validated understanding → predictive intelligence → risk detection → candidate actions → AI reasoning → independent review → validated decision → human approval → what-if simulation → measurable business impact → complete audit trail.

The goal is not to demonstrate individual AI technologies.

The goal is to demonstrate that the platform can turn operational supply-chain data into validated, explainable, measurable, and governable business decisions.


### One more important change

Your current `progress.md` still has this older section:

> **Project Prioritization (Scope Control)**  
> Primary MVP = Project 17, Secondary MVP = Project 18, Project 10 = Future. :contentReference[oaicite:1]{index=1}

For the **new product direction**, I would remove/replace that section. It made sense when you were organizing three problem statements, but now it conflicts with your goal of treating this as **one unified product**.

Replace it with:

```md
## Product Scope Control

SupplyChain Sentinel AI is treated as ONE product.

Current product capabilities:

- Demand Forecasting
- Inventory Risk Intelligence
- Delivery Risk Intelligence
- Route Optimization
- Unified Supply Chain Intelligence
- AI Decision Agent
- Policy/RAG Grounding
- Independent Multi-Agent Review
- Decision Validation
- Human Approval
- What-If Simulation
- Business Impact
- Decision History & Auditability
- Real Business Data Onboarding

### Explicitly out of current scope

- Supplier Risk Intelligence
- External Disruption Intelligence
- External News Intelligence

These are future expansion areas and must not consume current development effort.

The current objective is to make the existing capabilities operate together as one complete product.