# SupplyChain Sentinel AI — Student Build Guide & Progress Tracker

**Last updated:** 2026-09-02
**What this file is:** A complete, self-contained handoff document. It teaches the concepts, shows the architecture, gives exact setup steps, hands off to a Claude Project for session-by-session building, tracks progress via a checklist, forces reflection via a learning log, and preempts the mistakes you will otherwise make twice. It is also the **live source of truth for a 4-person team building in parallel** (see Section 15) — anyone should be able to read this file and immediately understand what's done, what's in progress, what's blocked, and what's available to pick up next.

---

## Current Project State

### Completed
- Phase 0: Repository structure, `uv init`, dependencies (`pyproject.toml`, `uv.lock`), `.gitignore`, folder structure (`core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/`, `db/`, `api/`, `tests/`).
- Scope, architecture, ML rules, RAG design, AI Decision Agent design, evaluation methodology finalized.
- `data_ingestion/base.py` — Abstract `DataSource` interface.
- `data_ingestion/csv_source.py` — Concrete `CSVDataSource` implementation.
- `data_ingestion/excel_source.py` — Concrete `ExcelDataSource` implementation.
- `data_ingestion/db_source.py` — Concrete `DBDataSource` implementation (SQLAlchemy / Neon Postgres).
- `data_ingestion/api_source.py` — Enterprise API `APIDataSource` interface stub.
- `data_pipeline/generate_seed_data.py` — Seed data generator & synthetic datasets in `data/` (`historical_demand.csv`, `inventory_snapshot.csv`, `deliveries.csv`).
- `ml/evaluation.py` — ML evaluation utilities (time-based split, leakage check, naive/majority baselines, MAE/RMSE/MAPE/AUC/F1 metrics).
- Unit tests in `tests/test_data_ingestion.py`, `tests/test_additional_sources.py`, and `tests/test_evaluation.py` (14 tests, 100% passing).

### In Progress
- None.

### Blocked
- None.

### Next Available Tasks
- `policies/*.md` (Written business/procurement/inventory policy documents for RAG engine)
- `db/models.py`, `db/connection.py` (Postgres schema models & database connection)
- `core/forecasting.py` (Demand forecasting model module)

### Last Updated
- **Date:** 2026-09-02
- **Developer:** Maryam
- **Branch:** `Maryam`
- **Commit:** Updated

---

## Why each section matters
| Section | Why it's here |
|---|---|
| 📚 Concepts First | Embeddings, cosine similarity, RAG, Streamlit, FastAPI, Uvicorn, OR-Tools, uv, Postgres, tool-using agents, SHAP, Git — explained with analogies. |
| 🏗️ Scope & Architecture | The finalized MVP scope, tech stack (with cost), folder structure, database, and data ingestion design — production-minded but realistic for one month. |
| 🤖 AI Decision Agent Design | How the agent genuinely calls tools (not a disguised pipeline), what the decision trace looks like, and the human-approval gate before any real action. |
| 📐 ML Engineering Rules | Time-based splits, no data leakage, baseline comparison, evaluation metrics, and explainability — the rules that make this a defensible ML project, not a curve-fit demo. |
| 💻 VS Code Setup | Extensions, terminal rules, `uv` environment — the local dev environment. |
| 🔑 Groq API Setup | Free LLM access, step by step. |
| 🤖 Claude Project Setup | Exact copy-paste instructions — the handoff from here on. |
| 🌿 GitHub Workflow | Exact git commands after every file. |
| 🧪 Testing Strategy | pytest for core modules and agent/tool behavior — confirming code works, not just "looking right." |
| ✅ Build Checklist | Phase by phase. Tick boxes as you go. |
| 📓 Learning Log | Forces reflection after every session. |
| ⚠️ Common Mistakes | The errors you will predictably make. |
| 🎯 Project Prioritization | What's primary MVP, secondary MVP, and Phase 2 — so scope never silently creeps. |
| 🧑🤝🧑 Team of 4 — Parallel Development | No fixed roles. How 4 people pick tasks, avoid collisions, branch, review, and keep this file as the shared source of truth. |

---

## 1. Concepts First
*(Refer to documentation for concepts on Embeddings, Cosine Similarity, RAG, Streamlit, FastAPI, Uvicorn, OR-Tools, uv, Neon Postgres, Tool-Using Agents, SHAP, Decision Trace, Human-in-the-loop, Grounding Constraint, Git).*

---

## 2. Scope & Architecture

### What is this project?
An end-to-end AI-powered supply-chain **decision intelligence** platform. Pipeline:
`Data → Prediction → Risk Detection → Scenario Analysis → Optimization → AI Decision Agent → Recommended Action → Human Approval → Measurable Business Impact`

### Tech Stack & Cost
| Layer | Choice | Cost |
|---|---|---|
| Environment/packages | `uv` + `pyproject.toml` + `uv.lock` | Free |
| Backend | FastAPI + Uvicorn | Free |
| ML | scikit-learn, LightGBM, Prophet/statsmodels, SHAP | Free |
| Optimization | OR-Tools | Free |
| RAG | ChromaDB + sentence-transformers | Free |
| Agent / LLM | Groq API (tool/function calling) | Free |
| Database | Neon PostgreSQL | Free |
| Testing | pytest | Free |
| Frontend/Deploy | Streamlit Community Cloud | Free |

---

## 10. Build Checklist

### Phase 0 — Setup
- [x] VS Code + extensions installed
- [x] `uv init` run, `pyproject.toml` created
- [x] Initial dependencies added via `uv add ...`, `uv.lock` generated
- [x] Folder structure created (`core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/`, `db/`, `policies/`, `api/`, `tests/`, `data/`)
- [x] Git repo initialized, `.gitignore` in place, first commit pushed to GitHub

