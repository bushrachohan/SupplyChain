# SupplyChain Sentinel AI — Student Build Guide & Progress Tracker

**Last updated:** 2026-09-02
**What this file is:** A complete, self-contained handoff document. It teaches the concepts, shows the architecture, gives exact setup steps, hands off to a Claude Project for session-by-session building, tracks progress via a checklist, forces reflection via a learning log, and preempts the mistakes you will otherwise make twice. It is also the **live source of truth for a 4-person team building in parallel** (see Section 15) — anyone should be able to read this file and immediately understand what's done, what's in progress, what's blocked, and what's available to pick up next.

---

## Current Project State

*(This section reflects the CURRENT REAL STATE of the shared repository. It is updated after work is verified and merged. Do not mark unmerged work as completed.)*

### Completed
- Project scope, architecture, MVP prioritization, ML engineering rules, RAG design, AI Decision Agent design, evaluation methodology, and data-ingestion strategy finalized.
- Phase 0 setup completed: repository, `uv`, dependencies, folder structure, `.gitignore`, and GitHub setup.
- `ml/evaluation.py` completed with time-based split, leakage checks, metrics, naive/majority baselines, and comparison utilities.
- Data ingestion layer completed: `data_ingestion/base.py`, `csv_source.py`, `excel_source.py`, `db_source.py`, `api_source.py`.
- Synthetic seed data generator and seed CSV datasets completed.
- Business/procurement/logistics policy documents for RAG completed.
- `core/forecasting.py` completed with LightGBM forecasting, time-based evaluation, baseline comparison, leakage checks, feature importance, and tests.
- Completed work is available in the shared GitHub repository and should be pulled from `main`.

### Currently In Progress
- `core/inventory_risk.py`
- `db/models.py` + `db/connection.py`

*(Task ownership is coordinated in WhatsApp/team chat. No permanent roles are assigned in `progress.md`.)*

### Blocked
- None.

### Next Available Tasks
- `core/rag.py` — policies are already available.
- `llm/explainer.py` — Groq setup is already available.
- `core/delivery_risk.py` — available once its dependency requirements are satisfied.
- `core/logistics_optimizer.py` — available once its data-pipeline dependency is satisfied.
- `data_pipeline/` — available after the database layer is ready.

### How Task Selection Works
The team chooses the next task through WhatsApp/team chat based on the current repository state.

Only selected active tasks are marked **IN PROGRESS** in the task board. All other unfinished tasks remain **TODO**.

Developer names and local folder paths are intentionally not stored in the shared task board. GitHub branches/PRs and WhatsApp coordination identify who is working on a task.

### Last Updated
- Update this section after a task PR is merged and verified.


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

supplychain-sentinel-ai/
├── core/
│ ├── forecasting.py
│ ├── inventory_risk.py
│ ├── delivery_risk.py
│ ├── logistics_optimizer.py
│ └── rag.py
├── ml/
│ ├── evaluation.py
│ └── explainability.py
├── agent/
│ ├── tools.py
│ ├── orchestrator.py
│ └── decision_trace.py
├── llm/
│ └── explainer.py
├── data_ingestion/
│ ├── base.py
│ ├── csv_source.py
│ ├── excel_source.py
│ ├── db_source.py
│ └── api_source.py
├── db/
│ ├── models.py
│ └── connection.py
├── policies/
├── api/
│ └── main.py
├── app.py
├── data_pipeline/
├── data/
├── tests/
├── pyproject.toml
├── uv.lock
├── .env
├── .gitignore
└── README.md


### Deployment Architecture (recap)
Streamlit Community Cloud only runs one process — it can't also host a separate FastAPI server. So: `core/`, `agent/`, `ml/`, `llm/`, and `data_ingestion/` hold all logic with zero web-framework dependencies. FastAPI (`api/main.py`) imports from these for local dev/testing. Streamlit (`app.py`) *also* imports from them directly — that's what actually runs in production. One codebase, two front doors, nothing duplicated.

