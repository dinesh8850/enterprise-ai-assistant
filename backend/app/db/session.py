"""
session.py — Sets up the SQLAlchemy connection to our Postgres database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency: provides a database session for one request,
    and guarantees it's closed afterward, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
