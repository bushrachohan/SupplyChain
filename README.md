# 🛡️ SupplyChain Sentinel AI

> ### AI-Powered Supply Chain Decision Intelligence Platform
> **Predict. Detect. Explain. Simulate. Decide.**

SupplyChain Sentinel AI is an end-to-end decision intelligence platform that combines **machine learning, explainable AI, policy-aware RAG, optimization, and multi-agent deliberation** to help supply-chain teams identify operational risks and make validated decisions with human oversight.

<p align="center">
  <a href="https://supply-chain-pied-eight.vercel.app/"><strong>🚀 Launch Live Demo</strong></a>
  &nbsp; • &nbsp;
  <a href="https://github.com/bushrachohan/SupplyChain"><strong>💻 Source Code</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="Frontend">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="Backend">
  <img src="https://img.shields.io/badge/Database-Neon%20PostgreSQL-00E599?style=for-the-badge&logo=postgresql&logoColor=white" alt="Database">
  <img src="https://img.shields.io/badge/LLM-Groq-f55036?style=for-the-badge" alt="LLM">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/ML-LightGBM%20%7C%20SHAP-FF6F00?style=flat" alt="ML">
  <img src="https://img.shields.io/badge/RAG-ChromaDB-5B21B6?style=flat" alt="RAG">
  <img src="https://img.shields.io/badge/Optimization-Google%20OR--Tools-4285F4?style=flat" alt="Optimization">
  <img src="https://img.shields.io/badge/Tests-135%2F135%20passing-22C55E?style=flat&logo=pytest" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-gray?style=flat" alt="License">
</p>

---

## 🌐 Live Application

### [🚀 Launch SupplyChain Sentinel AI](https://supply-chain-pied-eight.vercel.app/)

**Current web application:** React + TypeScript frontend deployed on **Vercel**.

**Backend:** FastAPI service deployed on **Render**.

