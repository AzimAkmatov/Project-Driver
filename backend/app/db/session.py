# backend/app/db/session.py
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ..core.security import settings  # expects settings.DATABASE_URL
from .base import Base

# Example DATABASE_URL formats:
# Postgres: postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
DATABASE_URL = settings.DATABASE_URL

# If you're deploying to AWS RDS, SSL is recommended.
# Easiest switch: include `?sslmode=require` in DATABASE_URL for prod.
if os.getenv("APP_ENV", "dev") != "dev" and "sslmode" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# Connection pool tuned for ECS Fargate (small dev service)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,           # adjust if you increase desired_count
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a DB session and ensures close().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
