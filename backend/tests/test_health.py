from fastapi.testclient import TestClient

from app.main import create_app


def test_health_responde_ok():
    client = TestClient(create_app())

    resposta = client.get("/api/v1/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"
