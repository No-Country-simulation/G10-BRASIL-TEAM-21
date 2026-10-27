from typing import Any
from fastapi import APIRouter, Depends

from ..schemas.common import ErroResposta
from ..schemas.perfil import PerfilResponse
from ._deps import get_current_user
from ..infra.db.models import Usuario
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/perfil", tags=["perfil"])

ERR: dict[int | str, dict[str, Any]] = {501: {"model": ErroResposta}}


@router.get("", response_model=PerfilResponse, responses=ERR)
async def obter_perfil(current_user: Usuario = Depends(get_current_user)) -> PerfilResponse:
    raise NaoImplementadoError()
