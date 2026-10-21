"""T1.8 — consistência entre formato_gerado e itens."""

import pytest
from pydantic import ValidationError

from app.schemas.adaptacao import (
    AdaptacaoResponse,
    AvaliacaoQualidade,
    ConteudoAdaptado,
    Metadados,
)
from app.schemas.enums import (
    DominioConhecimento,
    FormatoSaida,
    Nicho,
    Nivel,
    NivelDetalhe,
    PerfilSaida,
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
