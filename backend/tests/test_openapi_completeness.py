"""T1.8 — todas as rotas da seção 2 do contrato aparecem no OpenAPI."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_publicado():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec["info"]["title"] == "AdaptAI"


def test_todas_as_rotas_da_secao_2_presentes():
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    esperado = {
        "/api/v1/auth/cadastro": {"post"},
        "/api/v1/auth/login": {"post"},
        "/api/v1/auth/logout": {"post"},
        "/api/v1/usuarios/me": {"get"},
        "/api/v1/documentos": {"post", "get"},
        "/api/v1/documentos/{documento_id}": {"get"},
        "/api/v1/adaptacoes": {"post", "get"},
        "/api/v1/adaptacoes/{adaptacao_id}": {"get"},
        "/api/v1/adaptacoes/{adaptacao_id}/respostas": {"post"},
        "/api/v1/perfil": {"get"},
        "/api/v1/testes-nivel": {"post"},
        "/api/v1/testes-nivel/{teste_id}/respostas": {"post"},
        "/api/v1/health": {"get"},
    }
    for rota, metodos in esperado.items():
        assert rota in paths, f"Rota {rota} ausente no OpenAPI"
        for metodo in metodos:
            assert metodo in paths[rota], f"Metodo {metodo} ausente em {rota}"


def test_schemas_chave_estao_no_openapi():
    spec = client.get("/openapi.json").json()
    schemas = spec["components"]["schemas"]
    for nome in ("AdaptacaoResponse", "AdaptacaoRequest", "DocumentoResponse", "ErroResposta"):
        assert nome in schemas, f"Schema {nome} ausente"
