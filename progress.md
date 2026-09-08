# 🛡️ SupplyChain Sentinel AI

> **AI-Powered Supply Chain Risk & Decision Intelligence Platform**

An end-to-end AI decision intelligence platform that forecasts demand, detects inventory and delivery risks, optimizes logistics routes, retrieves business policies using RAG, and uses **genuine multi-agent deliberation** before presenting recommendations to a human decision-maker.

**🚀 Live Demo → [supplychain-xiydr3sj8cfn8o5rstpg8t.streamlit.app](https://supplychain-xiydr3sj8cfn8o5rstpg8t.streamlit.app/)**

---

## What It Does

SupplyChain Sentinel AI acts like an intelligent supply-chain manager. It combines machine learning, optimization, RAG, and multi-agent AI to help businesses make safer and more data-driven decisions.

* 📈 **Forecast Demand** → Predict future demand using LightGBM
* ⚠️ **Detect Supply Chain Risks** → Identify stockout, overstock, and delivery risks
* 🚚 **Optimize Routes** → Solve Capacitated Vehicle Routing Problems using OR-Tools
* 📚 **Understand Business Policies** → Retrieve relevant policies using RAG
* 🤖 **Multi-Agent Decision Making** → Primary AI proposes a solution while specialized critics review it
* 💰 **Evaluate Business Impact** → Check cost and operational feasibility
* 👤 **Human-in-the-Loop** → Every recommendation requires human approval before action
* 🔬 **What-If Simulation** → Test potential decisions before approving them

---

## Screenshots

> Add your Streamlit dashboard screenshots here.

| Supply Chain Command Center             | AI Decision                              |
| --------------------------------------- | ---------------------------------------- |
| ![Dashboard](screenshots/dashboard.png) | ![AI Decision](screenshots/decision.png) |

| Risk Analysis                          | What-If Simulation                        |
| -------------------------------------- | ----------------------------------------- |
| ![Risk Analysis](screenshots/risk.png) | ![Simulation](screenshots/simulation.png) |

| Policy Review                            | Multi-Agent Consensus                   |
| ---------------------------------------- | --------------------------------------- |
| ![Policy Review](screenshots/policy.png) | ![Consensus](screenshots/consensus.png) |

---

## How the AI Makes a Decision

SupplyChain Sentinel AI does **not** simply ask an LLM to guess what should happen.

The decision process is grounded in actual data and specialized tools:

```text
Supply Chain Data
       ↓
Data Ingestion
       ↓
ML + Optimization + RAG Tools
       ↓
Primary AI Decision Agent
       ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
Policy Critic   Business Critic   Evidence
 ↓               ↓                ↓
 └───────────────┴────────────────┘
               ↓
       Consensus Layer
               ↓
       Human Approval
          ↓         ↓
       Approve     Reject
          ↓
   What-If Simulation
```

### Example

If inventory is falling below the required safety stock:

1. The forecasting model estimates future demand.
2. The inventory-risk module calculates the risk.
3. The Primary Agent evaluates the situation and available tools.
4. The Policy Critic checks whether the recommendation follows company policies.
5. The Business Critic checks cost and feasibility.
6. The Consensus Layer determines whether the proposal passes review.
7. The recommendation is shown to a human manager.
8. The manager can **Approve or Reject** the recommendation.
9. What-if simulation can be used to evaluate the potential outcome.

---

## Tech Stack

| Layer                      | Technology                                   |
| -------------------------- | -------------------------------------------- |
| **ML / Forecasting**       | LightGBM, scikit-learn, SHAP                 |
| **Optimization**           | Google OR-Tools — Capacitated VRP            |
| **RAG / Policy Retrieval** | ChromaDB + sentence-transformers             |
| **AI / LLM**               | Groq API — `openai/gpt-oss-120b`             |
| **Agent Framework**        | Custom tool-calling multi-agent architecture |
| **Database**               | Neon PostgreSQL                              |
| **Backend**                | FastAPI + Uvicorn                            |
| **Frontend**               | Streamlit                                    |
| **Environment**            | `uv` + `pyproject.toml` + `uv.lock`          |
| **Deployment**             | Streamlit Community Cloud                    |

---

## Architecture

```text
CSV / Excel / Neon PostgreSQL / API
                │
                ▼
        Data Ingestion Layer
                │
                ▼
        ┌─────────────────────┐
        │    Core Modules     │
        ├─────────────────────┤
        │ forecasting.py      │ → LightGBM demand forecast
        │ inventory_risk.py   │ → Stockout / overstock risk
        │ delivery_risk.py    │ → Delivery risk + SHAP
        │ logistics_optimizer │ → OR-Tools VRP
        │ rag.py              │ → Policy retrieval
        │ simulation.py       │ → What-if analysis
        └─────────────────────┘
                │
                ▼
       AI Decision Agent
       └── orchestrator.py
                │
                ▼
        Multi-Agent Critique
          ┌───────────────┐
          │               │
          ▼               ▼
   Policy Critic    Business Critic
   Safety + Rules   Cost + Feasibility
          │               │
          └───────┬───────┘
                  ▼
          Consensus Layer
                  │
                  ▼
        Human Approval Gate
          ┌────────┴────────┐
          ▼                 ▼
       APPROVE            REJECT
          │
          ▼
     What-If Simulation
```

---

## Key Features

### 📈 Demand Forecasting

LightGBM is used to forecast future demand from historical supply-chain data.

The forecast is then used by downstream risk and decision modules rather than allowing the LLM to invent inventory or demand numbers.

---

### ⚠️ Inventory Risk Detection

The system identifies potential:

* Stockout situations
* Overstock situations
* Safety-stock violations
* Reorder requirements

The actual numerical calculations are performed by deterministic core tools.

---

### 🚚 Logistics Optimization

The platform uses **Google OR-Tools** to solve Capacitated Vehicle Routing Problems.

It considers factors such as:

* Vehicle capacity
* Delivery locations
* Demand
* Route distance
* Operational constraints

The LLM does not calculate the route itself. It calls the optimization tool and uses the resulting numbers.

---

### 📦 Delivery Risk Prediction

A machine-learning classifier predicts delivery risk.

**SHAP** is used to explain which features contributed to the prediction, making the model output easier to inspect and understand.

---

### 📚 Policy RAG

Business policies are stored as documents and indexed using:

* ChromaDB
* Sentence Transformers
* `all-MiniLM-L6-v2`

When the AI needs to evaluate a decision, it retrieves the relevant policy information instead of relying on general LLM knowledge.

---

### 🤖 Genuine Tool-Calling Agent

The Primary Agent is not a fixed sequence of predefined steps.

The LLM decides which available tools are relevant to the situation.

For example:

```text
Inventory problem
      ↓
Forecasting
      ↓
Inventory Risk
      ↓
Decision
```

A route-specific problem can instead trigger:

```text
Delivery problem
      ↓
Delivery Risk
      ↓
Route Optimization
      ↓
Decision
```

This allows the system to select tools based on the actual business situation.

---

### 👥 Multi-Agent Critique

The recommendation is independently reviewed by specialized AI critics.

**Policy Critic**

Checks:

* Policy compliance
* Safety constraints
* Business rules

**Business Critic**

Checks:

* Cost
* Operational feasibility
* Business impact

The recommendation proceeds through a **consensus layer** before reaching the human approval stage.

---

### 👤 Human-in-the-Loop

The AI never directly executes a business action.

Instead:

```text
AI Recommendation
       ↓
Policy Review
       ↓
Business Review
       ↓
Consensus
       ↓
Human Manager
    ↙       ↘
Approve    Reject
```

This keeps the final decision with the human operator.

---

### 🔬 What-If Simulation

Before approving a recommendation, users can evaluate potential scenarios.

For example:

```text
Current Inventory: 150 units

AI Recommendation:
Order 101 additional units

What-if:
Inventory → 251 units

Evaluate:
• Safety stock
• Demand coverage
• Risk
• Business impact
```

This allows decision-makers to understand potential outcomes before acting.

---

## Quick Start

### Prerequisites

* Python 3.13+
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Clone the repository

```bash
git clone https://github.com/bushrachohan/SupplyChain.git
cd SupplyChain
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key
NEON_DATABASE_URL=your_neon_database_url
```

⚠️ **Never commit your `.env` file to GitHub.**

### 4. Start the Streamlit dashboard

```bash
uv run streamlit run app.py
```

The dashboard will open at:

```text
http://localhost:8501
```

---

## Run Tests

Run the complete test suite:

```bash
uv run pytest
```

Expected:

```text
90 passed
```

---

## Run FastAPI Locally

FastAPI is available for local development and API testing:

```bash
uv run uvicorn api.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

---

## Secrets Required

| Secret              | Purpose                       |
| ------------------- | ----------------------------- |
| `GROQ_API_KEY`      | Access to the Groq LLM        |
| `NEON_DATABASE_URL` | Connection to Neon PostgreSQL |

For local development, store these in `.env`.

For Streamlit Cloud, add them through:

**Advanced settings → Secrets**

Example:

```toml
GROQ_API_KEY = "gsk_..."
NEON_DATABASE_URL = "postgresql://..."
```

---

## Deployment — Streamlit Community Cloud

The Streamlit dashboard can be deployed directly from GitHub.

1. Push the project to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app**.
4. Select the repository.
5. Set the main file to:

```text
app.py
```

6. Configure the required secrets.
7. Click **Deploy**.

### ChromaDB on Streamlit Cloud

The `chroma_db/` directory is not committed to GitHub.

On a fresh deployment, `core/rag.py` detects the missing index and rebuilds it automatically from the policy documents in:

```text
policies/
```

No manual ChromaDB setup is required.

---

## Why `requirements.txt`?

Streamlit Community Cloud installs production dependencies using `requirements.txt`.

The file is generated from the project's `uv.lock`:

```bash
uv export --format requirements-txt --no-hashes --no-dev -o requirements.txt
```

Do not manually edit the generated production dependency file.

---

## Project Structure

```text
SupplyChain/
│
├── app.py                         # Streamlit production entry point
├── api/
│   └── main.py                   # FastAPI local API
│
├── agent/
│   ├── orchestrator.py            # Primary AI decision agent
│   ├── tools.py                   # Tool wrappers + schemas
│   ├── consensus.py               # Multi-agent consensus
│   ├── decision_trace.py          # Decision trace persistence
│   └── critics/
│       ├── policy_critic.py       # Policy + safety review
│       └── business_critic.py     # Cost + feasibility review
│
├── core/
│   ├── forecasting.py             # LightGBM forecasting
│   ├── inventory_risk.py          # Inventory risk detection
│   ├── delivery_risk.py           # Delivery risk + SHAP
│   ├── logistics_optimizer.py     # OR-Tools VRP
│   ├── rag.py                     # Policy RAG
│   └── simulation.py              # What-if simulation
│
├── ml/
│   ├── evaluation.py              # Model evaluation
│   └── explainability.py          # SHAP helpers
│
├── llm/
│   └── explainer.py               # LLM explanation layer
│
├── db/
│   ├── models.py                  # SQLAlchemy models
│   └── connection.py              # Neon PostgreSQL connection
│
├── data_ingestion/
│   ├── base.py                    # DataSource interface
│   ├── csv_source.py              # CSV source
│   ├── excel_source.py            # Excel source
│   ├── db_source.py               # Database source
│   └── api_source.py              # API source
│
├── policies/                      # Business policy documents
├── data/                          # Synthetic demonstration data
├── data_pipeline/                 # Data generation + loading
├── tests/                         # Automated tests
│
├── .streamlit/
│   └── config.toml                # Streamlit configuration
│
├── pyproject.toml                 # Project dependencies
├── requirements.txt               # Deployment dependencies
├── uv.lock                        # Locked dependencies
├── .env.example                   # Environment template
└── README.md
```

---

## Key Design Principles

### 🎯 LLM Grounding

The LLM is responsible for **reasoning and narration**, not inventing business numbers.

Numerical values must come from the underlying tools and data sources.

```text
Data → Tool → Numerical Result → LLM Reasoning
```

Not:

```text
LLM → Guess a Number
```

---

### 🛡️ Safety First

No business action is executed automatically.

Every recommendation passes through:

```text
Policy Review
      ↓
Business Review
      ↓
Consensus
      ↓
Human Approval
```

---

### 🧠 Real Agent, Not a Fixed Pipeline

The Primary Agent dynamically chooses which tools to call based on the situation.

A simple inventory issue does not automatically trigger route optimization.

This makes the system more efficient and closer to an actual decision-support agent.

---

### 📊 Synthetic Data

All files inside `data/` are **synthetic demonstration data**.

They are used for development, testing, and demonstration and are not presented as real company data.

---

## Team

Built by:

**Bushra** — Team Leader · **Maryam** · **Shreeya** · **Samiya**

See [`progress.md`](progress.md) for the complete task board, implementation checklist, and development progress.

---

## Project Highlights

* 🤖 Genuine LLM tool-calling agent
* 👥 Multi-agent policy + business critique
* 📈 LightGBM demand forecasting
* ⚠️ Inventory and delivery risk detection
* 🚚 OR-Tools Capacitated VRP optimization
* 📚 ChromaDB-based policy RAG
* 🔍 SHAP explainability
* 🔬 What-if decision simulation
* 👤 Human approval gate
* 🗄️ Neon PostgreSQL
* ☁️ Streamlit Cloud deployment
* 🧪 90 automated tests

---

## ⚠️ Important

This project is designed as a **decision-support and demonstration platform**. Recommendations should be reviewed by qualified human operators before being applied to real-world supply-chain operations.

---

**SupplyChain Sentinel AI — From supply-chain data to explainable, policy-aware decisions.** 🛡️