**Known caveats:** Neon Postgres is persistent, so data survives redeploys. ChromaDB's local index still needs rebuilding on cold start unless persisted separately. Groq API key and Neon connection string go in Streamlit's Secrets manager, never hardcoded.

### Database Schema (Postgres/Neon, draft)
`skus`, `historical_demand`, `inventory_snapshots`, `forecast_results`, `inventory_risk`, `deliveries`, `delivery_risk_predictions`, `vehicles`, `routes`/`route_stops`, `policies`, `recommendations`, `impact_simulations`, **`decision_traces`**, **`approvals`**

### Data Ingestion Strategy
The data layer is built behind a `DataSource` interface (`data_ingestion/base.py`). CSV is the main MVP working source. Excel and Neon DB sources have working sample implementations. API source is an extensible interface/example only.

### Evaluation Methodology
| Component | Metric |
|---|---|
| Forecasting | MAPE / RMSE on a **time-based holdout window**, compared against a naive baseline |
| Delivery risk | AUC / precision-recall, compared against a majority-class baseline |
| Inventory risk | Precision/recall vs. simulated ground-truth stockouts |
| Logistics optimization | % cost/distance reduction vs. naive routing |
| Agent + business impact | Before/after KPI deltas |

---

## 3. AI Decision Agent Design (genuine tool-using agent)

### Tools exposed to the agent (`agent/tools.py`)
- `get_demand_forecast(sku_id)` → wraps `core/forecasting.py`
- `get_inventory_risk(sku_id)` → wraps `core/inventory_risk.py`
- `get_delivery_risk(delivery_id)` → wraps `core/delivery_risk.py`
- `optimize_routes(delivery_ids, vehicle_constraints)` → wraps `core/logistics_optimizer.py`
- `retrieve_policies(query)` → wraps `core/rag.py`

### How the agent loop works (`agent/orchestrator.py`)
1. The agent receives a situation.
2. The Groq LLM decides which tool(s) to call — not a fixed hardcoded order.
3. Each tool call returns real, code-computed data (never LLM-invented).
4. Retrieved policies must genuinely constrain options considered.
5. Code (not LLM) assembles a structured options table.
6. LLM narrates and justifies the recommended option in plain English.
7. Recommendation + full trace written to `decision_traces` and surfaced for human approval.

### Decision Trace schema

trace_id, timestamp, inputs, predictions, policies_retrieved,
tools_used, options_considered, recommendation, human_approval, outcome


### Human-in-the-Loop Approval Gate
Any recommendation implying a real action is written with `human_approval.status = "pending"` and surfaced in Streamlit with **Approve / Reject** buttons. The agent never auto-executes.

---

## 4. ML Engineering Rules

### Time-based train/validation/test split
Never randomly shuffle time-series data into train/test. Split strictly by time.

### No data leakage
No feature may be computed using information not available at prediction time.

### Baseline comparison (mandatory)
Every model must be compared against a simple baseline before considered "done."

### Evaluation metrics
Report metrics on the **test** split only.

### Explainability
Use SHAP or built-in feature importance. Output feeds directly into the LLM's explanation step.

---

## 5. VS Code Setup

### Extensions to install
- **Python** (Microsoft), **Pylance**, **Jupyter** (optional), **GitLens**, **Even Better TOML**, **DotENV**

### Environment setup with `uv`

uv init
uv add fastapi uvicorn streamlit scikit-learn lightgbm chromadb sentence-transformers ortools groq sqlalchemy psycopg2-binary shap pytest python-dotenv
uv sync
uv run python core/forecasting.py
uv run pytest
uv run uvicorn api.main:app --reload
uv run streamlit run app.py


### Integrated terminal rules
1. Never chain commands with `&&`.
2. Prefix Python/tool commands with `uv run`.
3. One terminal tab per long-running process.
4. Read the actual error, top to bottom, before asking Claude about it.

