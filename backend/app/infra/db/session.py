from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def _fabrica() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False)


def create_session() -> Session:
    return _fabrica()()


def get_db() -> Iterator[Session]:
    db = create_session()
    try:
        yield db
    finally:
        db.close()
