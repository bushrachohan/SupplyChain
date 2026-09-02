import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("NEON_DATABASE_URL is not set in .env")

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