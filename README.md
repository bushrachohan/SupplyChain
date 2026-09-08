# SupplyChain Sentinel AI

> **AI-Powered Supply Chain Risk & Decision Intelligence Platform**
> **An end-to-end system that forecasts demand, detects inventory & delivery risk, optimises routes, retrieves business policies via RAG, and runs a genuine multi-agent deliberation before surfacing recommendations for human approval.**

---


## Live Demo

🚀 🚀 [Check Out Product](https://supplychain-xiydr3sj8cfn8o5rstpg8t.streamlit.app/)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **ML / Forecasting** | LightGBM, scikit-learn, SHAP |
| **Optimisation** | Google OR-Tools (Capacitated VRP) |
| **RAG / Policy Retrieval** | ChromaDB + sentence-transformers (`all-MiniLM-L6-v2`) |
| **Agent / LLM** | Groq API — `openai/gpt-oss-120b` (tool/function calling) |
| **Database** | Neon PostgreSQL (serverless, free tier) |
| **Backend** | FastAPI + Uvicorn (local dev) |
| **Frontend** | Streamlit (production entry point) |
| **Environment** | `uv` + `pyproject.toml` + `uv.lock` |



---

## Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/54d7b715-72e6-4c83-a794-ab4f4c31ee47"
       alt="SupplyChain Sentinel AI Architecture"
       width="700">
</p>

---


## Quick Start (Local)

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/bushrachohan/SupplyChain.git
cd SupplyChain

# 2. Install all dependencies (including dev/test)
uv sync

# 3. Copy the example env file and fill in your secrets
cp .env.example .env
# Edit .env with your real GROQ_API_KEY and NEON_DATABASE_URL

# 4. Run the Streamlit app
uv run streamlit run app.py
```

### Run Tests

```bash
uv run pytest
# Expected: 116 passed
```

### Run FastAPI (local dev only)

```bash
uv run uvicorn api.main:app --reload
# Visit http://localhost:8000/docs
```

---

## Secrets Required

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free tier |
| `NEON_DATABASE_URL` | [neon.tech](https://neon.tech) — free tier PostgreSQL |

For local dev, place these in a `.env` file (never commit it).

---

## Deployment — Streamlit Cloud

1. **Push repo to GitHub** on the **`Bushra`** branch.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Connect your GitHub repo: `bushrachohan/SupplyChain`.
4. Set **Branch** to: `Bushra`.
5. Set **Main file path** to: `app.py`.
6. Set **Python version** to: `3.13` (or `3.12`).
7. Click **Advanced settings → Secrets** and paste (TOML syntax with double quotes):

```toml
GROQ_API_KEY = "gsk_..."
NEON_DATABASE_URL = "postgresql://..."
```

8. Click **Deploy**.

### ChromaDB on Streamlit Cloud
The `chroma_db/` directory is git-ignored. On each cold start, `core/rag.py` detects the missing index and rebuilds it automatically from `policies/*.md`. No manual action needed.

### Why `requirements.txt` instead of `pyproject.toml`?
Streamlit Community Cloud uses `pip` for installation and looks for `requirements.txt`. The `requirements.txt` in this repo is exported from `uv.lock`. When regenerating, **always include `--no-emit-project`** so `-e .` is not added:
```bash
uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt
```
> [!NOTE]
> Do not add `packages.txt` with `apt-get` packages unless strictly necessary; modern binary wheels already bundle OpenMP / C++ runtimes, and omitting `packages.txt` prevents Debian repository expiration errors during Streamlit Cloud deployment.

---

## Project Structure

```
SupplyChain/
├── app.py                     # Streamlit production entry point
├── api/main.py                # FastAPI (local dev / testing only)
├── agent/
│   ├── orchestrator.py        # Primary decision agent (Groq tool-calling)
│   ├── tools.py               # Tool wrappers + Groq function schemas
│   ├── critics/
│   │   ├── policy_critic.py   # Policy compliance + safety check
│   │   └── business_critic.py # Cost + feasibility check
│   ├── consensus.py           # Multi-agent consensus layer
│   └── decision_trace.py      # Builds + persists full trace to DB
├── core/
│   ├── forecasting.py         # LightGBM demand forecast
│   ├── inventory_risk.py      # Rule-based stockout/overstock
│   ├── delivery_risk.py       # Binary classifier + SHAP
│   ├── logistics_optimizer.py # OR-Tools Capacitated VRP
│   ├── rag.py                 # ChromaDB RAG over policy documents
│   ├── simulation.py          # What-if scenario simulation engine
│   └── unified_intelligence.py# Cross-risk compounding & enterprise severity assessment
├── ml/
│   ├── evaluation.py          # Time-based split, metrics, baselines
│   └── explainability.py      # SHAP tree explainer helpers
├── llm/
│   └── explainer.py           # Groq narration-only wrapper
├── db/
│   ├── models.py              # SQLAlchemy models (15 tables)
│   └── connection.py          # Neon Postgres engine + session
├── data_ingestion/
│   ├── base.py                # Abstract DataSource interface
│   ├── active_dataset.py      # Dynamic dataset manager & cache invalidation
│   ├── validation.py          # Schema validator, Kaggle auto-mapping, profiler
│   ├── csv_source.py          # CSV source (300 shipments, Kaggle compatibility)
│   ├── excel_source.py        # Excel source (.xlsx)
│   ├── db_source.py           # Neon DB / SQLite source
│   └── api_source.py          # API stub (extensible)
├── policies/                  # Business policy documents for RAG
├── data/                      # 300 deliveries, demand, inventory, vehicles
├── data_pipeline/             # Seed data generation + Neon DB loader
├── tests/                     # 116 tests across all modules (100% pass)
├── .streamlit/config.toml     # Streamlit dark theme + 200MB upload limit
├── pyproject.toml             # uv dependency manifest
├── requirements.txt           # pip-compatible export (for Streamlit Cloud)
└── .env.example               # Secret key template
```

---

## Team

**Bushra** (Team Leader) · **Maryam** · **Shreeya** · **Samiya**

See [`progress.md`](progress.md) for the full task board, build checklist, and session log.

---

## Key Design Rules

- **LLM Grounding Constraint**: The LLM only narrates and reasons. Every number traces to a `core/*` tool call — never hallucinated.
- **Human-in-the-loop**: No business action executes without human approval.
- **Real agent, not a pipeline**: The LLM decides which tools to call based on the situation. A pure inventory alert must not trigger route optimisation.
- **Synthetic data**: All `data/*.csv` files are clearly synthetic. Never presented as real company data.
