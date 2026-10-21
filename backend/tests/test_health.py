from fastapi.testclient import TestClient

from app.main import create_app


def test_health_responde_ok():
    client = TestClient(create_app())
    resposta = client.get("/api/v1/health")

    assert resposta.status_code == 200
    data = resposta.json()

    # O endpoint retorna api, db e pgvector, não um campo "status"
    assert data.get("api") == "ok"
    assert "db" in data
    assert "pgvector" in data
