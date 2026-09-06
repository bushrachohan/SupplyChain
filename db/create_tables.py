import sys
sys.path.insert(0, '.')

from db.connection import engine, Base
import db.models  # noqa: F401 — registers all models with Base

Base.metadata.create_all(bind=engine)
print("All tables created.")