---

## 6. Groq API Setup (free LLM + tool calling)

1. Go to **console.groq.com**, sign up free.
2. Navigate to **API Keys** → **Create API Key**, copy immediately.
3. Add to `.env`: `GROQ_API_KEY=your_key_here` and `NEON_DATABASE_URL=your_neon_connection_string_here`
4. Load with `python-dotenv` in `llm/explainer.py` and `agent/orchestrator.py`.
5. Use a Groq model that supports **tool/function calling**.
6. For deploy: add keys in **Streamlit Cloud → App settings → Secrets**.

---

## 7. Claude Project Setup — the handoff

1. Go to claude.ai → **Projects** → **Create Project**.
2. Name it: `SupplyChain Sentinel AI`.
3. Upload this file (`progress.md`) into the Project's knowledge/files.
4. Paste the following into the Project's **custom instructions** field:

You are my AI/ML mentor, software architect, backend engineer, data scientist,
and AI-agent engineer for my capstone project "SupplyChain Sentinel AI."

Read progress.md (uploaded to this project) as the single source of truth for
scope, architecture, tech stack, and current progress before answering anything.

Rules:

Before doing anything, read progress.md AND inspect the actual repository
files relevant to the current task — never assume a file's contents or
schema without seeing it.

Build incrementally, one file/component at a time. Never generate the whole
project at once.

Step-by-step workflow for every task:
1. Read the latest progress.md and inspect the actual repository files
   before making assumptions.
2. Identify the current task and explain what we're building and why, tied
   to the Build Checklist in progress.md.
3. Make only the required code/file changes.
4. Give me the exact terminal command(s) to run — including relevant
   pytest commands.
5. STOP and WAIT for me to provide the actual terminal output. Do not
   assume a file or test is correct just because it was written.
6. Analyze my actual output before deciding whether the implementation
   works.
7. If there is an error, fix it, then again give me the command(s) and
   wait for output — repeat until verified.
8. Do NOT ask me to commit, open a PR, push, merge, or mark a task DONE
   immediately after writing code. Git/PR steps happen only after the
   implementation is verified by my actual terminal output AND I
   explicitly say I want to continue to the Git workflow.

If I propose something unnecessary, overly complex, or risky for a 1-month
timeline, tell me clearly and suggest a simpler alternative.

The AI Decision Agent must be a genuine tool-calling agent (Groq tool/function
calling) that decides which tools to invoke based on the situation. Never
implement it as a hardcoded sequential pipeline disguised as an agent.

The LLM layer must never invent or calculate numerical predictions, risks,
costs, or optimization results — it only explains, summarizes, and reasons
about which tools to call.

RAG must use real, written business/procurement/inventory policies, and
retrieved policies must actually constrain the recommendation, not just be
mentioned.

Any ML model must use a time-based train/validation/test split, must be
checked for data leakage, and must be compared against a simple baseline
before being considered done.

Any action with real business consequence must go through a human-approval
gate before being marked as executed — never auto-execute.

Use uv (not pip/venv) and pytest for all environment and testing commands.

Never use && in terminal commands — one command at a time.

When another local file's actual contents are needed (e.g. exact column
names or schema from a file already built), inspect the repository if
accessible; otherwise ask me to paste the file contents or terminal
output. Never invent its schema or contents.

progress.md represents VERIFIED, MERGED shared repository state. Work on a
local/feature branch is NOT DONE until it is merged — never mark or imply
something is complete before that.

After we finish and I've verified a file, YOU must provide the exact text
to paste into progress.md — updated Current Project State, Build Checklist
tick, task board status change, and Session Handoff entry — but only once
verified, and only up to REVIEW status until I confirm the PR is merged.
Never just remind me — always give me the exact content ready to
copy-paste and commit.

5. Start a new conversation inside the Project and say: *"Let's start Phase 0 (Setup) from the Build Checklist."*
6. Every future session: open the Project (not a fresh unrelated chat), so the file context persists.
---

