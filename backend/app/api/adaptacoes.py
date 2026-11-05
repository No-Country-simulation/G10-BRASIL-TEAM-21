import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra import criar_cadeia
from ..infra.db.models import Adaptacao, Documento, Usuario
from ..schemas.adaptacao import AdaptacaoRequest, AdaptacaoResponse
from ..schemas.common import ErroResposta
from ..schemas.listagens import AdaptacaoResumo, AdaptacoesListResponse
from ..schemas.perfil import RespostasQuizRequest, RespostasQuizResponse

# ⚠️ CORREÇÃO DO IMPORT: O arquivo está em services, não em agents
from ..services.adaptacao import gerar_adaptacao
from ._deps import get_current_user, get_db
from ._errors import ErroApi, NaoImplementadoError

router = APIRouter(prefix="/adaptacoes", tags=["adaptacoes"])
logger = logging.getLogger(__name__)

ERR: dict[int | str, dict[str, Any]] = {501: {"model": ErroResposta}}


@router.post("", response_model=AdaptacaoResponse, responses=ERR)
async def criar_adaptacao(
    request: Request,  # Adicionado para pegar o request_id
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
        # 1. Instancia a cadeia de LLM (Gemini -> Groq)
        settings = get_settings()
        cadeia = criar_cadeia(settings)

        # 2. Pega o request_id do middleware
        request_id = getattr(request.state, "request_id", "req-desconhecido")

        # 3. Chama a função com os parâmetros EXATOS do print
        # Nota: A função é síncrona, então não usamos 'await'
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
        raise e  # Repassa erros de validação (400, 422, 502)
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
                perfil_aplicado=adaptacao.perfil_destinatario,
                formato_gerado=adaptacao.formato_saida,
                nicho_aplicado=adaptacao.nicho_setor,
                dominio_conhecimento=dominio,
                ancoragem_fonte_score=float(adaptacao.ancoragem_fonte_score),
                status_upload=adaptacao.status_upload,
                criado_em=adaptacao.criado_em,
            )
            for adaptacao, titulo, dominio in linhas
        ],
        total=total,
    )


@router.get("/{adaptacao_id}", response_model=AdaptacaoResponse, responses=ERR)
async def obter_adaptacao(
    adaptacao_id: str,
    incluir_gabarito: bool = Query(False),
    current_user: Usuario = Depends(get_current_user),
) -> AdaptacaoResponse:
    raise NaoImplementadoError()


@router.post(
    "/{adaptacao_id}/respostas",
    response_model=RespostasQuizResponse,
    responses=ERR,
)
async def responder_quiz(
    adaptacao_id: str,
    payload: RespostasQuizRequest,
    current_user: Usuario = Depends(get_current_user),
) -> RespostasQuizResponse:
    raise NaoImplementadoError()
