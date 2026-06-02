"""Re-exports database utilities from models.database for backward compatibility."""

from models.database import DATABASE_URL, SessionLocal, engine, get_session, init_db

__all__ = ["DATABASE_URL", "engine", "SessionLocal", "init_db", "get_session"]
