import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra import criar_cadeia
from ..infra.db.models import Usuario
from ..schemas.adaptacao import AdaptacaoRequest, AdaptacaoResponse
from ..schemas.common import ErroResposta
from ..schemas.listagens import AdaptacoesListResponse
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
        )
        return resposta

    except ErroApi as e:
        raise e  # Repassa erros de validação (400, 422, 502)
    except Exception as e:
        logger.error(f"Erro inesperado na rota de adaptação: {str(e)}", exc_info=True)
        raise ErroApi(500, "ERRO_IA", "Ocorreu um erro interno ao processar a adaptação.") from e


@router.get("", response_model=AdaptacoesListResponse, responses=ERR)
async def listar_adaptacoes(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
) -> AdaptacoesListResponse:
    raise NaoImplementadoError()


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
