import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Guardrail: Check PostgreSQL connection string (NEON_DATABASE_URL or standard DATABASE_URL)
DATABASE_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("NEON_DATABASE_URL") or st.secrets.get("DATABASE_URL")
    except Exception:
        pass

is_production = (
    os.getenv("ENVIRONMENT", "").lower() == "production" 
    or os.getenv("RENDER", "").lower() == "true"
)

if not DATABASE_URL:
    if is_production:
        raise ValueError(
            "CRITICAL: Production database URL (NEON_DATABASE_URL or DATABASE_URL) is not set. "
            "Render production deployment requires a configured PostgreSQL database."
        )
    # Local development / test fallback only
    DATABASE_URL = "sqlite:///./sentinel.db"
    print("[INFO] NEON_DATABASE_URL not set. Running in local development mode with SQLite: sentinel.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # checks connection is alive before using it
        pool_size=5,
        max_overflow=10,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass


def get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()