import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: testes que dependem do PostgreSQL do Compose"
    )