**Backend URL:** [https://supplychainsupplychain-sentinel-ai.onrender.com](https://supplychainsupplychain-sentinel-ai.onrender.com)

**API Documentation:** [https://supplychainsupplychain-sentinel-ai.onrender.com/docs](https://supplychainsupplychain-sentinel-ai.onrender.com/docs)

**Database:** Neon PostgreSQL.

**LLM:** Groq API.

> **Demo note:** The backend uses Render's free instance, which can spin down after inactivity. The first request after a period of inactivity may therefore take longer than subsequent requests.

---

# 🎯 The Problem

Modern supply chains generate large amounts of operational data, but conventional systems often struggle to turn that data into connected, explainable decisions.

### Common challenges

- **Siloed Risk Awareness** — Inventory, delivery, and logistics risks are often analyzed separately.
- **Black-Box Alerts** — Traditional alerts may identify a problem without explaining the operational factors behind it.
- **Ungrounded AI** — Generic LLM assistants can generate unsupported numbers or recommendations.
- **Unverified Actions** — Automated recommendations need policy and business validation before high-impact decisions are made.

### Sentinel's approach

**SupplyChain Sentinel AI connects the full decision lifecycle:**

```text
DATA
  ↓
PREDICT
  ↓
DETECT
  ↓
EXPLAIN
  ↓
RECOMMEND
  ↓
CRITIQUE
  ↓
SIMULATE
  ↓
HUMAN APPROVAL
  ↓
AUDIT TRACE
```

---

# 🖥️ Product Experience

The application provides a modern light-mode enterprise interface built with React and TypeScript while preserving the analytical functionality of the original Streamlit implementation.

### 🏠 Landing Page

The product entry point introduces Sentinel's decision-intelligence approach and provides direct access to the Command Center.

### 📊 Command Center

The central operational view for monitoring supply-chain conditions, demand, inventory, delivery risk, and decision intelligence.

### 📦 Data Hub

Upload and work with supply-chain datasets through:

- CSV ingestion
- Excel `.xlsx` ingestion
- Database connections
- Demo datasets
- Multiple-file workflows
- Dataset preview
- Dataset-type assignment
- Interactive column-to-schema mapping
- Validation
- Dataset understanding/profile information

### 🧠 Create a Decision

Generate explainable operational decisions using the existing ML, deterministic tools, policy context, and agent reasoning pipeline.

### ✅ Approval Queue

Review proposed actions and provide explicit human approval or rejection before operational commitment.

### 🕘 Decision History

Review previous decision traces, recommendations, critic evaluations, and approval status.

### 🔬 What-if Simulation

Evaluate alternative operational scenarios before committing to a decision.

---

# 🧩 Core Intelligence

## 📈 1. Dynamic Demand Forecasting & Inventory Risk

LightGBM quantile regression models future SKU demand by warehouse. The inventory engine cross-references lead times and current stock levels to calculate stockout risks, safety-stock deficits, and holding penalties.

## 📊 2. Demand Forecast vs Actual

The platform compares business actuals against Sentinel's out-of-sample LightGBM predictions on matching validation dates.

It provides:

- Forecast horizon
- Actual average
- Forecast average
- MAE
- MAPE
- Interactive visualizations
- Daily variance audit information

## ⚙️ 3. Deterministic Candidate Action Engine

The decision engine evaluates structured actions including:

```text
do_nothing
reorder
expedite
transfer_inventory
```

Candidate actions are evaluated against authoritative policy constraints and can produce purchase-order draft recommendations for human review.

## 🚚 4. Delivery Delay Risk + SHAP

The delivery-risk model evaluates shipment failure probability using operational features such as:

- Distance
- Traffic delay
- Carrier performance
- Weather conditions

SHAP TreeExplainer provides feature-level attribution so users can understand why a shipment is considered risky.

## 🌐 5. Cross-Risk Compounding

Sentinel combines inventory and delivery conditions into a unified operational state.

For example:

```text
Inventory shortage
       +
Delayed inbound shipment
       ↓
Compounding operational risk
       ↓
Higher enterprise severity
```

## 📚 6. Policy-Aware RAG

Corporate policy documents are indexed using ChromaDB and `all-MiniLM-L6-v2` embeddings.

Retrieved policy context can inform:

- Expediting limits
- Carrier SLAs
- Budget thresholds
- Inventory constraints
- Escalation requirements

## 🤖 7. Multi-Agent Deliberation

The decision workflow uses multiple reasoning roles:

### Orchestrator Agent
Analyzes the verified operational situation and formulates candidate resolutions.

### Policy Critic
Checks recommendations against policy, compliance boundaries, and budget constraints.

### Business Critic
Evaluates cost, feasibility, operational trade-offs, and business impact.

### Consensus Guardrail
Requires critic agreement before presenting an actionable recommendation.

## 🛡️ 8. Human-in-the-Loop Governance

Sentinel does not treat an AI recommendation as an automatic operational command.

The workflow is:

```text
AI Analysis
    ↓
Candidate Recommendation
    ↓
Policy Critic
    ↓
Business Critic
    ↓
Consensus
    ↓
Human Approval / Rejection
    ↓
Decision Ledger
```

---

# 🏗️ System Architecture


### High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       USER           │
                         │  React + TypeScript  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       VERCEL         │
                         │   Frontend / Vite    │
                         └──────────┬───────────┘
                                    │ HTTPS API
                                    ▼
                         ┌──────────────────────┐
                         │       RENDER         │
                         │   FastAPI Backend    │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │ ML / Risk   │       │ Agent + RAG │       │ Optimization│
       │ Forecasting │       │ + Critics   │       │  OR-Tools   │
       └─────────────┘       └──────┬──────┘       └─────────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
                ┌─────────────┐           ┌─────────────┐
                │    GROQ     │           │    NEON     │
                │     LLM     │           │ PostgreSQL  │
                └─────────────┘           └─────────────┘
```

---

# 🔄 Decision Intelligence Pipeline

```text
CSV / Excel / Database / Demo Dataset
                  ↓
          Dataset Preview
                  ↓
        Dataset Type Assignment
                  ↓
        Column-to-Schema Mapping
                  ↓
           Schema Validation
                  ↓
          Data Normalization
                  ↓
     ┌────────────┼─────────────┐
     ▼            ▼             ▼
 Demand        Inventory      Delivery
Forecasting      Risk           Risk
     └────────────┼─────────────┘
                  ↓
         Unified Intelligence
                  ↓
        Cross-Risk Assessment
                  ↓
        Policy RAG Retrieval
                  ↓
       Candidate Action Engine
                  ↓
        Multi-Agent Deliberation
             ↙          ↘
      Policy Critic   Business Critic
             ↘          ↙
              Consensus
                  ↓
         What-if Simulation
                  ↓
        Explainable Decision
                  ↓
          Human Approval
                  ↓
        Immutable Decision Trace
```

---

# 🧠 Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React + TypeScript | Production web interface |
| **Build Tool** | Vite | Frontend development and production build |
| **Styling** | Tailwind CSS | Responsive light-mode UI |
| **Routing** | React Router | Landing page and application navigation |
| **Backend** | FastAPI | REST API and application services |
| **Language** | Python 3.13+ | ML, backend, data and agent services |
| **ML** | LightGBM + scikit-learn | Forecasting and predictive models |
| **Explainability** | SHAP | Feature-level risk attribution |
| **Optimization** | Google OR-Tools | Capacitated Vehicle Routing |
| **RAG** | ChromaDB + Sentence Transformers | Semantic policy retrieval |
| **LLM** | Groq | Agent reasoning and narrative synthesis |
| **Database** | Neon PostgreSQL | Persistent application and decision data |
| **Data** | Pandas + OpenPyXL + SQLAlchemy | CSV, Excel and database ingestion |
| **Testing** | pytest | Unit and integration testing |
| **Deployment** | Vercel + Render + Neon | Cloud deployment |

---

# 🔌 Data Ingestion

Sentinel supports multiple operational data sources:

```text
CSV
 │
 ├── Upload one or multiple files
 │
 ▼
Preview + Column Detection
 │
 ▼
Dataset Type
 │
 ▼
Schema Mapping
 │
 ▼
Validation
 │
 ▼
Dataset Profile
 │
 ▼
Active Dataset
```

The same workflow is available for Excel data, while database ingestion provides a path for relational operational sources.

The ingestion layer supports schema validation and dataset-specific column mapping rather than assuming that every external dataset uses identical column names.

---

# 🛡️ Explainability & Governance

Sentinel is designed around five core principles:

### 1. Grounded AI

The LLM operates on verified operational values and deterministic tool outputs rather than inventing business metrics.

### 2. Policy Awareness

Recommendations are checked against retrieved enterprise policy context.

### 3. Multi-Agent Verification

Separate policy and business critics evaluate proposed actions.

### 4. Human Authority

High-impact operational actions require explicit human approval.

### 5. Auditability

Decision traces preserve the reasoning context, recommendations, critic evaluations, policies, and approval status.

---

# 📊 Why Sentinel AI?

| Capability | Traditional ERP | Generic LLM | Standalone ML | Sentinel AI |
|---|:---:|:---:|:---:|:---:|
| Cross-risk intelligence | ⚠️ | ⚠️ | ❌ | ✅ |
| Explainable risk attribution | ⚠️ | ❌ | ✅ | ✅ |
| Policy-aware RAG | ⚠️ | ⚠️ | ❌ | ✅ |
| Multi-agent verification | ❌ | ❌ | ❌ | ✅ |
| Candidate action evaluation | ⚠️ | ⚠️ | ⚠️ | ✅ |
| What-if simulation | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Human approval gate | ⚠️ | ❌ | ❌ | ✅ |
| Immutable decision traces | ⚠️ | ❌ | ❌ | ✅ |
| CSV / Excel / DB ingestion | ✅ | ❌ | ⚠️ | ✅ |

---

# 🗄️ Database

The system uses **Neon PostgreSQL** for persistent operational and decision data.

Core persisted information includes:

- Decision traces
- Human approvals
- Delivery-risk predictions
- Recommendations
- Critic evaluations
- Retrieved policies
- Operational records

Example decision lifecycle:

```text
PENDING_APPROVAL
       │
       ├──── APPROVED
       │
       └──── REJECTED
```

---

# 📁 Project Structure

```text
SupplyChain/
├── agent/
│   ├── orchestrator.py
│   ├── tools.py
│   ├── critics/
│   │   ├── policy_critic.py
│   │   └── business_critic.py
│   ├── consensus.py
│   └── decision_trace.py
│
├── api/
│   └── main.py
│
├── core/
│   ├── candidate_actions.py
│   ├── forecasting.py
│   ├── inventory_risk.py
│   ├── delivery_risk.py
│   ├── logistics_optimizer.py
│   ├── rag.py
│   ├── simulation.py
│   └── unified_intelligence.py
│
├── data_ingestion/
│   ├── base.py
│   ├── active_dataset.py
│   ├── validation.py
│   ├── csv_source.py
│   ├── excel_source.py
│   ├── db_source.py
│   └── api_source.py
│
├── data/
├── data_pipeline/
├── db/
├── llm/
├── ml/
├── policies/
├── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   └── vite.config.ts
│
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

# ⚙️ Local Development

## Prerequisites

- Python 3.13+
- Node.js 18+
- npm
- Git
- Groq API key
- Neon PostgreSQL database

## 1. Clone

```bash
git clone https://github.com/bushrachohan/SupplyChain.git
cd SupplyChain
```

## 2. Backend setup

```bash
uv sync
```

Create your environment file:

```bash
cp .env.example .env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key
NEON_DATABASE_URL=your_neon_database_url
```

Run FastAPI:

```bash
uv run uvicorn api.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

## 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The local frontend will be available through the Vite development server.

---

# 🧪 Testing

The project contains unit and integration tests covering major intelligence and application components.

```bash
uv run pytest
```

Current project test status:

```text
135 / 135 tests passing
```

---

# ☁️ Deployment

## Frontend — Vercel

The React + TypeScript frontend is deployed on Vercel.

```text
https://supply-chain-pied-eight.vercel.app/
```

Vercel configuration:

```text
Root Directory: frontend
Framework: Vite
Build Command: npm run build
Output Directory: dist
```

Frontend environment variable:

```env
VITE_API_URL=https://supplychainsupplychain-sentinel-ai.onrender.com
```

## Backend — Render

The FastAPI backend is deployed as a Render Web Service.

**Live Backend:** [https://supplychainsupplychain-sentinel-ai.onrender.com](https://supplychainsupplychain-sentinel-ai.onrender.com)  
**FastAPI Docs:** [https://supplychainsupplychain-sentinel-ai.onrender.com/docs](https://supplychainsupplychain-sentinel-ai.onrender.com/docs)

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Required backend secrets:

```env
GROQ_API_KEY=...
NEON_DATABASE_URL=...
```

## Database — Neon

Neon PostgreSQL provides the persistent relational database used by the application.

---

# 🔐 Environment Variables

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Powers LLM reasoning and multi-agent deliberation |
| `NEON_DATABASE_URL` | Connects the application to Neon PostgreSQL |
| `VITE_API_URL` | Connects the deployed frontend to the FastAPI backend |

> Never commit `.env` files or API keys to GitHub.

---

# 🗺️ Roadmap

### Completed

- [x] LightGBM demand forecasting with quantile intervals
- [x] Demand forecast vs actual visualization
- [x] Delivery delay classifier with SHAP attribution
- [x] Capacitated Vehicle Routing Problem via Google OR-Tools
- [x] ChromaDB policy RAG
- [x] Deterministic candidate action engine
- [x] Multi-agent deliberation
- [x] Policy and Business Critics
- [x] Consensus guardrails
- [x] Immutable decision traces
- [x] Human-in-the-loop approval workflow
- [x] CSV ingestion
- [x] Excel ingestion
- [x] Database ingestion
- [x] Multiple-file dataset workflow
- [x] Interactive schema mapping
- [x] Dataset understanding/profile
- [x] Kaggle schema auto-aliasing
- [x] Cross-risk compounding
- [x] React + TypeScript frontend
- [x] Vercel frontend deployment
- [x] FastAPI backend deployment

### Future Scope

- [ ] Enterprise ERP integrations such as SAP / Oracle WMS
- [ ] Real-time supply-chain telemetry
- [ ] Real-time weather and traffic integrations
- [ ] Multi-depot, time-windowed routing
- [ ] Enterprise role-based access control
- [ ] Multi-tenant architecture
- [ ] Real-time alerting and notifications
- [ ] Advanced scenario optimization
- [ ] Cloud-native model serving and observability

---

# 👥 Team

**Bushra** — Team Leader  
**Maryam**  
**Shreeya**  
**Samiya**

---

# 🧭 Design Principles

### 01 — Grounded Intelligence
The LLM narrates and reasons over verified operational values and deterministic tool outputs.

### 02 — Human-in-the-Loop
High-impact interventions require human sign-off before operational commitment.

### 03 — True Agentic Deliberation
The orchestrator can select appropriate tools based on the operational situation rather than relying only on a rigid linear workflow.

### 04 — Transparent Explainability
Risk predictions are accompanied by feature-level attribution where supported by the underlying model.

### 05 — Data Integrity
Synthetic datasets are clearly treated as testing/demo data and are not represented as proprietary production records.

---

# 📄 License

MIT License — see [`LICENSE`](./LICENSE).

---

<p align="center">
  <strong>SupplyChain Sentinel AI</strong><br>
  AI-powered decision intelligence for resilient supply chains.
</p>
