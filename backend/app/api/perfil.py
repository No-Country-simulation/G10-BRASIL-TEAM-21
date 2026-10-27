from fastapi import APIRouter, Depends

from ..schemas.common import ErroResposta
from ..schemas.perfil import PerfilResponse
from ._deps import get_current_user_stub
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/perfil", tags=["perfil"])
ERR = {501: {"model": ErroResposta}}


@router.get("", response_model=PerfilResponse, responses=ERR)
async def obter_perfil(_: dict = Depends(get_current_user_stub)) -> PerfilResponse:
    raise NaoImplementadoError()