from typing import Any
from fastapi import APIRouter, Depends

from ..schemas.common import ErroResposta
from ..schemas.perfil import (
    RespostasTesteRequest,
    RespostasTesteResponse,
    TesteNivelResponse,
)
from ._deps import get_current_user
from ..infra.db.models import Usuario
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/testes-nivel", tags=["testes-nivel"])

ERR: dict[int | str, dict[str, Any]] = {501: {"model": ErroResposta}}


@router.post("", response_model=TesteNivelResponse, status_code=201, responses=ERR)
async def iniciar_teste(current_user: Usuario = Depends(get_current_user)) -> TesteNivelResponse:
    raise NaoImplementadoError()


@router.post(
    "/{teste_id}/respostas",
    response_model=RespostasTesteResponse,
    responses=ERR,
)
async def responder_teste(
    teste_id: str,
    payload: RespostasTesteRequest,
    current_user: Usuario = Depends(get_current_user),
) -> RespostasTesteResponse:
    raise NaoImplementadoError()
