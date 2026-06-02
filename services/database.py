from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base

DATABASE_URL = "sqlite:///booknotes.db"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Return a new SQLAlchemy session instance."""
    return SessionLocal()
