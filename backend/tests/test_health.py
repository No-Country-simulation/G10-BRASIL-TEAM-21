import pytest
from fastapi.testclient import TestClient

from app.api._deps import get_db
from app.main import create_app


class _Res:
    def __init__(self, v):
        self.v = v

    def first(self):
        return self.v


class SessaoOk:
    def execute(self, *a, **k):
        return _Res((1,))


class SessaoQuebrada:
    def execute(self, *a, **k):
        raise RuntimeError("banco fora")


class SessaoSemVector:
    def __init__(self):
        self.n = 0

    def execute(self, *a, **k):
        self.n += 1
        return _Res(None if self.n == 2 else (1,))


def _cliente(sessao):
    app = create_app()

    def _db():
        yield sessao

    app.dependency_overrides[get_db] = _db
    return TestClient(app)


def test_health_ok():
    r = _cliente(SessaoOk()).get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"api": "ok", "db": "ok", "pgvector": "ok"}


def test_health_503_quando_banco_cai():
    r = _cliente(SessaoQuebrada()).get("/api/v1/health")
    assert r.status_code == 503
    assert r.json()["db"] == "falha"


def test_health_503_quando_falta_vector():
    r = _cliente(SessaoSemVector()).get("/api/v1/health")
    assert r.status_code == 503
    assert r.json() == {"api": "ok", "db": "ok", "pgvector": "falha"}


@pytest.mark.integration
def test_health_banco_real(engine):
    r = TestClient(create_app()).get("/api/v1/health")
    assert r.status_code == 200 and r.json()["pgvector"] == "ok"