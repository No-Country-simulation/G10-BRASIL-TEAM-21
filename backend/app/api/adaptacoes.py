import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra import criar_cadeia
from ..infra.db.models import Adaptacao, Documento, Usuario
from ..schemas.adaptacao import AdaptacaoRequest, AdaptacaoResponse
from ..schemas.common import ErroResposta
from ..schemas.enums import DominioConhecimento, FormatoSaida, Nicho, PerfilSaida, StatusUpload
from ..schemas.listagens import AdaptacaoResumo, AdaptacoesListResponse
from ..schemas.perfil import RespostasQuizRequest, RespostasQuizResponse
from ..services.adaptacao import _resposta_do_cache, gerar_adaptacao
from ..services.quiz import responder_quiz as corrigir_quiz
from ._deps import get_current_user, get_db
from ._errors import ErroApi

router = APIRouter(prefix="/adaptacoes", tags=["adaptacoes"])
logger = logging.getLogger(__name__)

ERR: dict[int | str, dict[str, Any]] = {400: {"model": ErroResposta}, 502: {"model": ErroResposta}}


@router.post("", response_model=AdaptacaoResponse, responses=ERR)
def criar_adaptacao(
    request: Request,
    payload: AdaptacaoRequest,
    incluir_gabarito: bool = Query(False),
    forcar_reprocessamento: bool = Query(False),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdaptacaoResponse:
    """Aciona o Agente para gerar a adaptação usando RAG e LLM."""
    if not payload.documento_id and not payload.documento_conteudo:
        raise ErroApi(
            400, "REQUISICAO_INVALIDA", "É necessário enviar o documento_id ou o conteúdo."
        )

    try:
        settings = get_settings()
        cadeia = criar_cadeia(settings)
        request_id = getattr(request.state, "request_id", "req-desconhecido")

        resposta = gerar_adaptacao(
            db=db,
            usuario=current_user,
            payload=payload,
            cadeia=cadeia,
            request_id=request_id,
            incluir_gabarito=incluir_gabarito,
            forcar_reprocessamento=forcar_reprocessamento,
        )
        return resposta

    except ErroApi as e:
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado na rota de adaptação: {str(e)}", exc_info=True)
        raise ErroApi(500, "ERRO_IA", "Ocorreu um erro interno ao processar a adaptação.") from e


@router.get("", response_model=AdaptacoesListResponse)
async def listar_adaptacoes(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdaptacoesListResponse:
    """Lista as adaptações do usuário, das mais recentes para as mais antigas."""
    filtro_usuario = Adaptacao.usuario_id == current_user.usuario_id
    total = db.scalar(select(func.count()).select_from(Adaptacao).where(filtro_usuario)) or 0

    consulta = (
        select(Adaptacao, Documento.titulo, Documento.dominio_conhecimento)
        .join(Documento, Documento.documento_id == Adaptacao.documento_id)
        .where(filtro_usuario)
        .order_by(Adaptacao.criado_em.desc(), Adaptacao.adaptacao_id.desc())
        .limit(limite)
        .offset(deslocamento)
    )
    linhas = db.execute(consulta).all()

    return AdaptacoesListResponse(
        itens=[
            AdaptacaoResumo(
                adaptacao_id=str(adaptacao.adaptacao_id),
                documento_id=str(adaptacao.documento_id),
                titulo=titulo,
                perfil_aplicado=PerfilSaida(adaptacao.perfil_destinatario),
                formato_gerado=FormatoSaida(adaptacao.formato_saida),
                nicho_aplicado=Nicho(adaptacao.nicho_setor),
                dominio_conhecimento=(
                    DominioConhecimento(dominio) if dominio is not None else None
                ),
                ancoragem_fonte_score=float(adaptacao.ancoragem_fonte_score),
                status_upload=StatusUpload(adaptacao.status_upload),
                criado_em=adaptacao.criado_em,
            )
            for adaptacao, titulo, dominio in linhas
        ],
        total=total,
    )


@router.get(
    "/{adaptacao_id}",
    response_model=AdaptacaoResponse,
    responses={400: {"model": ErroResposta}, 404: {"model": ErroResposta}},
)
async def obter_adaptacao(
    adaptacao_id: str,
    request: Request,
    incluir_gabarito: bool = Query(False),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdaptacaoResponse:
    """Retorna uma adaptação salva pertencente ao usuário autenticado."""
    try:
        adaptacao_uuid = uuid.UUID(adaptacao_id)
    except ValueError:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "adaptacao_id inválido.") from None

    adaptacao = db.scalars(
        select(Adaptacao).where(
            Adaptacao.adaptacao_id == adaptacao_uuid,
            Adaptacao.usuario_id == current_user.usuario_id,
        )
    ).first()
    if adaptacao is None:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Adaptação não encontrada.")

    request_id = getattr(request.state, "request_id", "req-desconhecido")
    return _resposta_do_cache(adaptacao, request_id, incluir_gabarito)


@router.post(
    "/{adaptacao_id}/respostas",
    response_model=RespostasQuizResponse,
    responses=ERR,
)
def responder_quiz(
    adaptacao_id: str,
    payload: RespostasQuizRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RespostasQuizResponse:
    """Corrige o quiz com o gabarito salvo, devolve a nota e concede XP (T13.1 e T13.2)."""
    return corrigir_quiz(db, current_user, adaptacao_id, payload.respostas)