### Phase 1 — Data Layer & Core ML Logic
- [x] `data_ingestion/base.py` — abstract `DataSource` interface defined
- [x] `data_ingestion/csv_source.py` — synthetic dataset loaded via this interface (dev/test only)
- [x] `data_ingestion/excel_source.py`, `db_source.py` — working sample implementations
- [x] `data_ingestion/api_source.py` — extensible interface/example only
- [ ] `db/models.py`, `db/connection.py` — Neon Postgres schema created and connected
- [ ] `data_pipeline/` scripts: source data → Neon Postgres
- [ ] `core/forecasting.py` — demand forecasting model, time-based split, baseline comparison
- [ ] `core/inventory_risk.py` — stockout/overstock logic
- [ ] `core/delivery_risk.py` — delivery risk classifier
- [ ] `core/logistics_optimizer.py` — OR-Tools VRP
- [x] `ml/evaluation.py` — split/leakage-check/baseline-comparison utilities
- [ ] `ml/explainability.py` — SHAP/feature importance for delivery risk
- [x] `tests/test_*.py` for each module above

---

## 15. Team of 4 — Parallel Development Workflow

### 15.0 Team
- **Team Leader:** Bushra
- **Members:** Maryam, Shreeya, Samiya
- **Shared GitHub repository:** https://github.com/bushrachohan/SupplyChain

### 15.2 Task Status System — Live Task Board

**Phase 0 — Setup**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| Repo structure + `uv init` | DONE | Bushra | main | — |
| Neon Postgres provisioning | TODO | — | — | — |
| Groq API key setup | TODO | — | — | — |
| Claude Project setup | TODO | — | — | — |

**Phase 1 — Data Layer & Core ML Logic**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| `data_ingestion/base.py` + `csv_source.py` | DONE | Maryam | Maryam | repo structure |
| `data_ingestion/excel_source.py`, `db_source.py` | DONE | Maryam | Maryam | `base.py` |
| `data_ingestion/api_source.py` | DONE | Maryam | Maryam | `base.py` |
| `db/models.py`, `db/connection.py` | TODO | — | — | Neon provisioning |
| `data_pipeline/` (load data → Neon) | TODO | — | — | `db/models.py` |
| `core/forecasting.py` | TODO | — | — | `data_pipeline/` |
| `core/inventory_risk.py` | TODO | — | — | `forecasting.py` |
| `core/delivery_risk.py` | TODO | — | — | `data_pipeline/` |
| `core/logistics_optimizer.py` | TODO | — | — | `data_pipeline/` |
| `ml/evaluation.py` | DONE | Maryam | Maryam | — |
| `ml/explainability.py` | TODO | — | — | `delivery_risk.py` |
| Tests for all of the above | DONE | Maryam | Maryam | respective modules |

**Phase 2 — RAG, Agent, Decision Trace**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| `policies/*.md` (real policy docs) | TODO | — | — | — |
| `core/rag.py` | TODO | — | — | `policies/` |
| `llm/explainer.py` | TODO | — | — | Groq key |
| `agent/tools.py` | TODO | — | — | `core/*` modules |
| `agent/orchestrator.py` | TODO | — | — | `agent/tools.py` |
| `agent/decision_trace.py` | TODO | — | — | orchestrator, `db/models.py` |
| Tests for all of the above | TODO | — | — | respective modules |

**Phase 3 — Human-in-the-Loop UI**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| `api/main.py` | TODO | — | — | `agent/`, `core/` |
| `app.py` (Streamlit + approval UI) | TODO | — | — | `agent/`, `decision_trace.py` |

**Phase 4 — Deploy**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| Finalize `pyproject.toml`/`uv.lock` | TODO | — | — | all above |
| Streamlit Cloud deploy + secrets | TODO | — | — | `app.py` |
| Full `pytest` suite passing | TODO | — | — | all modules |

---

## Session Handoff

Date: 2026-09-02
Developer: Maryam
Branch: `Maryam`
Task: Data Ingestion Layer (CSV, Excel, DB, API sources), Seed Data Pipeline, & ML Evaluation Utilities
Status: DONE

What was completed:
- Abstract `DataSource` interface in `data_ingestion/base.py`
- Concrete `CSVDataSource`, `ExcelDataSource`, `DBDataSource`, and `APIDataSource` implementations
- Synthetic data generation script in `data_pipeline/generate_seed_data.py` & seed files in `data/`
- Time-based splits, leakage checks, baselines, and evaluation metrics in `ml/evaluation.py`
- Automated test suites in `tests/test_data_ingestion.py`, `tests/test_additional_sources.py`, and `tests/test_evaluation.py` (14 passing tests)

Files created/modified:
- `progress.md`
- `data_ingestion/base.py`
- `data_ingestion/csv_source.py`
- `data_ingestion/excel_source.py`
- `data_ingestion/db_source.py`
- `data_ingestion/api_source.py`
- `data_pipeline/generate_seed_data.py`
- `ml/evaluation.py`
- `tests/test_data_ingestion.py`
- `tests/test_additional_sources.py`
- `tests/test_evaluation.py`
- `data/historical_demand.csv`, `data/inventory_snapshot.csv`, `data/deliveries.csv`

Tests run: `python -m pytest`
Test results: 14 passed in 6.21s
Commit: Merged & Pushed to `Maryam` branch
Known issues: None
Blocked by: None
Recommended next task: `policies/*.md` or `core/forecasting.py`
