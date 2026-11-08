"""T13 no PostgreSQL: gerar -> responder quiz -> conferir eventos_xp e perfis_evolucao."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api._deps import get_current_user, get_db
from app.infra.db.models import Adaptacao, EventoXP, PerfilEvolucao, Usuario
from app.main import app
from app.services import xp

pytestmark = pytest.mark.integration

AUTH = {"Authorization": "Bearer x"}
BASE = {
    "documento_titulo": "Intro a APIs",
    "documento_conteudo": "Uma API é um contrato entre sistemas. " * 5,
    "perfil_destinatario": "Iniciante",
    "nicho_setor": "Geral",
    "nivel_detalhe": "Didatico",
}


def _quiz_json() -> str:
    def item(n, certa):
        return {
            "pergunta": f"pergunta {n}?",
            "alternativas": [{"id": "a", "texto": "x"}, {"id": "b", "texto": "y"}],
            "resposta_correta": certa,
            "justificativa": f"porque {certa}",
            "conceito_ref": "c",
            "fontes_chunks": ["chunk-001"],
        }

    return json.dumps(
        {
            "titulo": "Quiz",
            "introducao_contextualizada": "I",
            "tempo_estimado_estudo_minutos": 5,
            "conceitos_chave": ["c"],
            "pre_requisitos": [],
            "itens": [item(0, "a"), item(1, "b")],
        }
    )


def _flash_json() -> str:
    return json.dumps(
        {
            "titulo": "F",
            "introducao_contextualizada": "I",
            "tempo_estimado_estudo_minutos": 5,
            "conceitos_chave": ["c"],
            "pre_requisitos": [],
            "itens": [
                {
                    "frente": "f",
                    "verso": "v",
                    "dica_didatica": "d",
                    "conceito_ref": "c",
                    "fontes_chunks": ["chunk-001"],
                }
            ],
        }
    )


class LLMFalso:
    nome, modelo = "falso", "falso-1"

    def __init__(self, texto):
        self.texto = texto

    def gerar_json(self, sistema, usuario, schema):
        return self.texto


@pytest.fixture
def api(db_session, usuario, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app), monkeypatch


def _gerar(api, formato="Quiz", variante=0, **extra):
    """Gera uma adaptação. `variante` muda o texto do documento: o T12 tem cache, e a mesma
    requisição repetida devolve a adaptação já salva (sem XP novo)."""
    cliente, mp = api
    texto = _quiz_json() if formato == "Quiz" else _flash_json()
    mp.setattr("app.api.adaptacoes.criar_cadeia", lambda settings: [LLMFalso(texto)])
    corpo = {
        **BASE,
        "documento_conteudo": BASE["documento_conteudo"] + f" Variante {variante}.",
        "formato_saida": formato,
    }
    return cliente.post("/api/v1/adaptacoes", json=corpo, headers=AUTH, **extra)


def _xp_total(db, usuario):
    return db.scalar(
        select(PerfilEvolucao.xp_total).where(PerfilEvolucao.usuario_id == usuario.usuario_id)
    )


def _eventos(db, usuario, tipo):
    return db.scalars(
        select(EventoXP).where(EventoXP.usuario_id == usuario.usuario_id, EventoXP.tipo == tipo)
    ).all()


def _enviar_quiz(cliente, adaptacao_id, *pares):
    corpo = {"respostas": [{"item_indice": i, "alternativa_escolhida": a} for i, a in pares]}
    return cliente.post(f"/api/v1/adaptacoes/{adaptacao_id}/respostas", json=corpo, headers=AUTH)


def test_geracao_salva_adaptacao_e_da_5_xp(api, db_session, usuario):
    r = _gerar(api)
    assert r.status_code == 200, r.text
    corpo = r.json()
    adaptacao_id = corpo["adaptacao_id"]
    # a resposta esconde o gabarito, mas o banco guarda o JSON completo
    assert corpo["conteudo_adaptado"]["itens"][0]["resposta_correta"] is None
    salva = db_session.get(Adaptacao, uuid.UUID(adaptacao_id))
    assert salva.resultado["conteudo_adaptado"]["itens"][0]["resposta_correta"] == "a"
    assert salva.formato_saida == "Quiz" and salva.usuario_id == usuario.usuario_id
    # XP: 1 evento de 5 e perfil atualizado
    eventos = _eventos(db_session, usuario, "geracao_conteudo")
    assert [(e.xp, e.item_indice) for e in eventos] == [(5, None)]
    assert _xp_total(db_session, usuario) == 5
    assert corpo["trilha_evolucao"]["xp_ganho_nesta_sessao"] == 5
    assert corpo["trilha_evolucao"]["xp_disponivel_ao_validar"] == 30  # 2 perguntas x 15


def test_flashcards_tambem_da_xp_mas_sem_xp_de_validacao(api, db_session, usuario):
    corpo = _gerar(api, "Flashcards").json()
    assert corpo["trilha_evolucao"]["xp_disponivel_ao_validar"] == 0
    assert _xp_total(db_session, usuario) == 5


def test_sem_teto_diario_por_padrao(api, db_session, usuario):
    for i in range(4):
        assert _gerar(api, variante=i).status_code == 200
    assert len(_eventos(db_session, usuario, "geracao_conteudo")) == 4
    assert _xp_total(db_session, usuario) == 20
    assert db_session.scalar(select(func.count()).select_from(Adaptacao)) == 4


def test_teto_diario_quando_configurado(api, db_session, usuario, monkeypatch):
    monkeypatch.setattr(xp, "TETO_GERACOES_POR_DIA", 3)
    for i in range(4):
        assert _gerar(api, variante=i).status_code == 200
    assert len(_eventos(db_session, usuario, "geracao_conteudo")) == 3
    assert _xp_total(db_session, usuario) == 15


def test_cache_hit_devolve_o_mesmo_id_e_nao_da_xp(api, db_session, usuario):
    primeira = _gerar(api).json()
    segunda = _gerar(api).json()  # mesma requisição: vem do cache do T12
    assert segunda["cache_hit"] is True
    assert segunda["adaptacao_id"] == primeira["adaptacao_id"]
    assert segunda["trilha_evolucao"]["xp_ganho_nesta_sessao"] == 0
    assert segunda["trilha_evolucao"]["xp_total"] == 5
    assert len(_eventos(db_session, usuario, "geracao_conteudo")) == 1
    assert _xp_total(db_session, usuario) == 5


def test_reprocessar_mantem_o_id_e_nao_da_xp(api, db_session, usuario):
    primeira = _gerar(api).json()
    de_novo = _gerar(api, params={"forcar_reprocessamento": "true"}).json()
    assert de_novo["cache_hit"] is False
    assert de_novo["adaptacao_id"] == primeira["adaptacao_id"]
    assert de_novo["trilha_evolucao"]["xp_ganho_nesta_sessao"] == 0
    assert _xp_total(db_session, usuario) == 5


def test_acerto_da_15_erro_tira_2_e_reenvio_nao_repete(api, db_session, usuario):
    cliente, _ = api
    adaptacao_id = _gerar(api).json()["adaptacao_id"]  # 5 XP
    # Q0 certa (a), Q1 errada (a; a certa é b)
    r = _enviar_quiz(cliente, adaptacao_id, (0, "a"), (1, "a"))
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert (corpo["acertos"], corpo["total"], corpo["percentual_acerto"]) == (1, 2, 50.0)
    assert corpo["itens_errados"] == [1] and corpo["xp_ganho"] == 13  # +15 -2
    assert corpo["feedback"][1] == {
        "item_indice": 1,
        "correta": False,
        "justificativa": "porque b",
    }
    assert corpo["trilha_evolucao"]["xp_total"] == 18
    assert [(e.xp, e.item_indice) for e in _eventos(db_session, usuario, "acerto_quiz")] == [
        (15, 0)
    ]
    assert [(e.xp, e.item_indice) for e in _eventos(db_session, usuario, "erro_quiz")] == [(-2, 1)]
    assert _xp_total(db_session, usuario) == 18

    # reenviar as mesmas respostas não pontua nem pune de novo
    assert _enviar_quiz(cliente, adaptacao_id, (0, "a"), (1, "a")).json()["xp_ganho"] == 0
    assert _xp_total(db_session, usuario) == 18

    # corrigir a pergunta errada: o acerto soma +15 e a penalidade antiga continua
    r = _enviar_quiz(cliente, adaptacao_id, (1, "b"))
    assert (r.json()["xp_ganho"], r.json()["trilha_evolucao"]["xp_total"]) == (15, 33)


def test_errar_depois_de_acertar_nao_pune(api, db_session, usuario):
    cliente, _ = api
    adaptacao_id = _gerar(api).json()["adaptacao_id"]
    assert _enviar_quiz(cliente, adaptacao_id, (0, "a")).json()["xp_ganho"] == 15
    assert _enviar_quiz(cliente, adaptacao_id, (0, "b")).json()["xp_ganho"] == 0
    assert _eventos(db_session, usuario, "erro_quiz") == []
    assert _xp_total(db_session, usuario) == 20


def test_xp_total_nunca_fica_negativo(api, db_session, usuario):
    cliente, _ = api
    adaptacao_id = _gerar(api).json()["adaptacao_id"]  # cria o perfil com 5 XP
    db_session.get(PerfilEvolucao, usuario.usuario_id).xp_total = 1
    db_session.commit()
    # as duas erradas: a 1ª tira 1 (só havia 1), a 2ª tira 0
    r = _enviar_quiz(cliente, adaptacao_id, (0, "b"), (1, "a"))
    assert r.json()["xp_ganho"] == -1
    assert _xp_total(db_session, usuario) == 0
    erros = _eventos(db_session, usuario, "erro_quiz")
    assert sorted((e.item_indice, e.xp) for e in erros) == [(0, -1), (1, 0)]
    # reenviar não tira nada
    assert _enviar_quiz(cliente, adaptacao_id, (0, "b"), (1, "a")).json()["xp_ganho"] == 0
    assert _xp_total(db_session, usuario) == 0


def test_teste_de_nivel_libera_ao_chegar_a_100_xp(api, db_session, usuario):
    cliente, _ = api
    adaptacao_id = _gerar(api).json()["adaptacao_id"]  # cria o perfil com 5 XP
    db_session.get(PerfilEvolucao, usuario.usuario_id).xp_total = 90
    db_session.commit()
    r = _enviar_quiz(cliente, adaptacao_id, (0, "a"))  # +15 -> 105
    assert r.json()["trilha_evolucao"] == {
        "nivel_atual": "Iniciante",
        "xp_total": 105,
        "teste_nivel_disponivel": True,
    }


def test_upload_da_10_xp_so_na_primeira_vez(api, db_session, usuario, monkeypatch):
    cliente, mp = api
    mp.setattr(
        "app.services.ingestao.gerar_embeddings",
        lambda textos, *, tipo_tarefa: [[1.0] + [0.0] * 3071 for _ in textos],
    )

    def enviar():
        return cliente.post(
            "/api/v1/documentos/upload",
            files={"arquivo": ("notas.txt", b"Conteudo de estudo sobre APIs.", "text/plain")},
        )

    primeiro = enviar()
    assert (primeiro.status_code, primeiro.json()["xp_ganho"]) == (201, 10)
    assert _xp_total(db_session, usuario) == 10
    eventos = _eventos(db_session, usuario, "upload_documento")
    assert [(e.xp, str(e.documento_id)) for e in eventos] == [(10, primeiro.json()["documento_id"])]

    segundo = enviar()  # mesmo arquivo (mesmo hash): 409 duplicado, sem XP
    assert (segundo.status_code, segundo.json()["codigo"]) == (409, "DOCUMENTO_DUPLICADO")
    assert _xp_total(db_session, usuario) == 10
    assert len(_eventos(db_session, usuario, "upload_documento")) == 1


def test_erros_da_rota_de_respostas(api, db_session, usuario):
    cliente, _ = api
    um_item = {"respostas": [{"item_indice": 0, "alternativa_escolhida": "a"}]}
    # id que não é UUID e id que não existe: 404
    for ruim in ("nao-e-uuid", str(uuid.uuid4())):
        r = cliente.post(f"/api/v1/adaptacoes/{ruim}/respostas", json=um_item, headers=AUTH)
        assert (r.status_code, r.json()["codigo"]) == (404, "RECURSO_NAO_ENCONTRADO")

    # adaptação de outro usuário: 404, sem vazar que existe
    outro = Usuario(
        nome="O", email=f"{uuid.uuid4().hex}@x.com", senha_hash="x", nivel_declarado="Iniciante"
    )
    db_session.add(outro)
    db_session.commit()
    adaptacao_id = _gerar(api).json()["adaptacao_id"]
    app.dependency_overrides[get_current_user] = lambda: outro
    r = cliente.post(f"/api/v1/adaptacoes/{adaptacao_id}/respostas", json=um_item, headers=AUTH)
    assert r.status_code == 404
    app.dependency_overrides[get_current_user] = lambda: usuario

    # alternativa inexistente e índice fora do quiz: 400
    for envio in (
        {"respostas": [{"item_indice": 0, "alternativa_escolhida": "z"}]},
        {"respostas": [{"item_indice": 9, "alternativa_escolhida": "a"}]},
    ):
        r = cliente.post(f"/api/v1/adaptacoes/{adaptacao_id}/respostas", json=envio, headers=AUTH)
        assert (r.status_code, r.json()["codigo"]) == (400, "REQUISICAO_INVALIDA")

    # adaptação que não é Quiz: 400
    flash_id = _gerar(api, "Flashcards").json()["adaptacao_id"]
    r = cliente.post(f"/api/v1/adaptacoes/{flash_id}/respostas", json=um_item, headers=AUTH)
    assert (r.status_code, r.json()["codigo"]) == (400, "REQUISICAO_INVALIDA")
    assert _xp_total(db_session, usuario) == 10  # só as 2 gerações (2 x 5) pontuaram
