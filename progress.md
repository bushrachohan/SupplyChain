# SupplyChain Sentinel AI — Student Build Guide & Progress Tracker

**Last updated:** 2026-09-02
**What this file is:** A complete, self-contained handoff document. It teaches the concepts, shows the architecture, gives exact setup steps, hands off to a Claude Project for session-by-session building, tracks progress via a checklist, forces reflection via a learning log, and preempts the mistakes you will otherwise make twice. It is also the **live source of truth for a 4-person team building in parallel** (see Section 15) — anyone should be able to read this file and immediately understand what's done, what's in progress, what's blocked, and what's available to pick up next.

---

## Current Project State

*(This section must always reflect the CURRENT REAL STATE of the repository. Update it after every meaningful session — see Section 15.13. Never mark something done unless it's actually been verified and committed.)*

### Completed
- Project scope, tech stack, folder structure, ML engineering rules, RAG design, AI Decision Agent design, evaluation methodology, data ingestion strategy, and MVP prioritization — all finalized as written specification (see Sections 2–4 and 13).
- **Phase 0 — Setup:** repo initialized, uv + all dependencies installed, full folder structure created, .gitignore in place, pushed to GitHub. *(Bushra, 2026-09-02)*
- **`ml/evaluation.py`** — time-based split, leakage check, regression/classification metrics, naive + majority-class baselines, compare_to_baseline. 13 tests passing. *(Bushra, 2026-09-02)*
- **`data_ingestion/base.py` + `csv_source.py`** — abstract DataSource interface + CSV implementation. *(Maryam, 2026-09-02)*
- **`data_pipeline/generate_seed_data.py`** — synthetic seed data generator. *(Maryam, 2026-09-02)*
- **`data/historical_demand.csv`, `data/deliveries.csv`, `data/inventory_snapshot.csv`** — synthetic seed data files. *(Maryam, 2026-09-02)*
- **`core/forecasting.py`** — LightGBM demand forecasting, time-based split, leakage check, baseline comparison, feature importance, predict_demand. 12 tests passing. *(Bushra, 2026-09-02)*

### In Progress
- `core/inventory_risk.py` — Maryam (branch: to be created)
- `core/delivery_risk.py` — Samiya (branch: to be created)
- `db/models.py` + `db/connection.py` — Shreeya (branch: to be created)

### Blocked
- None.

### Next Available Tasks
- `ml/explainability.py` — depends on `core/delivery_risk.py` (Samiya's task)
- `core/logistics_optimizer.py` — depends on `data_pipeline/` ✅ (available now)
- `policies/*.md` — real business policy documents (available now, no dependencies)
- `core/rag.py` — depends on `policies/`
- `data_ingestion/excel_source.py`, `db_source.py` — depends on `db/models.py`

### Last Updated
- **Date:** 2026-09-02
- **Developer:** Bushra
- **Commit:** 2efb632 (main)

### Completed
- Project scope, tech stack, folder structure, ML engineering rules, RAG design, AI Decision Agent design, evaluation methodology, data ingestion strategy, and MVP prioritization — all finalized as written specification (see Sections 2–4 and 13). **No code has been written yet** — this is a planning-stage completion only, not an implementation completion.

### In Progress
- None yet.

### Blocked
- None yet.

### Next Available Tasks
*(Pulled from the Build Checklist, Section 10, Phase 0 — Setup. See Section 15.2 for the full live task board.)*
- Repository structure + `uv init` / initial dependency setup
- Neon Postgres database provisioning
- Groq API key setup
- Git repo init + GitHub remote + `.gitignore`
- Claude Project setup (Section 7)

### Last Updated
- **Date:** 2026-09-02
- **Developer:** — (pre-development; not yet started)
- **Commit:** — (no commits yet)

---

## Why each section matters
| Section | Why it's here |
|---|---|
| 📚 Concepts First | Embeddings, cosine similarity, RAG, Streamlit, FastAPI, Uvicorn, OR-Tools, uv, Postgres, tool-using agents, SHAP, Git — explained with analogies. Read *before* touching Claude. |
| 🏗️ Scope & Architecture | The finalized MVP scope, tech stack (with cost), folder structure, database, and data ingestion design — production-minded but realistic for one month. |
| 🤖 AI Decision Agent Design | How the agent genuinely calls tools (not a disguised pipeline), what the decision trace looks like, and the human-approval gate before any real action. |
| 📐 ML Engineering Rules | Time-based splits, no data leakage, baseline comparison, evaluation metrics, and explainability — the rules that make this a defensible ML project, not a curve-fit demo. |
| 💻 VS Code Setup | Extensions, terminal rules, `uv` environment — the local dev environment. |
| 🔑 Groq API Setup | Free LLM access, step by step. |
| 🤖 Claude Project Setup | Exact copy-paste instructions — the handoff from here on. |
| 🌿 GitHub Workflow | Exact git commands after every file. |
| 🧪 Testing Strategy | pytest for core modules and agent/tool behavior — confirming code works, not just "looking right." |
| ✅ Build Checklist | Phase by phase. Tick boxes as you go. Every phase requires confirming terminal output *and* passing tests before committing. |
| 📓 Learning Log | Forces reflection after every session. |
| ⚠️ Common Mistakes | The errors you will predictably make. |
| 🎯 Project Prioritization | What's primary MVP, secondary MVP, and Phase 2 — so scope never silently creeps. |
| 🧑‍🤝‍🧑 Team of 4 — Parallel Development | No fixed roles. How 4 people pick tasks, avoid collisions, branch, review, and keep this file as the shared source of truth. |

## How to use this with students
1. Hand them this file on Day 1.
2. Tell them to read **Section 1 (Concepts First)** before opening Claude.
3. They set up VS Code + `uv` (Section 5) and get a Groq API key (Section 6).
4. They create a Claude Project and upload this file (Section 7).
5. **If working solo:** they follow the Build Checklist (Section 10), session by session, one file at a time.
   **If working as a team of 4:** each member reads **Current Project State** (above) and **Section 15 (Team of 4 — Parallel Development Workflow)** first, then picks a TODO task from the live task board.
6. After every file: test in terminal → run pytest → confirm output → commit to GitHub (Section 8).
7. They fill in the Learning Log (Section 11) after every session — non-negotiable. Team members also fill in a Session Handoff (Section 15.3).
8. Deploy to Streamlit Cloud once the final phase is reached.

**Student flow, summarized:**
`Read concepts → Set up VS Code + uv → Get Groq API key → Create Claude Project → Upload this file → Build one file at a time → Test + run pytest → Commit to GitHub → Deploy to Streamlit Cloud`

**Team flow, summarized (4 members, no fixed roles):**
`Pull main → Read progress.md + Current Project State → Check active branches/issues → Pick an available TODO task → Mark it IN PROGRESS with your name + branch → Build on a task branch → Test → PR → Review → Merge → Update progress.md → Session Handoff`

---

## 1. Concepts First (read before touching Claude)

### Embeddings
An embedding turns a piece of text into a list of numbers (a vector) that captures its *meaning*. Think of it like GPS coordinates for meaning: "safety stock policy" and "minimum inventory buffer" land near each other in this number-space even though they share no words, because they mean similar things. We use embeddings so the system can find *relevant* policy documents, not just documents containing exact keyword matches.

### Cosine Similarity
Once two pieces of text are turned into vectors, cosine similarity measures how similar their *direction* is, regardless of length. Think of it like comparing the direction two arrows point. A score close to 1 means "very similar meaning." This is the math behind "find the most relevant policy document for this situation."

### RAG (Retrieval-Augmented Generation)
RAG = embeddings + cosine similarity + an LLM. You embed your real policy documents ahead of time, embed the current situation, find the most relevant policy snippets, and hand those to the LLM/agent to actually use — not just mention. In this project, retrieved policies must genuinely constrain the recommendation (e.g. a policy says "never let Tier-1 SKUs drop below 2 weeks of safety stock" — the agent's recommendation must respect that, not just reference it decoratively).

### Streamlit
A Python library that turns a script into a web app — no HTML/CSS/JavaScript needed. Used for the demo UI and human-approval interface, and deploys for free.

### FastAPI
A Python web framework for building APIs. Used to demonstrate proper API architecture locally, even though the *deployed* demo bypasses it (see Section 2, Deployment).

### Uvicorn
The server that *runs* your FastAPI app. You'll type `uvicorn api.main:app --reload` constantly — explained in Section 5.

### OR-Tools / VRP (Vehicle Routing Problem)
Google's free optimization library. Given delivery stops and vehicles with limited capacity, find efficient routes. We don't invent an algorithm — we correctly set up constraints and let OR-Tools solve it.

### `uv` and `pyproject.toml`
`uv` is a fast, modern Python package/environment manager that replaces `venv` + `pip` + `requirements.txt`. `pyproject.toml` declares your project's dependencies in one file; `uv.lock` is an auto-generated exact-version lockfile (like a receipt of precisely what was installed, so any teammate or the deploy server gets *identical* versions). You'll run `uv sync` instead of `pip install -r requirements.txt` — full commands in Section 5.

### Neon PostgreSQL
Postgres is a real, production-grade relational database (unlike SQLite, which is a single local file with no real concurrent-access or cloud story). Neon is a free-tier, serverless, cloud-hosted Postgres provider — you get a real persistent database with a connection string, no server to manage. We use it so the architecture is genuinely ready to hold real company data later, not just a demo file that resets.

### Tool-Using Agent (vs. a fake pipeline)
A **real** agent is given a set of tools (functions it can call) and an LLM that *decides*, based on the situation, which tools to call, in what order, and what to do with the results — this is "tool calling" or "function calling," and Groq's Llama models support it natively. This is different from a hardcoded sequence like `forecast() → risk() → optimize()` that always runs in the same fixed order regardless of the situation — that's just a pipeline wearing an "agent" label. In this project, the agent decides *which* tools are relevant to the situation in front of it (e.g. skip logistics optimization entirely if there's no delivery risk flagged), and the LLM still never computes numbers itself — it only orchestrates tool calls and narrates results.

### SHAP / Feature Importance (Explainability)
SHAP (SHapley Additive exPlanations) and simpler feature-importance scores answer "*why* did the model predict this?" — e.g., "this delivery was flagged high-risk mainly because of carrier + distance, not because of the product type." This matters because the LLM's explanation should be grounded in the model's actual reasoning, not a generic-sounding guess.

### Decision Trace
A structured, stored record of everything that happened for one decision: what data went in, what the models predicted, which policies were retrieved, which tools the agent called, what options were considered, what was recommended, whether a human approved it, and what actually happened afterward. This is what makes the system auditable — a business (or an examiner) can look at any recommendation and see exactly how it was reached.

### Human-in-the-Loop Approval
Any action with real business consequence (e.g. creating a purchase order) must be **recommended by the agent, then explicitly approved by a human** before it's considered "executed." The agent never auto-executes real actions. This is a standard, non-negotiable safety pattern for AI systems that touch real business operations.

### The LLM Grounding Constraint
The single most important engineering rule in this project: **the LLM explains, narrates, summarizes, and reasons about which tools to call — it never calculates.** All numbers (forecasts, risk scores, route costs, impact metrics) come from your ML/optimization code. If the LLM is ever computing a number itself, something is wrong.

### Git & GitHub (the basics)
Git tracks changes to your code over time; GitHub hosts a backed-up, shareable copy. The core loop: `git add` → `git commit` → `git push`. Full commands in Section 8.

---

## 2. Scope & Architecture

### What is this project?
An end-to-end AI-powered supply-chain **decision intelligence** platform. Pipeline:
`Data → Prediction → Risk Detection → Scenario Analysis → Optimization → AI Decision Agent → Recommended Action → Human Approval → Measurable Business Impact`

### Finalized MVP Scope (production-minded, still realistic for 1 month)
| # | Component | Build approach |
|---|---|---|
| 1 | Demand Forecasting | scikit-learn / LightGBM or Prophet, SKU-level, 4–12 weeks ahead; time-based split, baseline comparison (see Section 4) |
| 2 | Inventory Risk | Rule-based logic on forecast + current stock; feature importance for what's driving each risk flag |
| 3 | Logistics Optimization | OR-Tools, standard Capacitated VRP |
| 4 | Delivery Risk Prediction | Binary classifier (scikit-learn/LightGBM); SHAP or built-in feature importance |
| 5 | **AI Decision Agent** | **Genuine tool-using agent** (Groq tool/function calling) that decides which of the forecasting/inventory/delivery/optimization/RAG tools to call for a given situation — not a hardcoded sequential pipeline |
| 6 | RAG | ChromaDB + `sentence-transformers` over **real, written business/procurement/inventory policy documents** — retrieved policies must genuinely constrain the final recommendation |
| 7 | LLM | Groq API — explanation, summarization, and agent tool-selection reasoning only; never computes/invents numbers |
| 8 | Business Impact | Before/after simulation of the approved action |
| 9 | Decision Trace + Human Approval | Every recommendation is logged end-to-end and requires human approval before being marked "executed" |
| 10 | Data Ingestion Layer | Interfaces for CSV/Excel/database/API ingestion, so real company data can be plugged in later (synthetic data only powers dev/testing now) |
| 11 | Automated Tests | pytest coverage for core modules and agent/tool behavior |

**Out of scope for this MVP (see Section 13 for full prioritization):** supplier-risk monitoring, external disruption intelligence (news/weather feeds) — these are Phase 2.

### Tech Stack & Cost
| Layer | Choice | Cost |
|---|---|---|
| Environment/packages | `uv` + `pyproject.toml` + `uv.lock` | Free |
| Backend | FastAPI + Uvicorn | Free |
| ML | scikit-learn, LightGBM, Prophet/statsmodels, SHAP | Free |
| Optimization | OR-Tools | Free |
| RAG | ChromaDB + sentence-transformers | Free (local, no server) |
| Agent / LLM | Groq API (tool/function calling) | Free tier, no card required |
| Database | **Neon PostgreSQL** (serverless, free tier) | Free tier |
| Testing | pytest | Free |
| Frontend/Deploy | Streamlit Community Cloud | Free tier |
| IDE | VS Code | Free |
| Version control | GitHub | Free |
| **Total cost** | | **$0** |

### Folder Structure
```
supplychain-sentinel-ai/
├── core/                        # domain logic — no FastAPI/Streamlit/agent imports here
│   ├── forecasting.py
│   ├── inventory_risk.py
│   ├── delivery_risk.py
│   ├── logistics_optimizer.py
│   └── rag.py
├── ml/
│   ├── evaluation.py             # time-based split, leakage checks, baseline comparison, metrics
│   └── explainability.py         # SHAP / feature importance helpers
├── agent/
│   ├── tools.py                  # tool definitions/wrappers around core/* functions, exposed to the LLM
│   ├── orchestrator.py           # the real tool-using agent (Groq tool calling loop)
│   └── decision_trace.py         # builds and persists the input→...→outcome trace
├── llm/
│   └── explainer.py              # Groq API wrapper — narration/summarization only
├── data_ingestion/                # pluggable data source interfaces
│   ├── base.py                   # abstract DataSource interface
│   ├── csv_source.py
│   ├── excel_source.py
│   ├── db_source.py              # reads from Neon Postgres
│   └── api_source.py             # stub for future real company API ingestion
├── db/
│   ├── models.py                  # SQLAlchemy models (Postgres/Neon)
│   └── connection.py
├── policies/                      # real business/procurement/inventory policy docs (markdown)
├── api/
│   └── main.py                    # FastAPI app — routes call agent/core (local dev/testing)
├── app.py                         # Streamlit app — human-approval UI, calls agent/core directly (this is what deploys)
├── data_pipeline/                 # loads synthetic/dev data into Neon Postgres
├── data/                          # synthetic seed data — DEV/TEST ONLY, never treated as production data
├── tests/
│   ├── test_forecasting.py
│   ├── test_inventory_risk.py
│   ├── test_delivery_risk.py
│   ├── test_logistics_optimizer.py
│   ├── test_rag.py
│   ├── test_agent_tools.py
│   └── test_decision_trace.py
├── pyproject.toml
├── uv.lock
├── .env                            # local secrets (Neon connection string, Groq key) — NEVER committed
├── .gitignore
└── README.md
```

### Deployment Architecture (recap)
Streamlit Community Cloud only runs one process — it can't also host a separate FastAPI server. So: `core/`, `agent/`, `ml/`, `llm/`, and `data_ingestion/` hold all logic with zero web-framework dependencies. FastAPI (`api/main.py`) imports from these for local dev/testing. Streamlit (`app.py`) *also* imports from them directly — that's what actually runs in production. One codebase, two front doors, nothing duplicated.

**Known caveats:** Neon Postgres is persistent (unlike the old SQLite-on-ephemeral-disk setup), so data survives redeploys — this is one of the reasons for the switch. ChromaDB's local index still needs rebuilding on cold start unless persisted separately. Groq API key and Neon connection string go in Streamlit's Secrets manager, never hardcoded.

### Database Schema (Postgres/Neon, draft)
`skus`, `historical_demand`, `inventory_snapshots`, `forecast_results`, `inventory_risk`, `deliveries`, `delivery_risk_predictions`, `vehicles`, `routes`/`route_stops`, `policies`, `recommendations`, `impact_simulations`, **`decision_traces`** (see Section 3), **`approvals`** (human-in-the-loop decisions)

### Data Ingestion Strategy — designed for real data, not just synthetic
The data layer is built behind a `DataSource` interface (`data_ingestion/base.py`) with methods like `load_historical_demand()`, `load_inventory_snapshot()`, `load_deliveries()`. Each concrete source (`csv_source.py`, `excel_source.py`, `db_source.py`, `api_source.py`) implements the same interface.
- **CSV** is the main MVP working source — this is what development and testing are actually run against.
- **Excel** and **Neon DB** sources have working sample implementations (real, not empty stubs) exercised with small sample inputs, so the interface is proven but not the primary path.
- **API** source is an extensible interface/example only — it demonstrates the shape a future real company API integration would take, and is **not** a production connector.

This means plugging in a real company's data later means writing one new implementation of the interface, not rearchitecting the ML/agent layers.

### Evaluation Methodology
| Component | Metric |
|---|---|
| Forecasting | MAPE / RMSE on a **time-based holdout window**, compared against a naive baseline (see Section 4) |
| Delivery risk | AUC / precision-recall, compared against a majority-class baseline |
| Inventory risk | Precision/recall vs. simulated ground-truth stockouts |
| Logistics optimization | % cost/distance reduction vs. naive routing |
| Agent + business impact | Before/after KPI deltas (headline demo number) |

---

## 3. AI Decision Agent Design (genuine tool-using agent)

This section exists because "AI agent" is the most commonly faked component in student projects — it's easy to hardcode a sequence of function calls and call it an agent. Here's what makes ours real, and how it stays buildable in a month.

### Tools exposed to the agent (`agent/tools.py`)
Each tool is a thin wrapper around a `core/*` function, with a clear name, description, and input/output schema — this is what the LLM sees when deciding what to call:
- `get_demand_forecast(sku_id)` → wraps `core/forecasting.py`
- `get_inventory_risk(sku_id)` → wraps `core/inventory_risk.py`
- `get_delivery_risk(delivery_id)` → wraps `core/delivery_risk.py`
- `optimize_routes(delivery_ids, vehicle_constraints)` → wraps `core/logistics_optimizer.py`
- `retrieve_policies(query)` → wraps `core/rag.py`

### How the agent loop works (`agent/orchestrator.py`)
1. The agent receives a situation (e.g. "SKU X inventory looks low, 3 deliveries are flagged").
2. The Groq LLM, given the tool list and the situation, **decides which tool(s) to call** — it does not follow a fixed hardcoded order. For a pure logistics issue with no inventory concern, it may skip forecasting/inventory tools entirely.
3. Each tool call returns real, code-computed data (never LLM-invented).
4. The agent may call `retrieve_policies()` and must apply what comes back — e.g., if a policy caps overtime shipping cost, that constraint has to show up in which options are considered feasible.
5. Once enough tool results are gathered, the code (not the LLM) assembles a structured **options table** (each option with its concrete predicted numbers and which policies it satisfies/violates).
6. The LLM is given that options table and asked only to **narrate and justify** the recommended option in plain English, citing the relevant policy.
7. The recommendation + full trace is written to `decision_traces` (Section above) and surfaced to a human for approval — nothing is auto-executed.

### Why this satisfies both requirements at once
"Genuine tool-calling agent" and "LLM never computes numbers" are not in tension: the LLM's job is *deciding which tools to call and narrating results*, never *doing the arithmetic*. Every number in the final recommendation traces back to a tool call, and every tool call traces back to `core/*` code.

### Decision Trace schema (`decision_trace.py` / `decision_traces` table)
```
trace_id
timestamp
inputs               # situation description, relevant SKU/delivery IDs
predictions           # forecast values, risk scores, route costs — as returned by tools
policies_retrieved    # which policy documents/snippets were retrieved and used
tools_used            # ordered list of tool calls made, with arguments and results
options_considered     # structured table of candidate actions with their tradeoffs
recommendation         # the agent's chosen option + LLM narration/justification
human_approval         # status (pending/approved/rejected), approver, timestamp, notes
outcome                # post-action result / simulated business impact, filled in after approval
```

### Human-in-the-Loop Approval Gate
Any recommendation that implies a real action (create a purchase order, reroute a delivery, expedite shipping) is written to `decision_traces` with `human_approval.status = "pending"` and surfaced in the Streamlit UI with **Approve** / **Reject** buttons. Only on approval does the system simulate/mark the action as executed and populate `outcome`. The agent never calls a "create purchase order" tool that actually executes anything — for the MVP, "execution" is simulated (its business-impact effect is calculated), and the gate is a real, working control, not a UI decoration.

---

## 4. ML Engineering Rules

These apply to every predictive model in the project (forecasting, delivery risk, and any inventory-risk ML if used beyond rules).

### Time-based train/validation/test split
Never randomly shuffle time-series data into train/test. Split strictly by time: train on the earliest period, validate on the next period, test on the most recent period. This mirrors how the model will actually be used (predicting the future from the past).

### No data leakage
No feature may be computed using information that wouldn't have been available at prediction time. Common leakage traps to check explicitly: rolling averages/aggregates computed over a window that includes future dates, using a delivery's actual outcome to help predict its own risk, or joining tables in a way that pulls in later-dated records.

### Baseline comparison (mandatory, not optional)
Every model must be compared against a simple, explainable baseline before it's considered "done":
- Forecasting baseline: naive forecast (last observed value) or seasonal naive (same period last cycle)
- Delivery risk baseline: majority-class predictor / simple rule (e.g. "flag if past deliveries to this carrier were late")
If your trained model doesn't clearly beat the baseline on the test set, that's a real finding to report, not a failure to hide — and it changes what you can honestly claim in the demo.

### Evaluation metrics (see Section 2 table)
Report metrics on the **test** split only — validation metrics are for model selection/tuning, not final claims.

### Explainability
- Forecasting: report which features (seasonality, recent trend, promotions if modeled) drive predictions, using the model's built-in feature importance where available (e.g. LightGBM).
- Delivery risk classifier: use SHAP (or built-in feature importance if SHAP proves too heavy for the timeline) to identify which features drove each high-risk flag.
- This output feeds directly into the LLM's explanation step (Section 3) so explanations are grounded in the model's actual reasoning, not a plausible-sounding guess.

---

## 5. VS Code Setup

### Extensions to install
- **Python** (Microsoft) — core language support, linting, debugging
- **Pylance** — fast type-checking and IntelliSense
- **Jupyter** (optional, for prototyping models before moving to `.py` files)
- **GitLens** — see git history/blame inline
- **Even Better TOML** — syntax highlighting for `pyproject.toml`
- **DotENV** — syntax highlighting for `.env`

### Environment setup with `uv`
Install `uv` once (see uv's official install instructions for your OS), then in the project root:
```
uv init
```
This creates `pyproject.toml`. Add dependencies as you need them, e.g.:
```
uv add fastapi uvicorn streamlit scikit-learn lightgbm chromadb sentence-transformers ortools groq sqlalchemy psycopg2-binary shap pytest python-dotenv
```
This updates `pyproject.toml` **and** `uv.lock` automatically. To install everything from an existing lockfile (e.g. after cloning the repo):
```
uv sync
```
Run any script or tool inside the managed environment with:
```
uv run python core/forecasting.py
uv run pytest
uv run uvicorn api.main:app --reload
uv run streamlit run app.py
```
No manual `venv` activation needed — `uv run` handles it. `uv` creates a `.venv/` folder automatically; it's listed in `.gitignore` (Section 8) just like the old `venv/` was.

### Integrated terminal rules — read this before you type anything
1. **Never chain commands with `&&`.** On Windows PowerShell this silently breaks or behaves inconsistently, and it hides *which* command actually failed. Run one command, read its output, then run the next.
2. **Prefix Python/tool commands with `uv run`** so you're always in the managed environment — no separate activation step to forget.
3. **One terminal tab per long-running process.** Keep Uvicorn (or Streamlit) running in one tab; use a separate tab for git commands / `uv add`.
4. **Read the actual error, top to bottom, before asking Claude about it.** Often the real error is the *first* line, not the last.

---

## 6. Groq API Setup (free LLM + tool calling)

1. Go to **console.groq.com**.
2. Sign up (free, no credit card required).
3. Navigate to **API Keys** in the left sidebar.
4. Click **Create API Key**, name it (e.g. `supplychain-sentinel-dev`), copy it immediately — it's only shown once.
5. Locally: create a `.env` file in the project root (never commit this — see `.gitignore` in Section 8):
   ```
   GROQ_API_KEY=your_key_here
   NEON_DATABASE_URL=your_neon_connection_string_here
   ```
6. In `llm/explainer.py` and `agent/orchestrator.py`, load it with `python-dotenv`:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   api_key = os.getenv("GROQ_API_KEY")
   ```
7. Use a Groq model that supports **tool/function calling** (check Groq's current model list at console.groq.com for the latest tool-calling-capable model) — this is required for the real agent design in Section 3, not just plain chat completion.
8. For the deployed app: add the same keys in **Streamlit Cloud → App settings → Secrets**, and read them via `st.secrets["GROQ_API_KEY"]` / `st.secrets["NEON_DATABASE_URL"]` instead of `.env`.

---

## 7. Claude Project Setup — the handoff

This is where responsibility shifts from "your mentor explains everything" to "you build session by session with Claude as your pair programmer." Follow these steps exactly:

1. Go to claude.ai → **Projects** → **Create Project**.
2. Name it: `SupplyChain Sentinel AI`.
3. Upload this file (`progress.md`) into the Project's knowledge/files.
4. Paste the following into the Project's **custom instructions** field:

   ```
   You are my AI/ML mentor, software architect, backend engineer, data scientist,
   and AI-agent engineer for my capstone project "SupplyChain Sentinel AI."

   Read progress.md (uploaded to this project) as the single source of truth for
   scope, architecture, tech stack, and current progress before answering anything.

   Rules:
   - Build incrementally, one file/component at a time. Never generate the whole
     project at once.
   - Before writing code, tell me which file we're building and why, tied to the
     Build Checklist in progress.md.
   - After giving me a file, tell me exactly how to test it in the terminal
     (including relevant pytest commands) and what output confirms it's working,
     before I move to the next file.
   - If I propose something unnecessary, overly complex, or risky for a 1-month
     timeline, tell me clearly and suggest a simpler alternative.
   - The AI Decision Agent must be a genuine tool-calling agent (Groq tool/function
     calling) that decides which tools to invoke based on the situation. Never
     implement it as a hardcoded sequential pipeline disguised as an agent.
   - The LLM layer must never invent or calculate numerical predictions, risks,
     costs, or optimization results — it only explains, summarizes, and reasons
     about which tools to call.
   - RAG must use real, written business/procurement/inventory policies, and
     retrieved policies must actually constrain the recommendation, not just be
     mentioned.
   - Any ML model must use a time-based train/validation/test split, must be
     checked for data leakage, and must be compared against a simple baseline
     before being considered done.
   - Any action with real business consequence must go through a human-approval
     gate before being marked as executed — never auto-execute.
   - Use `uv` (not pip/venv) and pytest for all environment and testing commands.
   - Never use `&&` in terminal commands — one command at a time.
   - After we finish a file, remind me to update progress.md's Build Checklist
     and Learning Log, and to commit to GitHub using the workflow in progress.md.
   ```

5. Start a new conversation inside the Project and say: *"Let's start Phase 0 (Setup) from the Build Checklist."*
6. Every future session: open the Project (not a fresh unrelated chat), so the file context persists.

---

## 8. GitHub Workflow

### One-time setup
```
git init
```
Create `.gitignore` in the project root with at least:
```
.venv/
.env
__pycache__/
*.pyc
.DS_Store
.streamlit/secrets.toml
chroma_db/
.pytest_cache/
```
Then:
```
git add .
git commit -m "Initial commit: project structure"
```
Create the repo on GitHub (empty, no README/license — you already have files locally), then:
```
git remote add origin https://github.com/your-username/supplychain-sentinel-ai.git
git branch -M main
git push -u origin main
```

### After every file you build (the loop you'll repeat constantly)
1. Test the file in the terminal — confirm the expected output.
2. Run `uv run pytest` — confirm all relevant tests pass.
3. `git add <filename>` (or `git add .` if multiple related files changed)
4. `git commit -m "Add: <short description of what this file does>"`
5. `git push`

**Commit message convention:** `Add: ...` for new files, `Fix: ...` for bug fixes, `Update: ...` for changes to existing logic. Small, frequent, descriptive commits — not one giant commit at the end of the week.

---

## 9. Testing Strategy (pytest)

Every `core/`, `ml/`, and `agent/` module needs a corresponding test file in `tests/`. Minimum expectations:

- **`core/forecasting.py`** — on a small known sample, output has the right shape/columns and reasonable value ranges; baseline comparison logic runs and returns both model and baseline metrics.
- **`core/inventory_risk.py`** — known input (e.g. stock=10, forecast demand=5/week) produces the expected days-remaining and correct risk flag.
- **`core/delivery_risk.py`** — model outputs are valid probabilities (0–1); baseline comparison present.
- **`core/logistics_optimizer.py`** — solution respects vehicle capacity constraints on a small hand-built test case.
- **`core/rag.py`** — a query about safety stock retrieves the safety-stock policy document (relevance check on known content, not just "returns something").
- **`agent/tools.py`** — each tool function returns the correct schema for a given input.
- **`agent/orchestrator.py`** — for a scenario with no delivery risk, confirm the agent does *not* call `optimize_routes`; for a scenario with a flagged high-risk delivery, confirm it does. This is the test that actually proves it's a real agent, not a fixed pipeline.
- **`agent/decision_trace.py`** — a completed run produces a trace with all required fields populated; `human_approval.status` starts as `"pending"` and only changes via an explicit approval call.

Run all tests with:
```
uv run pytest
```
**No file is committed without its tests passing.**

---

## 10. Build Checklist

Every phase requires **confirming terminal output and passing tests before committing** — don't commit code you haven't actually run and tested.

### Phase 0 — Setup
- [ ] VS Code + extensions installed
- [ ] `uv init` run, `pyproject.toml` created
- [ ] Initial dependencies added via `uv add ...`, `uv.lock` generated
- [ ] Groq API key obtained, Neon Postgres database created, both stored in `.env`
- [ ] Folder structure created (`core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/`, `db/`, `policies/`, `api/`, `tests/`, `data/`)
- [ ] Git repo initialized, `.gitignore` in place, first commit pushed to GitHub
- [ ] Claude Project created, this file uploaded, custom instructions pasted
- [ ] **Confirm:** `git log` shows initial commit; `git remote -v` shows GitHub origin; `uv run python -c "print('ok')"` runs cleanly

### Phase 1 — Data Layer & Core ML Logic
- [ ] `data_ingestion/base.py` — abstract `DataSource` interface defined
- [ ] `data_ingestion/csv_source.py` — synthetic dataset loaded via this interface (dev/test only)
- [ ] `data_ingestion/excel_source.py`, `db_source.py` — working sample implementations (small sample inputs)
- [ ] `data_ingestion/api_source.py` — extensible interface/example only (not a production connector)
- [ ] `db/models.py`, `db/connection.py` — Neon Postgres schema created and connected
- [ ] `data_pipeline/` scripts: source data → Neon Postgres
- [ ] `core/forecasting.py` — demand forecasting model, time-based split, baseline comparison, tested standalone
- [ ] `core/inventory_risk.py` — stockout/overstock logic, tested standalone
- [ ] `core/delivery_risk.py` — delivery risk classifier, time-based split, baseline comparison, tested standalone
- [ ] `core/logistics_optimizer.py` — OR-Tools VRP, tested standalone
- [ ] `ml/evaluation.py` — split/leakage-check/baseline-comparison utilities, used by the above
- [ ] `ml/explainability.py` — SHAP/feature importance for delivery risk (and forecasting where practical)
- [ ] `tests/test_*.py` for each module above — passing
- [ ] **Confirm:** each module runs independently, terminal output shows expected results, `uv run pytest` is green, before committing

### Phase 2 — RAG, Agent, and Decision Trace
- [ ] Real business/procurement/inventory policy documents written (markdown) and placed in `policies/`
- [ ] `core/rag.py` — ChromaDB + sentence-transformers embedding + retrieval, tested standalone with real policy queries
- [ ] `llm/explainer.py` — Groq API call, tested standalone with a hardcoded example (confirm no invented numbers)
- [ ] `agent/tools.py` — tool wrappers around `core/*`, with schemas
- [ ] `agent/orchestrator.py` — real Groq tool-calling agent loop, tested for at least two different scenarios that call *different* tool subsets
- [ ] `agent/decision_trace.py` — trace built and persisted to `decision_traces` table
- [ ] `tests/test_rag.py`, `test_agent_tools.py`, `test_decision_trace.py` — passing
- [ ] **Confirm:** orchestrator run end-to-end from the terminal produces a full trace (inputs → predictions → policies → tools used → options → recommendation) for at least two distinct test scenarios

### Phase 3 — Human-in-the-Loop UI
- [ ] `api/main.py` — FastAPI endpoints wired to `agent/`/`core/`, tested locally via `uv run uvicorn api.main:app --reload` and the `/docs` page
- [ ] `app.py` — Streamlit dashboard: shows pending recommendations with full decision trace, **Approve/Reject** buttons, and business-impact simulation after approval
- [ ] **Confirm:** both the FastAPI docs page and the Streamlit dashboard show correct results for the same test case; rejecting a recommendation does not mark it executed; approving does

### Phase 4 — Deploy
- [ ] `pyproject.toml` / `uv.lock` finalized and confirmed to install cleanly via `uv sync` in a fresh clone
- [ ] Repo pushed to GitHub, up to date
- [ ] Neon Postgres production database confirmed reachable from the deploy environment
- [ ] Streamlit Cloud app created, connected to repo, entry point set to `app.py`
- [ ] `GROQ_API_KEY` and `NEON_DATABASE_URL` added to Streamlit Cloud Secrets
- [ ] Startup logic confirmed working (ChromaDB index rebuild on cold start if needed; Neon connection tested)
- [ ] Full `uv run pytest` suite passing before final deploy
- [ ] **Confirm:** deployed app loads, runs a full demo scenario end-to-end including human approval, matches local behavior

---

## 11. Learning Log

Fill this in **after every session** — non-negotiable. Copy the template below for each entry.

```
### Session: [date]
**What I built:** 
**What broke (and how I fixed it, or didn't yet):** 
**What I actually learned (not just "it works now"):** 
**Questions for next session:** 
```

---

## 12. Common Mistakes (read before you make them)

- **Chaining commands with `&&`** — breaks silently on Windows PowerShell. One command at a time.
- **Committing `.env`, `.venv/`, or database credentials to GitHub** — check `.gitignore` is in place *before* your first commit.
- **Letting the LLM "help" by generating a number** (a forecast, a cost, a risk score) instead of only narrating one you computed — always check the LLM's output doesn't contain a figure that isn't in its input/tool results.
- **Building a hardcoded pipeline and calling it an agent** — if your "agent" always calls every tool in the same fixed order regardless of the situation, it's not a tool-using agent. Test with scenarios that should skip tools.
- **Random train/test splits on time-series data** — always split by time, never shuffle.
- **Skipping the baseline comparison** because the trained model "obviously" works better — measure it, don't assume it.
- **Letting the agent auto-execute a real action** (e.g. a purchase order) without human approval — the approval gate is a hard requirement, not optional polish.
- **Skipping standalone testing** and jumping straight to integrating a new module into the agent — if it breaks, you won't know which of the 5 things you just wired together is the problem.
- **Building the whole project in one Claude session** instead of one file/phase at a time.
- **Treating the synthetic dataset as if it were real company data** in any claim you make about results — be explicit that it's dev/test data.
- **Forgetting to run `uv add` when you import a new package** — if it's not in `pyproject.toml`, a fresh clone/deploy will fail.
- **Committing code with failing tests** — tests must pass before every commit, not "mostly pass."

---

## 13. Project Prioritization (keep scope disciplined)

| Priority | Project | Status |
|---|---|---|
| **Primary MVP** | Project 17 — Inventory Forecasting (demand forecasting + inventory risk + replenishment) | In scope now |
| **Secondary MVP** | Project 18 — Logistics/Delivery (delivery risk prediction + route optimization) | In scope now, built after primary MVP is solid |
| **Phase 2 (later)** | Project 10 — Supplier-Risk Monitoring & external disruption intelligence | Explicitly out of scope for the 1-month MVP |

**Discipline rule:** the AI Decision Agent, RAG, decision trace, and human-approval layers are built to serve Project 17 first, then extended to cover Project 18. Project 10 is not touched until both are working end-to-end and deployed. If a build session starts drifting toward Project 10 features, stop and re-check this table.

---

## 14. Student Flow (quick reference)

1. Read Concepts (Section 1)
2. Set up VS Code + `uv` (Section 5)
3. Get Groq API key + Neon Postgres (Section 6)
4. Create Claude Project + upload this file (Section 7)
5. Build one file at a time (Section 10, Build Checklist)
6. Test in terminal + run `uv run pytest` — confirm output
7. Commit to GitHub (Section 8)
8. Fill in Learning Log (Section 11) after each session
9. Deploy to Streamlit Cloud (Phase 4)

---

## 15. Team of 4 — Parallel Development Workflow

This is a 4-person team. **All members may work simultaneously. There are no permanent roles.** Members choose tasks dynamically from the current Build Checklist (Section 10) and the live task board / GitHub issues below — a member may work on ML, backend, data, agent, RAG, UI, testing, deployment, or documentation depending on what's currently available and what someone else is already doing. The priority is maximum parallel progress with minimum duplicated work and minimum merge conflicts.

Nothing in Sections 1–14 (scope, architecture, ML rules, RAG design, agent design, evaluation methodology, MVP prioritization) changes because of this section — this section only adds *how the team coordinates* around that existing plan.

### 15.0 Team

- **Team Leader:** Bushra
- **Members:** Maryam, Shreeya, Samiya
- **Shared GitHub repository:** https://github.com/bushrachohan/SupplyChain

All members work against this same shared repository. Each member's local folder/clone path is machine-specific and is **not** recorded in `progress.md` — only branch names, commits, and task status belong here (see Section 15.2–15.4).

### 15.1 Task Ownership Rule

Before starting a task, a member must:
1. Read the latest `progress.md` (especially **Current Project State**, above).
2. Check the GitHub repository for active branches/issues/PRs.
3. Choose a task marked **TODO** and available (no unresolved dependency).
4. Mark the task **IN PROGRESS** in the live task board (Section 15.2).
5. Add their name/identifier and branch name.
6. Confirm the task's dependencies are actually finished (see the Dependency column).
7. Start implementation only after confirming it does not duplicate another active task.

**Ownership is per TASK, not per DOMAIN.** No one reserves "all of ML" or "all of the frontend" permanently. Example:
```
Task: core/forecasting.py
Status: IN PROGRESS — <developer name> — feature/forecasting
```
Another member must not independently implement the same task unless explicitly coordinated (e.g. <developer name> is blocked and hands it off).

### 15.2 Task Status System — Live Task Board

Every meaningful task has one of: **TODO · IN PROGRESS · BLOCKED · REVIEW · DONE**. Update the status the moment it changes — this board (derived from the Build Checklist, Section 10) is what lets a teammate see, at a glance, what's safe to pick up.

**Phase 0 — Setup**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| Repo structure + `uv init` | TODO | — | — | — |
| Neon Postgres provisioning | TODO | — | — | — |
| Groq API key setup | TODO | — | — | — |
| Claude Project setup | TODO | — | — | — |

**Phase 1 — Data Layer & Core ML Logic**
| Task | Status | Developer | Branch | Dependency |
|---|---|---|---|---|
| `data_ingestion/base.py` + `csv_source.py` | TODO | — | — | repo structure |
| `data_ingestion/excel_source.py`, `db_source.py` (working sample implementations) | TODO | — | — | `base.py` |
| `data_ingestion/api_source.py` (extensible interface/example, not production) | TODO | — | — | `base.py` |
| `db/models.py`, `db/connection.py` | TODO | — | — | Neon provisioning |
| `data_pipeline/` (load data → Neon) | TODO | — | — | `db/models.py` |
| `core/forecasting.py` | TODO | — | — | `data_pipeline/` |
| `core/inventory_risk.py` | TODO | — | — | `forecasting.py` |
| `core/delivery_risk.py` | TODO | — | — | `data_pipeline/` |
| `core/logistics_optimizer.py` | TODO | — | — | `data_pipeline/` |
| `ml/evaluation.py` | TODO | — | — | — |
| `ml/explainability.py` | TODO | — | — | `delivery_risk.py` |
| Tests for all of the above | TODO | — | — | respective modules |

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

### 15.3 Session Handoff

After every meaningful development session, update the project state with an entry like this (append new entries, don't overwrite old ones — this becomes a running log):

```
## Session Handoff

Date:
Developer:
Branch:
Task:
Status:

What was completed:
Files created/modified:
Tests run:
Test results:
Commit:
Known issues:
Blocked by:
Recommended next task:
```
The purpose: another team member can continue from exactly where the previous one stopped, without a sync call.

### 15.4 GitHub Branching

`main` = stable, tested, demo-ready branch. **Never develop directly on `main`.** Each task gets its own branch, named for the task, not the person:
```
feature/forecasting
feature/inventory-risk
feature/delivery-risk
feature/route-optimizer
feature/rag
feature/agent-tools
feature/decision-trace
feature/dashboard
```
Workflow: (1) pull latest `main` → (2) create a focused task branch → (3) implement one coherent task → (4) run relevant tests → (5) update `progress.md`/task status → (6) commit → (7) push branch → (8) open a Pull Request → (9) review/test → (10) merge only after tests pass. No large unreviewed merges.

### 15.5 Parallel Development

Independent workstreams proceed at the same time whenever interfaces/contracts are already defined (Section 15.7):
- One member works on forecasting while another builds route optimization.
- One member works on RAG while another builds database models.
- One member builds the Streamlit UI against an agreed mock interface while another builds the real backend behind it.
- One member writes tests while another implements the feature.

**If two tasks would modify the same shared file, coordinate before editing** — see Section 15.6.

### 15.6 Shared / High-Conflict Files

Treat these as shared/high-conflict — do not casually modify them from multiple branches at the same time:
- `progress.md`
- `pyproject.toml`
- `uv.lock`
- Database schema (`db/models.py`)
- API contracts (`api/main.py` route signatures, `agent/tools.py` tool schemas)
- Shared configuration
- Core interfaces (`data_ingestion/base.py`)

When a shared file must change: (1) coordinate with the team, (2) make the smallest required change, (3) explain the change, (4) run relevant tests, (5) update `progress.md`.

### 15.7 Interface-First Development

Parallel development depends on stable interfaces. Before implementing components that depend on each other, define: function name, inputs, output schema, types, errors, and expected behavior. Example — `get_demand_forecast(sku_id)` must have a known input/output schema *before* the AI Decision Agent depends on it. This lets one member implement the consumer while another implements the provider. Use mocks/stubs only temporarily when needed for parallel work, and replace them with the real implementation before integration.

### 15.8 Integration Rule

Integration happens frequently — don't wait until the final week to merge everything. Recommended cycle:
```
Individual task → local tests → Pull Request → review → integration → full test suite → main
```
Tag a stable version after major milestones: `v0.1-foundation`, `v0.2-ml`, `v0.3-agent`, `v0.4-mvp`.

### 15.9 progress.md Is the Handoff Source of Truth

`progress.md` must always describe the **current real state** of the repository:
- After a feature is completed and verified → mark it **DONE**, record developer, branch/commit, tests, and update Current Project State (top of this file).
- If partially completed → mark **IN PROGRESS**, record what remains.
- If blocked → mark **BLOCKED**, explain the dependency/reason.

**Never mark a feature complete merely because code was written.** It's DONE only when the Definition of Done (15.10) is satisfied.

### 15.10 Definition of Done

A task is DONE only when **all** of the following are true:
1. Code is implemented.
2. Real test input has been used.
3. Relevant automated tests pass (Section 9).
4. Errors/invalid inputs are handled.
5. Output is correct and explainable where applicable.
6. Existing functionality still works (no regressions).
7. `progress.md` is updated (task status + Current Project State).
8. Changes are committed and pushed.
9. Pull Request is merged successfully.

### 15.11 ML Integrity

Never modify datasets, features, thresholds, or models merely to make metrics look better. All reported ML and business metrics must come from reproducible experiments using the evaluation methodology already defined in Section 4. Synthetic data must always be identified as synthetic — never presented as if it were real company data (this reinforces the rule already stated in Section 2's Data Ingestion Strategy).

### 15.12 One-Month Scope Control (Team Version)

Priorities are unchanged from Section 13:
- **PRIMARY:** Project 17 — Inventory Forecasting / Stockout Prevention
- **SECONDARY:** Project 18 — Logistics / Delivery Risk / Route Optimization
- **FUTURE (Phase 2):** Project 10 — Supplier Risk Monitoring / External Disruption Intelligence

No team member should begin Phase 2 supplier-risk features merely because they're interesting if the primary MVP is incomplete. If anyone proposes a new feature, it must be classified as **MVP**, **Phase 2**, or **Phase 3** before implementation — check it against Section 13's table first.

### 15.13 Current State Update Protocol

At the end of **every** meaningful Claude/AI coding session:
1. Verify the work.
2. Run relevant tests.
3. Update `progress.md`.
4. Update **Current Project State** (top of this file).
5. Update the **Build Checklist** (Section 10) and **live task board** (Section 15.2).
6. Add a **Session Handoff** entry (Section 15.3).
7. Record branch and commit.
8. Identify the next available tasks.

When a new team member starts (or an existing member starts a new session), their first action must be:
1. Pull latest `main`.
2. Read `progress.md`.
3. Check **Current Project State**.
4. Check active branches/PRs/issues on GitHub.
5. Choose an available TODO task.
6. Update its status to IN PROGRESS (Section 15.2), with name and branch.
7. Begin work.

### 15.14 AI Coding Agent Rule

This project may be developed using Claude, Google Antigravity, or another AI coding assistant. The assistant must:
- Read `progress.md` before making architectural changes.
- Treat `progress.md` as the project source of truth.
- Never silently change architecture.
- Never silently expand scope (check Section 15.12 / Section 13 before adding anything new).
- Preserve existing working functionality.
- Run tests after relevant changes.
- Never expose or commit secrets.
- Avoid destructive operations unless explicitly approved.
- Update `progress.md` after meaningful work.
- Report exactly what was changed and verified.

### 15.15 Claude Account Handoff

Members may use different Claude accounts/Projects, so:
- **GitHub is the authoritative source of project state** — not any individual's Claude Project.
- Each member may use a different Claude account/Claude Project.
- Before starting a session, pull the latest state from GitHub and read the latest `progress.md` on `main`.
- If the local Claude Project's copy of `progress.md` differs from the latest verified GitHub version, **the latest verified GitHub version always takes priority.**

### 15.16 progress.md Merge Rule

To reduce merge conflicts on `progress.md` (see also Section 15.6):
- Do not overwrite newer progress with an older branch's copy of `progress.md`.
- Synchronize `progress.md` with the latest `main` before merging.
- Resolve `progress.md` conflicts carefully — merge the actual status/content changes rather than blindly accepting one side.
