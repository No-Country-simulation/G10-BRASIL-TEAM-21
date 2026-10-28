import pytest
from fastapi.testclient import TestClient

from app.api._deps import get_current_user  # <-- Adicione essa linha inteira
from app.main import app, create_app  # <-- Adicione o create_app aqui

CHAVES = {"status", "codigo", "mensagem", "detalhes", "request_id"}
AUTH = {"Authorization": "Bearer qualquer"}
BASE = {
    "perfil_destinatario": "Iniciante",
    "formato_saida": "Flashcards",
    "nicho_setor": "Geral",
    "nivel_detalhe": "Didatico",
}


@pytest.fixture
def client():
    return TestClient(app)  # <-- MUDOU AQUI


def _confere(r, status, codigo):
    assert r.status_code == status
    corpo = r.json()
    assert set(corpo) == CHAVES and corpo["status"] == "erro" and corpo["codigo"] == codigo
    return corpo


def test_501_nas_rotas_casca(client):
    for rota in (
        "/api/v1/perfil",
        #"/api/v1/usuarios/me",
        "/api/v1/documentos",
        "/api/v1/adaptacoes",
    ):
        _confere(client.get(rota, headers=AUTH), 501, "NAO_IMPLEMENTADO")


def test_401_sem_token(client):
    # Para esse teste dar 401, precisamos remover o mock temporariamente
    app.dependency_overrides.pop(get_current_user, None)
    _confere(client.get("/api/v1/perfil"), 401, "NAO_AUTENTICADO")


def test_404_rota_inexistente(client):
    _confere(client.get("/api/v1/nao-existe", headers=AUTH), 404, "RECURSO_NAO_ENCONTRADO")


def test_422_validacao(client):
    corpo = _confere(client.post("/api/v1/auth/login", json={}), 422, "VALIDACAO_FALHOU")
    assert corpo["detalhes"] and "campo" in corpo["detalhes"][0]


def test_400_documento_id_e_conteudo_juntos(client):
    corpo = {**BASE, "documento_id": "doc-1", "documento_titulo": "T", "documento_conteudo": "C"}
    _confere(
        client.post("/api/v1/adaptacoes", json=corpo, headers=AUTH), 400, "REQUISICAO_INVALIDA"
    )


def test_400_sem_documento_nenhum(client):
    _confere(client.post("/api/v1/adaptacoes", json=BASE, headers=AUTH), 400, "REQUISICAO_INVALIDA")


def test_documento_id_sozinho_chega_no_501(client):
    _confere(
        client.post("/api/v1/adaptacoes", json={**BASE, "documento_id": "doc-1"}, headers=AUTH),
        501,
        "NAO_IMPLEMENTADO",
    )


def test_500_formato_padrao():
    app_erro = create_app()

    @app_erro.get("/boom")
    def boom():
        raise RuntimeError("segredo interno")

    r = TestClient(app_erro, raise_server_exceptions=False).get("/boom")
    _confere(r, 500, "ERRO_INTERNO")
    assert "segredo interno" not in r.text


def test_request_id_reaproveita_o_do_cliente(client):
    r = client.get("/api/v1/perfil", headers={"X-Request-ID": "abc-123"})
    assert r.json()["request_id"] == "abc-123" and r.headers["X-Request-ID"] == "abc-123"


def test_request_id_gerado_quando_ausente(client):
    assert client.get("/api/v1/perfil").json()["request_id"].startswith("req-")
