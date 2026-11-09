"""Rotas do teste de nível e promoção na trilha de gamificação."""

import logging
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..agents.adaptacao import AgenteFalhouError, executar_cadeia
from ..config import get_settings
from ..infra import criar_cadeia
from ..infra.db.models import PerfilEvolucao, TesteNivel, Usuario
from ..schemas.itens import Alternativa
from ..schemas.perfil import (
    FeedbackTesteItem,
    PerguntaTeste,
    RespostasTesteRequest,
    RespostasTesteResponse,
    TesteNivelResponse,
)
from ..services import xp
from ._deps import get_current_user, get_db
from ._errors import ErroApi

router = APIRouter(prefix="/testes-nivel", tags=["testes-nivel"])
logger = logging.getLogger(__name__)


class _PerguntaGerada(BaseModel):
    """Formato privado da pergunta, incluindo gabarito que nunca vai ao cliente."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    pergunta: str = Field(min_length=1)
    alternativas: list[Alternativa] = Field(min_length=2)
    resposta_correta: str = Field(min_length=1)
    justificativa: str = Field(min_length=1)
    conceito_ref: str = Field(min_length=1)

    @model_validator(mode="after")
    def _gabarito_valido(self) -> "_PerguntaGerada":
        if self.resposta_correta not in {alternativa.id for alternativa in self.alternativas}:
            raise ValueError("resposta_correta deve identificar uma alternativa existente.")
        return self


class _QuizNivelGerado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    perguntas: list[_PerguntaGerada] = Field(min_length=5, max_length=5)


def _perguntas_salvas(teste: TesteNivel) -> list[_PerguntaGerada]:
    perguntas_salvas = teste.perguntas.get("itens")
    if not isinstance(perguntas_salvas, list) or not perguntas_salvas:
        raise ErroApi(500, "ERRO_INTERNO", "O teste não contém perguntas válidas.")
    try:
        return [_PerguntaGerada.model_validate(pergunta) for pergunta in perguntas_salvas]
    except ValidationError as exc:
        raise ErroApi(500, "ERRO_INTERNO", "As perguntas salvas do teste são inválidas.") from exc


@router.post("", response_model=TesteNivelResponse, status_code=201)
def iniciar_teste(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TesteNivelResponse:
    perfil = xp.perfil_ou_padrao(db, current_user)
    nivel = xp.nivel_de(perfil.nivel_atual)
    modo_demo = xp.modo_demo()
    if not xp.teste_nivel_disponivel(nivel, perfil.xp_total, modo_demo):
        raise ErroApi(
            400,
            "REQUISICAO_INVALIDA",
            "XP insuficiente para iniciar o teste de nível.",
        )

    sistema = (
        "Você é um avaliador educacional. Gere exatamente cinco questões de múltipla escolha "
        "em português, adequadas ao nível informado. Cada pergunta deve ter um identificador "
        "único, alternativas com IDs curtos e distintos, uma resposta correta que corresponda "
        "a uma alternativa, justificativa e conceito_ref. Não inclua explicações fora do JSON."
    )
    usuario_prompt = (
        f"Gere um teste de nível para o nível atual {nivel.value}. "
        "Avalie conhecimentos gerais apropriados a esse nível, com quatro alternativas por questão."
    )

    try:
        resultado = executar_cadeia(
            criar_cadeia(get_settings()), sistema, usuario_prompt, _QuizNivelGerado
        )
    except AgenteFalhouError as exc:
        logger.warning("Falha ao gerar teste de nível: %s", exc)
        raise ErroApi(502, "LLM_INDISPONIVEL", "Não foi possível gerar o teste de nível.") from exc
    except Exception as exc:
        logger.exception("Erro inesperado ao gerar teste de nível")
        raise ErroApi(502, "LLM_INDISPONIVEL", "Não foi possível gerar o teste de nível.") from exc

    quiz_gerado = _QuizNivelGerado.model_validate(resultado.saida)
    perguntas = quiz_gerado.perguntas
    ids = [pergunta.id for pergunta in perguntas]
    if len(ids) != len(set(ids)):
        raise ErroApi(502, "LLM_INDISPONIVEL", "A IA gerou identificadores repetidos.")

    tentativas_anteriores = (
        db.scalar(
            select(func.count())
            .select_from(TesteNivel)
            .where(
                TesteNivel.usuario_id == current_user.usuario_id,
                TesteNivel.nivel_avaliado == nivel.value,
            )
        )
        or 0
    )

    teste = TesteNivel(
        usuario_id=current_user.usuario_id,
        nivel_avaliado=nivel.value,
        perguntas={"itens": [pergunta.model_dump(mode="json") for pergunta in perguntas]},
        tentativa=tentativas_anteriores + 1,
    )
    db.add(teste)
    try:
        db.commit()
        db.refresh(teste)
    except Exception as exc:
        db.rollback()
        logger.exception("Falha ao persistir teste de nível")
        raise ErroApi(500, "ERRO_INTERNO", "Não foi possível salvar o teste de nível.") from exc

    return TesteNivelResponse(
        teste_id=str(teste.teste_id),
        nivel_avaliado=nivel,
        tentativa=teste.tentativa,
        perguntas=[
            PerguntaTeste(
                id=pergunta.id,
                pergunta=pergunta.pergunta,
                alternativas=pergunta.alternativas,
                conceito_ref=pergunta.conceito_ref,
            )
            for pergunta in perguntas
        ],
    )


@router.post(
    "/{teste_id}/respostas",
    response_model=RespostasTesteResponse,
)
def responder_teste(
    teste_id: str,
    payload: RespostasTesteRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RespostasTesteResponse:
    try:
        teste_uuid = uuid.UUID(teste_id)
    except ValueError:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "teste_id inválido.") from None

    teste = db.scalars(
        select(TesteNivel).where(
            TesteNivel.teste_id == teste_uuid,
            TesteNivel.usuario_id == current_user.usuario_id,
        )
    ).first()
    if teste is None:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Teste de nível não encontrado.")
    if teste.respostas or teste.aprovado is not None:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "Este teste já foi respondido.")

    perguntas = _perguntas_salvas(teste)
    respostas_por_id: dict[str, str] = {}
    for resposta in payload.respostas:
        if resposta.pergunta_id in respostas_por_id:
            raise ErroApi(
                400,
                "REQUISICAO_INVALIDA",
                f"A pergunta '{resposta.pergunta_id}' foi respondida mais de uma vez.",
            )
        respostas_por_id[resposta.pergunta_id] = resposta.alternativa_escolhida

    perguntas_por_id = {pergunta.id: pergunta for pergunta in perguntas}
    if any(pergunta_id not in perguntas_por_id for pergunta_id in respostas_por_id):
        raise ErroApi(400, "REQUISICAO_INVALIDA", "A resposta contém uma pergunta inválida.")
    if set(respostas_por_id) != set(perguntas_por_id):
        raise ErroApi(400, "REQUISICAO_INVALIDA", "É necessário responder todas as perguntas.")

    feedback: list[FeedbackTesteItem] = []
    conceitos_fracos: list[str] = []
    acertos = 0
    for pergunta in perguntas:
        pergunta_id = pergunta.id
        alternativa_escolhida = respostas_por_id.get(pergunta_id)
        if alternativa_escolhida is None:
            continue

        ids_alternativas = {alternativa.id for alternativa in pergunta.alternativas}
        if alternativa_escolhida not in ids_alternativas:
            raise ErroApi(
                400,
                "REQUISICAO_INVALIDA",
                f"Alternativa inválida para a pergunta '{pergunta_id}'.",
            )

        correta = alternativa_escolhida == pergunta.resposta_correta
        if correta:
            acertos += 1
        else:
            conceito = pergunta.conceito_ref
            if conceito and conceito not in conceitos_fracos:
                conceitos_fracos.append(conceito)
        feedback.append(
            FeedbackTesteItem(
                pergunta_id=pergunta_id,
                correta=correta,
                justificativa=pergunta.justificativa,
            )
        )

    percentual = round(acertos / len(perguntas), 3)
    perfil = db.get(PerfilEvolucao, current_user.usuario_id)
    if perfil is None:
        perfil = xp.obter_perfil(db, current_user)

    nivel_atual = xp.nivel_de(perfil.nivel_atual)
    teste_corresponde_ao_nivel = nivel_atual.value == teste.nivel_avaliado
    tem_xp = xp.teste_nivel_disponivel(nivel_atual, perfil.xp_total, xp.modo_demo())
    aprovado = percentual >= xp.LIMIAR_APROVACAO and teste_corresponde_ao_nivel and tem_xp

    if aprovado:
        indice_nivel = xp.ORDEM_NIVEIS.index(nivel_atual)
        if indice_nivel + 1 < len(xp.ORDEM_NIVEIS):
            perfil.nivel_atual = xp.ORDEM_NIVEIS[indice_nivel + 1].value
        else:
            aprovado = False

    teste.respostas = respostas_por_id
    teste.percentual_dominio = percentual
    teste.aprovado = aprovado

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Falha ao persistir respostas do teste de nível")
        raise ErroApi(500, "ERRO_INTERNO", "Não foi possível salvar o resultado do teste.") from exc

    return RespostasTesteResponse(
        percentual_dominio=percentual,
        aprovado=aprovado,
        nivel_atual=xp.nivel_de(perfil.nivel_atual),
        conceitos_fracos=conceitos_fracos,
        feedback=feedback,
    )
