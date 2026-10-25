"""T1.8 — todas as rotas da seção 2 do contrato aparecem no OpenAPI."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app, create_app

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


def test_post_documentos_documenta_o_corpo():
    spec = client.get("/openapi.json").json()
    corpo = spec["paths"]["/api/v1/documentos"]["post"]["requestBody"]
    assert corpo["required"] is True
    assert set(corpo["content"]) == {"multipart/form-data", "application/json"}
    json_schema = corpo["content"]["application/json"]["schema"]
    assert set(json_schema["required"]) == {"titulo", "conteudo"}


def test_openapi_commitado_esta_atualizado():
    arquivo = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
    if not arquivo.exists():
        pytest.skip("docs/openapi.json fora do container; rode no host ou no CI")
    assert json.loads(arquivo.read_text(encoding="utf-8")) == create_app().openapi(), (
        "docs/openapi.json desatualizado: rode `python -m scripts.export_openapi`"
    )
