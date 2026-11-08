"""Correção de quiz (T13.1): compara as respostas com o gabarito salvo e concede XP."""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api._errors import ErroApi
from ..infra.db.models import Adaptacao, Usuario
from ..schemas.enums import FormatoSaida
from ..schemas.perfil import (
    FeedbackQuizItem,
    RespostaQuizItem,
    RespostasQuizResponse,
    TrilhaResumo,
)
from . import xp


@dataclass(frozen=True)
class Correcao:
    item_indice: int
    correta: bool
    justificativa: str


def corrigir(itens: list[dict], respostas: list[RespostaQuizItem]) -> list[Correcao]:
    """Lógica pura: compara cada resposta com o gabarito do item. Não toca no banco.

    Levanta ErroApi 400 se o índice não existe, se há índice repetido ou se a alternativa
    escolhida não é uma das alternativas da pergunta.
    """
    vistos: set[int] = set()
    resultado: list[Correcao] = []
    for r in respostas:
        if r.item_indice in vistos:
            raise ErroApi(400, "REQUISICAO_INVALIDA", f"item_indice {r.item_indice} repetido.")
        vistos.add(r.item_indice)
        if r.item_indice >= len(itens):
            raise ErroApi(
                400,
                "REQUISICAO_INVALIDA",
                f"item_indice {r.item_indice} não existe (o quiz tem {len(itens)} perguntas).",
            )
        item = itens[r.item_indice]
        ids = {a["id"] for a in item.get("alternativas", [])}
        if r.alternativa_escolhida not in ids:
            raise ErroApi(
                400,
                "REQUISICAO_INVALIDA",
                f"Alternativa '{r.alternativa_escolhida}' não existe na pergunta {r.item_indice}.",
            )
        certa = item.get("resposta_correta")
        if not certa:
            raise ErroApi(
                500, "ERRO_IA", "Este quiz foi salvo sem gabarito e não pode ser corrigido."
            )
        resultado.append(
            Correcao(
                item_indice=r.item_indice,
                correta=r.alternativa_escolhida == certa,
                justificativa=item.get("justificativa") or "",
            )
        )
    return resultado


def buscar_adaptacao(db: Session, usuario: Usuario, adaptacao_id: str) -> Adaptacao:
    """Carrega a adaptação do próprio usuário; id inválido, inexistente ou alheio dá 404."""
    try:
        id_ = uuid.UUID(adaptacao_id)
    except ValueError:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Adaptação não encontrada.") from None
    adaptacao = db.scalars(
        select(Adaptacao).where(
            Adaptacao.adaptacao_id == id_, Adaptacao.usuario_id == usuario.usuario_id
        )
    ).first()
    if adaptacao is None:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Adaptação não encontrada.")
    return adaptacao


def responder_quiz(
    db: Session, usuario: Usuario, adaptacao_id: str, respostas: list[RespostaQuizItem]
) -> RespostasQuizResponse:
    adaptacao = buscar_adaptacao(db, usuario, adaptacao_id)
    if adaptacao.formato_saida != FormatoSaida.QUIZ.value:
        # Em v1 só o formato Quiz oferece validação (e XP).
        raise ErroApi(400, "REQUISICAO_INVALIDA", "Só adaptações no formato Quiz têm perguntas.")

    itens = adaptacao.resultado["conteudo_adaptado"]["itens"]
    correcoes = corrigir(itens, respostas)

    acertos = [c.item_indice for c in correcoes if c.correta]
    erradas = [c.item_indice for c in correcoes if not c.correta]
    # Resultado e XP na mesma transação (RNF-14).
    xp_ganho = xp.registrar_quiz(db, usuario, adaptacao.adaptacao_id, acertos, erradas)
    perfil = xp.obter_perfil(db, usuario)
    db.commit()

    demo = xp.modo_demo()
    nivel = xp.nivel_de(perfil.nivel_atual)
    return RespostasQuizResponse(
        acertos=len(acertos),
        total=len(correcoes),
        percentual_acerto=round(len(acertos) / len(correcoes) * 100, 1),
        itens_errados=erradas,
        xp_ganho=xp_ganho,
        feedback=[
            FeedbackQuizItem(
                item_indice=c.item_indice, correta=c.correta, justificativa=c.justificativa
            )
            for c in correcoes
        ],
        trilha_evolucao=TrilhaResumo(
            nivel_atual=nivel,
            xp_total=perfil.xp_total,
            teste_nivel_disponivel=xp.teste_nivel_disponivel(nivel, perfil.xp_total, demo),
        ),
    )
