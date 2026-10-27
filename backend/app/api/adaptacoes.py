from fastapi import APIRouter, Depends, Query

from ..schemas.adaptacao import AdaptacaoRequest, AdaptacaoResponse
from ..schemas.common import ErroResposta
from ..schemas.listagens import AdaptacoesListResponse
from ..schemas.perfil import RespostasQuizRequest, RespostasQuizResponse
from ._deps import get_current_user_stub
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/adaptacoes", tags=["adaptacoes"])
ERR = {501: {"model": ErroResposta}}


@router.post("", response_model=AdaptacaoResponse, responses=ERR)
async def criar_adaptacao(
    payload: AdaptacaoRequest,
    incluir_gabarito: bool = Query(
        False,
        description="Quiz: inclui resposta_correta e justificativa na resposta.",
    ),
    forcar_reprocessamento: bool = Query(
        False,
        description="Ignora o cache por hash e força a execução do grafo (RN-20).",
    ),
    _: dict = Depends(get_current_user_stub),
) -> AdaptacaoResponse:
    raise NaoImplementadoError()


@router.get("", response_model=AdaptacoesListResponse, responses=ERR)
async def listar_adaptacoes(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    _: dict = Depends(get_current_user_stub),
) -> AdaptacoesListResponse:
    raise NaoImplementadoError()


@router.get("/{adaptacao_id}", response_model=AdaptacaoResponse, responses=ERR)
async def obter_adaptacao(
    adaptacao_id: str,
    incluir_gabarito: bool = Query(False),
    _: dict = Depends(get_current_user_stub),
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
    _: dict = Depends(get_current_user_stub),
) -> RespostasQuizResponse:
    raise NaoImplementadoError()