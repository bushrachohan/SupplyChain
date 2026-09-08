# 🛡️ SupplyChain Sentinel AI

> **An AI-Powered Supply Chain Risk & Decision Intelligence Platform**

Welcome to **SupplyChain Sentinel AI**! This project is designed to act like a highly intelligent supply-chain manager. It looks at your data to predict when things might go wrong (like running out of stock or shipments being delayed) and uses a team of AI agents to recommend the safest, most cost-effective solution for your business.

**👉 [View the Live Demo Here!](https://supplychain-xiydr3sj8cfn8o5rstpg8t.streamlit.app/)**

---

## 🌟 What Does It Do?

1. **Spot Risks Early:** It uses Machine Learning to predict future demand and flag potential inventory shortages or delivery delays.
2. **Consults the Rulebook:** It reads your company's actual business policies to ensure any action it takes is compliant.
3. **Multi-Agent Teamwork:** Instead of just trusting one AI, we have multiple!
   - A **Primary Agent** suggests a solution.
   - A **Policy Critic** checks if it breaks any rules.
   - A **Business Critic** checks if it makes financial sense.
4. **Human-in-the-Loop:** The AI *never* acts on its own. It presents its entire thought process to a human manager for final approval.

---

## 🚀 How to Run the Project (Step-by-Step)

If you want to run this project on your own computer, follow these simple steps!

### Step 1: Install Prerequisites
Make sure you have installed:
- Python (version 3.13 or higher)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (a super-fast Python package manager)

### Step 2: Clone the Project
Open your computer's terminal and download the project:
```bash
git clone https://github.com/bushrachohan/SupplyChain.git
cd SupplyChain
```

### Step 3: Install Everything
Use `uv` to automatically download all the required libraries:
```bash
uv sync
```

### Step 4: Add Your Secret Keys
To connect to our AI brain and database, the project needs two secret passwords. 
1. Copy the template file: `cp .env.example .env` (or just rename `.env.example` to `.env`).
2. Open `.env` and fill in your keys:
   - `GROQ_API_KEY`: Get a free key from [Groq](https://console.groq.com)
   - `NEON_DATABASE_URL`: Get a free Postgres database from [Neon](https://neon.tech)

### Step 5: Start the Dashboard!
Run this command to launch the beautiful user interface:
```bash
uv run streamlit run app.py
```
Your web browser will automatically open the **Supply Chain Command Center**!

---

## 🌐 How to Deploy to the Web (Streamlit Cloud)

Want to share this project with the world? You can deploy it for free!

1. Make sure all your code is pushed to your GitHub `main` branch.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
3. Click **New app** and connect your `SupplyChain` repository.
4. Set the **Main file path** to `app.py`.
5. Click **Advanced settings → Secrets** and paste your `.env` secrets:
   ```toml
   GROQ_API_KEY = "gsk_..."
   NEON_DATABASE_URL = "postgresql://..."
   ```
6. Click **Deploy!**

*(Note: The `requirements.txt` file is used specifically to help Streamlit Cloud install your packages).*

---

## 🛠️ The Technology Behind the Magic

For the technical judges and developers, here is what powers the platform under the hood:

- **Machine Learning:** LightGBM, scikit-learn, and SHAP for forecasting and risk detection.
- **AI Brain:** Groq API running `openai/gpt-oss-120b` for blazingly fast reasoning.
- **RAG (Retrieval-Augmented Generation):** ChromaDB stores our company policies so the AI can read them instantly.
- **Database:** Neon Serverless PostgreSQL.
- **Frontend / Backend:** Streamlit (UI) and FastAPI (Local API).

---

## 👥 Meet the Team

This project was proudly built by:
- **Bushra** (Team Leader)
- **Maryam** 
- **Shreeya** 
- **Samiya**

*(For detailed project tracking, see our `progress.md` file!)*

---

### ⚠️ Key Design Philosophy
- **No Hallucinations:** The AI is strictly programmed to pull real numbers from the database. It is not allowed to guess inventory levels.
- **Safety First:** No action is taken without human approval.
- **Mock Data:** The CSV data provided in this project is synthetic and built for demonstration purposes.