## 8. GitHub Workflow

### One-time setup

git init

Create `.gitignore` with at least:

.venv/
venv/
.env
pycache/
*.pyc
.DS_Store
.streamlit/secrets.toml
chroma_db/
.pytest_cache/
*.egg-info/

Then:

git add .
git commit -m "Initial commit: project structure"
git remote add origin https://github.com/bushrachohan/SupplyChain.git
git branch -M main
git push -u origin main


### After every file you build
1. Test in terminal — confirm expected output.
2. Run `uv run pytest` — confirm all relevant tests pass.
3. `git add <filename>`
4. `git commit -m "Add: <short description>"`
5. `git push`

**Commit message convention:** `Add:` for new files, `Fix:` for bug fixes, `Update:` for changes.

---

## 9. Testing Strategy (pytest)

- **`core/forecasting.py`** — correct shape/columns, baseline comparison runs, metrics returned.
- **`core/inventory_risk.py`** — known input produces expected risk flag.
- **`core/delivery_risk.py`** — valid probabilities (0–1), baseline comparison present.
- **`core/logistics_optimizer.py`** — solution respects vehicle capacity constraints.
- **`core/rag.py`** — safety stock query retrieves safety-stock policy document.
- **`agent/tools.py`** — each tool returns correct schema.
- **`agent/orchestrator.py`** — no delivery risk → does NOT call `optimize_routes`; flagged delivery → does call it.
- **`agent/decision_trace.py`** — trace has all required fields; `human_approval.status` starts as `"pending"`.

uv run pytest

**No file is committed without its tests passing.**

---

## 10. Build Checklist

### Phase 0 — Setup
- [x] VS Code + extensions installed
- [x] `uv init` run, `pyproject.toml` created
- [x] Initial dependencies added via `uv add ...`, `uv.lock` generated
- [x] Groq API key obtained, Neon Postgres database created, both stored in `.env`
- [x] Folder structure created (`core/`, `agent/`, `ml/`, `llm/`, `data_ingestion/`, `db/`, `policies/`, `api/`, `tests/`, `data/`)
- [x] Git repo initialized, `.gitignore` in place, first commit pushed to GitHub
- [x] Claude Project created, this file uploaded, custom instructions pasted
- [x] **Confirmed:** `git log` shows commits; `git remote -v` shows GitHub origin

### Phase 1 — Data Layer & Core ML Logic
- [x] `data_ingestion/base.py` — abstract `DataSource` interface defined
- [x] `data_ingestion/csv_source.py` — synthetic dataset loaded via this interface
- [x] `data_ingestion/excel_source.py`, `db_source.py` — working sample implementations
- [x] `data_ingestion/api_source.py` — extensible interface/example only
- [ ] `db/models.py`, `db/connection.py` — Neon Postgres schema created and connected
- [ ] `data_pipeline/` scripts: source data → Neon Postgres
- [x] `core/forecasting.py` — LightGBM, time-based split, baseline comparison, 12 tests passing
- [ ] `core/inventory_risk.py` — stockout/overstock logic, tested standalone
- [ ] `core/delivery_risk.py` — delivery risk classifier, time-based split, baseline comparison
- [ ] `core/logistics_optimizer.py` — OR-Tools VRP, tested standalone
- [x] `ml/evaluation.py` — split/leakage-check/baseline-comparison utilities, 13 tests passing
- [ ] `ml/explainability.py` — SHAP/feature importance for delivery risk
- [x] `tests/test_evaluation.py`, `tests/test_forecasting.py`, `tests/test_data_ingestion.py` — passing

