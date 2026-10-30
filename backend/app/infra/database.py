# backend/app/infra/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# A URL do banco vem das variáveis de ambiente (docker-compose já configura)
# Ex.: postgresql://user:password@db:5432/dbname
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency do FastAPI para obter uma sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()