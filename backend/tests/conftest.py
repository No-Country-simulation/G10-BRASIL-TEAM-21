import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.infra.db.models import Base


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: testes que dependem do PostgreSQL do Compose"
    )

@pytest.fixture(scope="session")
def engine():
    # Usa o banco do Docker Compose
    url = get_settings().database_url
    return create_engine(url)

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