### Phase 2 — RAG, Agent, and Decision Trace
- [x] Real business/procurement/inventory policy documents written and placed in `policies/`
- [ ] `core/rag.py` — ChromaDB + sentence-transformers, tested with real policy queries
- [ ] `llm/explainer.py` — Groq API wrapper, tested standalone
- [ ] `agent/tools.py` — tool wrappers around `core/*`, with schemas
- [ ] `agent/orchestrator.py` — real Groq tool-calling agent loop
- [ ] `agent/decision_trace.py` — trace built and persisted to `decision_traces` table
- [ ] `tests/test_rag.py`, `test_agent_tools.py`, `test_decision_trace.py` — passing

### Phase 3 — Human-in-the-Loop UI
- [ ] `api/main.py` — FastAPI endpoints wired to `agent/`/`core/`
- [ ] `app.py` — Streamlit dashboard with Approve/Reject buttons and business-impact simulation

### Phase 4 — Deploy
- [ ] `pyproject.toml` / `uv.lock` finalized
- [ ] Streamlit Cloud app created, connected to repo, secrets added
- [ ] Full `uv run pytest` suite passing before final deploy
- [ ] **Confirmed:** deployed app loads, runs full demo scenario end-to-end

---

## 11. Learning Log

Fill this in **after every session** — non-negotiable.
Session: [date]

