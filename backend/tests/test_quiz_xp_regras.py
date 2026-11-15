"""T13: regras puras de correção de quiz e de XP. Não usam banco, rodam em qualquer ambiente."""

import json

import pytest
from pydantic import ValidationError

from app.api._errors import ErroApi
from app.infra.db.models import PerfilEvolucao
from app.schemas.adaptacao_output import SAIDA_POR_FORMATO
from app.schemas.enums import FormatoSaida, Nivel
from app.schemas.perfil import RespostaQuizItem
from app.services import xp
from app.services.quiz import corrigir

ITENS = [
    {
        "pergunta": "p0",
        "alternativas": [{"id": "a", "texto": "x"}, {"id": "b", "texto": "y"}],
        "resposta_correta": "a",
        "justificativa": "porque a",
    },
    {
        "pergunta": "p1",
        "alternativas": [{"id": "a", "texto": "x"}, {"id": "b", "texto": "y"}],
        "resposta_correta": "b",
        "justificativa": "porque b",
    },
]


def resp(indice, alt):
    return RespostaQuizItem(item_indice=indice, alternativa_escolhida=alt)


def test_corrige_acerto_e_erro_com_justificativa():
    r = corrigir(ITENS, [resp(0, "a"), resp(1, "a")])
    assert [(c.item_indice, c.correta) for c in r] == [(0, True), (1, False)]
    assert r[1].justificativa == "porque b"


@pytest.mark.parametrize(
    "respostas",
    [
        [resp(2, "a")],  # índice inexistente
        [resp(0, "z")],  # alternativa inexistente
        [resp(0, "a"), resp(0, "b")],  # índice repetido
    ],
)
def test_resposta_invalida_da_400(respostas):
    with pytest.raises(ErroApi) as e:
        corrigir(ITENS, respostas)
    assert (e.value.status, e.value.codigo) == (400, "REQUISICAO_INVALIDA")


def test_quiz_salvo_sem_gabarito_nao_e_corrigido():
    sem = [{**ITENS[0], "resposta_correta": None}]
    with pytest.raises(ErroApi) as e:
        corrigir(sem, [resp(0, "a")])
    assert e.value.status == 500


def _quiz(com_gabarito: bool) -> str:
    item = {
        "pergunta": "p?",
        "alternativas": [{"id": "a", "texto": "x"}, {"id": "b", "texto": "y"}],
        "conceito_ref": "c",
        "fontes_chunks": ["chunk-001"],
    }
    if com_gabarito:
        item |= {"resposta_correta": "a", "justificativa": "porque"}
    return json.dumps(
        {
            "titulo": "Q",
            "introducao_contextualizada": "I",
            "tempo_estimado_estudo_minutos": 5,
            "conceitos_chave": ["c"],
            "pre_requisitos": [],
            "itens": [item],
        }
    )


def test_llm_nao_pode_devolver_quiz_sem_gabarito():
    schema = SAIDA_POR_FORMATO[FormatoSaida.QUIZ]
    assert schema.model_validate_json(_quiz(True)).itens[0].resposta_correta == "a"
    with pytest.raises(ValidationError):
        schema.model_validate_json(_quiz(False))


# ---------- limiares e trilha ----------


def test_limiares_da_tabela_do_grupo():
    assert [xp.limiar_do_nivel(n) for n in Nivel] == [100, 300, 700, 1500, None]


def test_valores_de_xp_da_tabela_do_grupo():
    assert (xp.XP_UPLOAD, xp.XP_GERACAO, xp.XP_ACERTO_QUIZ, xp.PENALIDADE_ERRO_QUIZ) == (
        10,
        5,
        15,
        2,
    )


def test_modo_demo_divide_limiares_por_10():
    assert xp.limiar_do_nivel(Nivel.INICIANTE, modo_demo=True) == 10
    assert xp.limiar_do_nivel(Nivel.AVANCADO, modo_demo=True) == 150


def test_teste_de_nivel_libera_ao_atingir_o_limiar():
    assert not xp.teste_nivel_disponivel(Nivel.INICIANTE, 99)
    assert xp.teste_nivel_disponivel(Nivel.INICIANTE, 100)
    assert not xp.teste_nivel_disponivel(Nivel.ESPECIALISTA, 10_000)  # nível máximo


def test_trilha_calcula_progresso():
    perfil = PerfilEvolucao(nivel_atual="Iniciante", xp_total=60)
    t = xp.montar_trilha(perfil, xp_ganho_sessao=10)
    assert (t.xp_para_proximo_nivel, t.progresso_percentual, t.proximo_nivel) == (
        100,
        60.0,
        Nivel.BASICO,
    )
    assert t.xp_ganho_nesta_sessao == 10 and not t.teste_nivel_disponivel


def test_nivel_desconhecido_cai_em_iniciante():
    assert xp.nivel_de("Junior") == Nivel.INICIANTE
    assert xp.nivel_de(None) == Nivel.INICIANTE
