from typing import Any
from fastapi import APIRouter, Depends, Query

from ..schemas.adaptacao import AdaptacaoRequest, AdaptacaoResponse
from ..schemas.common import ErroResposta
from ..schemas.listagens import AdaptacoesListResponse
from ..schemas.perfil import RespostasQuizRequest, RespostasQuizResponse
from ._deps import get_current_user
from ..infra.db.models import Usuario
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/adaptacoes", tags=["adaptacoes"])

# Correção do Lint aqui:
ERR: dict[int | str, dict[str, Any]] = {501: {"model": ErroResposta}}


@router.post("", response_model=AdaptacaoResponse, responses=ERR)
async def criar_adaptacao(
    payload: AdaptacaoRequest,
    incluir_gabarito: bool = Query(False),
    forcar_reprocessamento: bool = Query(False),
    current_user: Usuario = Depends(get_current_user),
) -> AdaptacaoResponse:
    raise NaoImplementadoError()

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
