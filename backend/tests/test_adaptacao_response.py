"""T1.8 — consistência entre formato_gerado e itens."""

import pytest
from pydantic import ValidationError

from app.schemas.adaptacao import (
    AdaptacaoResponse,
    ArmazenamentoOCI,
    AvaliacaoQualidade,
    ConteudoAdaptado,
    Metadados,
    ocultar_gabarito,
)
from app.schemas.enums import (
    DominioConhecimento,
    FormatoSaida,
    Nicho,
    Nivel,
    NivelDetalhe,
    PerfilSaida,
    StatusUpload,
)
from app.schemas.itens import Alternativa, ItemFlashcard, ItemQuiz  # <-- Importei Alternativa


def _metadados(formato: FormatoSaida) -> Metadados:
    return Metadados(
        perfil_aplicado=PerfilSaida.INICIANTE,
        formato_gerado=formato,
        nicho_aplicado=Nicho.GERAL,
        dominio_conhecimento=DominioConhecimento.TI,
        nivel_detalhe=NivelDetalhe.DIDATICO,
        tempo_estimado_estudo_minutos=5,
        conceitos_chave=["VCN"],
        pre_requisitos=[],
        nivel_documento_estimado=Nivel.INTERMEDIARIO,
        alerta_descompasso=True,
    )


def _avaliacao() -> AvaliacaoQualidade:
    return AvaliacaoQualidade(
        ancoragem_fonte_score=0.98,
        clareza_pedagogica="Alta",
        chunks_utilizados=4,
        busca_hibrida=True,
    )


def _armazenamento() -> ArmazenamentoOCI:
    return ArmazenamentoOCI(
        bucket="adaptai-conteudos-educativos",
        objeto_id="adaptacoes/u/x.json",
        documento_original_id="documentos/u/d/o.md",
        status_upload=StatusUpload.CONCLUIDO,
    )


def _resposta(**extra):
    return AdaptacaoResponse(
        request_id="r1",
        metadados=_metadados(FormatoSaida.FLASHCARDS),
        conteudo_adaptado=ConteudoAdaptado(titulo="T", introducao_contextualizada="i", itens=[]),
        avaliacao_qualidade=_avaliacao(),
        **extra,
    )


def test_flashcard_com_item_flashcard_ok():
    item = ItemFlashcard(
        frente="f",
        verso="v",
        dica_didatica="d",
        conceito_ref="VCN",
        fontes_chunks=["chunk-001"],
    )
    resp = AdaptacaoResponse(
        request_id="r1",
        metadados=_metadados(FormatoSaida.FLASHCARDS),
        conteudo_adaptado=ConteudoAdaptado(
            titulo="T",
            introducao_contextualizada="i",
            itens=[item],
        ),
        avaliacao_qualidade=_avaliacao(),
        armazenamento_oci=_armazenamento(),
    )
    assert resp.cache_hit is False

    # O isinstance avisa ao VS Code que o item é um Flashcard antes de acessar o .frente
    item_gerado = resp.conteudo_adaptado.itens[0]
    assert isinstance(item_gerado, ItemFlashcard)
    assert item_gerado.frente == "f"


def test_flashcard_com_item_quiz_falha():
    item_errado = ItemQuiz(
        pergunta="p",
        # Instanciando o objeto Alternativa em vez de passar um dicionário
        alternativas=[Alternativa(id="a", texto="A")],
        resposta_correta="a",
        justificativa="j",
        conceito_ref="VCN",
        fontes_chunks=["chunk-001"],
    )
    with pytest.raises(ValidationError):
        AdaptacaoResponse(
            request_id="r1",
            metadados=_metadados(FormatoSaida.FLASHCARDS),
            conteudo_adaptado=ConteudoAdaptado(
                titulo="T",
                introducao_contextualizada="i",
                itens=[item_errado],
            ),
            avaliacao_qualidade=_avaliacao(),
        )


def _quiz_item(**kw):
    base = dict(
        pergunta="p",
        alternativas=[Alternativa(id="a", texto="A"), Alternativa(id="b", texto="B")],
        conceito_ref="VCN",
        fontes_chunks=["chunk-001"],
    )
    return ItemQuiz(**base, **kw)


def test_quiz_sem_gabarito_e_valido():
    assert _quiz_item().resposta_correta is None


def test_quiz_resposta_correta_precisa_existir():
    with pytest.raises(ValidationError):
        _quiz_item(resposta_correta="z", justificativa="j")


def test_ocultar_gabarito_remove_resposta_e_justificativa():
    resp = AdaptacaoResponse(
        request_id="r1",
        metadados=_metadados(FormatoSaida.QUIZ),
        conteudo_adaptado=ConteudoAdaptado(
            titulo="T",
            introducao_contextualizada="i",
            itens=[_quiz_item(resposta_correta="a", justificativa="j")],
        ),
        avaliacao_qualidade=_avaliacao(),
        armazenamento_oci=_armazenamento(),  # criado no passo 3
    )
    item = ocultar_gabarito(resp).conteudo_adaptado.itens[0]
    assert item.resposta_correta is None and item.justificativa is None
    assert resp.conteudo_adaptado.itens[0].resposta_correta == "a"  # original intacto


def test_armazenamento_oci_e_obrigatorio():
    with pytest.raises(ValidationError):
        _resposta()


def test_analogias_microlearning_e_trilha_podem_ser_nulos():
    r = _resposta(armazenamento_oci=_armazenamento())
    assert r.analogias is None and r.microlearning is None and r.trilha_evolucao is None
