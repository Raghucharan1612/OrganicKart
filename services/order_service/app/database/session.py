from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.database.base import Base

if settings.ORDER_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.ORDER_DATABASE_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
else:
    engine = create_engine(settings.ORDER_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["Base", "engine", "SessionLocal", "get_db"]
