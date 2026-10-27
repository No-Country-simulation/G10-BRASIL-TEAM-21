from fastapi import APIRouter, Depends

from ..schemas.common import ErroResposta
from ..schemas.perfil import (
    RespostasTesteRequest,
    RespostasTesteResponse,
    TesteNivelResponse,
)
from ._deps import get_current_user_stub
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/testes-nivel", tags=["testes-nivel"])
ERR = {501: {"model": ErroResposta}}


@router.post("", response_model=TesteNivelResponse, status_code=201, responses=ERR)
async def iniciar_teste(_: dict = Depends(get_current_user_stub)) -> TesteNivelResponse:
    raise NaoImplementadoError()


@router.post(
    "/{teste_id}/respostas",
    response_model=RespostasTesteResponse,
    responses=ERR,
)
async def responder_teste(
    teste_id: str,
    payload: RespostasTesteRequest,
    _: dict = Depends(get_current_user_stub),
) -> RespostasTesteResponse:
    raise NaoImplementadoError()