What I built:
What broke (and how I fixed it, or didn't yet):
What I actually learned (not just "it works now"):
Questions for next session:


---

## 12. Common Mistakes (read before you make them)

- **Chaining commands with `&&`** — breaks silently on Windows PowerShell.
- **Committing `.env`, `.venv/`, or database credentials to GitHub.**
- **Letting the LLM generate a number** instead of only narrating one you computed.
- **Building a hardcoded pipeline and calling it an agent.**
- **Random train/test splits on time-series data** — always split by time.
- **Skipping the baseline comparison.**
- **Letting the agent auto-execute a real action** without human approval.
- **Skipping standalone testing** before integrating into the agent.
- **Building the whole project in one Claude session.**
- **Treating synthetic data as real company data.**
- **Forgetting to run `uv add`** when importing a new package.
- **Committing code with failing tests.**

---

## 13. Project Prioritization (keep scope disciplined)

| Priority | Project | Status |
|---|---|---|
| **Primary MVP** | Project 17 — Inventory Forecasting (demand forecasting + inventory risk + replenishment) | In scope now |
| **Secondary MVP** | Project 18 — Logistics/Delivery (delivery risk prediction + route optimization) | In scope now, built after primary MVP is solid |
| **Phase 2 (later)** | Project 10 — Supplier-Risk Monitoring & external disruption intelligence | Explicitly out of scope for the 1-month MVP |

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

This is a 4-person team. **All members may work simultaneously. There are no permanent roles.**

### 15.0 Team

- **Team Leader:** Bushra
- **Members:** Maryam, Shreeya, Samiya
- **Shared GitHub repository:** https://github.com/bushrachohan/SupplyChain

### 15.1 Task Ownership Rule

Before starting a task, a member must:
1. Read the latest `progress.md`.
2. Check the GitHub repository for active branches/issues/PRs.
3. Choose a task marked **TODO** and available.
4. Mark the task **IN PROGRESS** in the live task board (Section 15.2).
5. Add their name and branch name.
6. Confirm dependencies are finished.
7. Start only after confirming no duplication.

### 15.2 Task Status System — Live Task Board

Every task has one of: **TODO · IN PROGRESS · BLOCKED · REVIEW · DONE**.

**Dynamic task rule:** The team does not permanently assign roles. The team selects tasks through WhatsApp/team chat based on what is currently completed and what is available next. Only selected active tasks are marked `IN PROGRESS` so every AI coding assistant can see which tasks are already being worked on.

The developer name and local branch are intentionally not stored here. GitHub branches/PRs and team chat provide that coordination.

**Phase 0 — Setup**
| Task | Status | Dependency |
|---|---|---|
| Repo structure + `uv init` | DONE | — |
| Neon Postgres provisioning | DONE | — |
| Groq API key setup | DONE | — |
| Claude Project setup | DONE | — |

**Phase 1 — Data Layer & Core ML Logic**
| Task | Status | Dependency |
|---|---|---|
| `data_ingestion/base.py` + `csv_source.py` | DONE | repo structure |
| `data_ingestion/excel_source.py`, `db_source.py` | DONE | `base.py` |
| `data_ingestion/api_source.py` | DONE | `base.py` |
| `db/models.py`, `db/connection.py` | IN PROGRESS | Neon provisioning |
| `data_pipeline/` (load data → Neon) | TODO | `db/models.py` |
| `core/forecasting.py` | DONE | data ingestion |
| `core/inventory_risk.py` | IN PROGRESS | `forecasting.py` |
| `core/delivery_risk.py` | TODO | `data_pipeline/` |
| `core/logistics_optimizer.py` | TODO | `data_pipeline/` |
| `ml/evaluation.py` | DONE | — |
| `ml/explainability.py` | TODO | `delivery_risk.py` |
| Tests for all of the above | TODO | respective modules |

**Phase 2 — RAG, Agent, Decision Trace**
| Task | Status | Dependency |
|---|---|---|
| `policies/*.md` (real policy docs) | DONE | — |
| `core/rag.py` | TODO | `policies/` |
| `llm/explainer.py` | TODO | Groq key |
| `agent/tools.py` | TODO | `core/*` modules |
| `agent/orchestrator.py` | TODO | `agent/tools.py` |
| `agent/decision_trace.py` | TODO | orchestrator, `db/models.py` |
| Tests for all of the above | TODO | respective modules |

**Phase 3 — Human-in-the-Loop UI**
| Task | Status | Dependency |
|---|---|---|
| `api/main.py` | TODO | `agent/`, `core/` |
| `app.py` (Streamlit + approval UI) | TODO | `agent/`, `decision_trace.py` |

**Phase 4 — Deploy**
| Task | Status | Dependency |
|---|---|---|
| Finalize `pyproject.toml`/`uv.lock` | TODO | all above |
| Streamlit Cloud deploy + secrets | TODO | `app.py` |
| Full `pytest` suite passing | TODO | all modules |

### 15.3 Merge / Progress Update Workflow

The team uses WhatsApp/team chat for coordination and GitHub for implementation history.

When a developer finishes a task:
1. Verify the implementation locally.
2. Run the relevant tests.
3. Push the feature branch and open/update the Pull Request.
4. Share in the team WhatsApp:
   - PR link
   - what changed
   - files/modules changed
   - tests run and result
   - any issue that needs attention
5. The Team Leader reviews and merges the PR.
6. **After the PR is merged**, the Team Leader updates `progress.md`:
   - change the task to `DONE`
   - update Current Project State
   - update the Build Checklist if applicable
   - mark any newly available task(s) as TODO/available
7. Push the updated `progress.md` to `main`.
8. All members pull the latest `main` before choosing the next task.

`progress.md` records the shared repository state and active tasks; detailed developer ownership is coordinated through WhatsApp and GitHub.

### 15.4 GitHub Branching

`main` = stable, tested, demo-ready. **Never develop directly on `main`.** Branch names:

feature/forecasting
feature/inventory-risk
feature/delivery-risk
feature/route-optimizer
feature/rag
feature/agent-tools
feature/decision-trace
feature/dashboard
feature/database


### 15.5 Parallel Development

Independent workstreams proceed simultaneously when interfaces are defined. If two tasks modify the same shared file, coordinate first.

### 15.6 Shared / High-Conflict Files

- `progress.md`
- `pyproject.toml` / `uv.lock`
- `db/models.py`
- `api/main.py` route signatures
- `agent/tools.py` tool schemas
- `data_ingestion/base.py`

### 15.7 Interface-First Development

Define function name, inputs, output schema, types, errors before implementing dependent components.

### 15.8 Integration Rule

Individual task → local tests → Pull Request → review → integration → full test suite → main

Tag stable versions: `v0.1-foundation`, `v0.2-ml`, `v0.3-agent`, `v0.4-mvp`.

### 15.9 progress.md Is the Handoff Source of Truth

Never mark a feature complete merely because code was written. DONE only when Definition of Done (15.10) is satisfied.

### 15.10 Definition of Done

A task is DONE only when **all** of the following are true:
1. Code is implemented.
2. Real test input has been used.
3. Relevant automated tests pass.
4. Errors/invalid inputs are handled.
5. Output is correct and explainable where applicable.
6. Existing functionality still works (no regressions).
7. `progress.md` is updated.
8. Changes are committed and pushed.
9. Pull Request is merged successfully.

### 15.11 ML Integrity

Never modify datasets or models merely to make metrics look better. Synthetic data must always be identified as synthetic.

### 15.12 One-Month Scope Control

- **PRIMARY:** Project 17 — Inventory Forecasting / Stockout Prevention
- **SECONDARY:** Project 18 — Logistics / Delivery Risk / Route Optimization
- **FUTURE:** Project 10 — Supplier Risk Monitoring / External Disruption Intelligence

### 15.13 Current State Update Protocol

**While working:**
1. The developer works on the selected task branch.
2. Tests are run locally.
3. The developer pushes the branch and opens a PR.
4. The developer shares the PR and changes in WhatsApp.

**After merge:**
1. The Team Leader updates `progress.md` to reflect the merged repository state.
2. Completed task → `DONE`.
3. Newly available tasks → remain `TODO` until selected.
4. Selected next tasks → `IN PROGRESS`.
5. Push updated `progress.md` to `main`.

**When starting a new task:**
1. Pull latest `main`.
2. Read `progress.md`.
3. Check which tasks are `IN PROGRESS` and avoid them.
4. Choose an available `TODO` task through team coordination.
5. Start work on a task branch.

### 15.14 AI Coding Agent Rule

This project may be developed using Claude, Google Antigravity, or another AI coding assistant.

The assistant must:
- Read the latest `progress.md` AND inspect the actual repository files
  before starting — never assume a file's contents, schema, or column
  names without seeing them; ask for them if inaccessible.
- Treat the latest merged `progress.md` on `main` as the project source of
  truth.
- Check the live task board before choosing work.
- Never take a task already marked `IN PROGRESS` unless explicitly handed
  off.
- Never silently change architecture, dependencies, or MVP scope.
- Preserve existing working functionality.
- Work step-by-step: explain the task, make the change, give exact
  terminal commands, then STOP and WAIT for the developer's actual output
  before judging whether it works. Never assume a file is correct just
  because it was written.
- If output shows an error, fix it and again wait for the developer to
  re-run and share output — do not proceed on assumption.
- Never expose or commit secrets.
- Never instruct or imply committing, pushing, opening a PR, merging, or
  marking a task DONE immediately after writing code — those steps happen
  only after the developer confirms verification AND explicitly chooses to
  continue to the Git workflow.
- Do not mark a task `DONE` (or imply completion) in the shared progress
  until its PR is merged and verified. Prior to that, status is at most
  `REVIEW`.
- Report exactly what was changed and verified (not assumed).
- After a task is actually merged and verified, prepare a concise
  status/PR summary for the developer to share in WhatsApp.

### 15.15 Claude Account Handoff

- GitHub `main` is authoritative.
- Each member may use a different Claude account/Project or Antigravity workspace.
- Before each session, pull the latest `main` and read `progress.md`.
- If the local AI Project copy is older than GitHub, GitHub takes priority.
- Local folder paths are never stored in shared project documentation.

### 15.16 progress.md Merge Rule

`main` is the authoritative project state.

- Never overwrite newer progress with an older branch copy.
- Do not mark work `DONE` before its PR is merged.
- The Team Leader updates the shared task status after merge.
- Resolve `progress.md` conflicts by preserving the actual latest merged state.
- After the update, push `progress.md` to `main`.
- All teammates pull the latest `main` before continuing.

