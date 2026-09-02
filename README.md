# SupplyChain Sentinel AI

An end-to-end AI-powered supply-chain decision intelligence platform.

## Stack
- **ML:** scikit-learn, LightGBM, SHAP
- **Optimization:** OR-Tools (VRP)
- **RAG:** ChromaDB + sentence-transformers
- **Agent/LLM:** Groq API (tool/function calling)
- **Database:** Neon PostgreSQL
- **Backend:** FastAPI + Uvicorn
- **Frontend:** Streamlit
- **Environment:** uv

## Setup
1. Clone the repo
2. Run `uv sync`
3. Copy `.env.example` to `.env` and fill in secrets
4. Run `uv run streamlit run app.py`

## Team
- Bushra (Team Leader), Maryam, Shreeya, Samiya