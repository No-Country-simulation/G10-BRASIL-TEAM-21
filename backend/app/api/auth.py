from fastapi import APIRouter, Depends, Request

from ..schemas.auth import (
    CadastroRequest,
    CadastroResponse,
    LoginRequest,
    LoginResponse,
    UsuarioMeResponse,
)
from ..schemas.common import ErroResposta
from ._deps import get_current_user_stub
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/auth", tags=["auth"])

ERR = {501: {"model": ErroResposta}}


@router.post(
    "/cadastro",
    response_model=CadastroResponse,
    status_code=201,
    responses=ERR,
)
async def cadastro(payload: CadastroRequest) -> CadastroResponse:
    raise NaoImplementadoError()


@router.post("/login", response_model=LoginResponse, responses=ERR)
async def login(payload: LoginRequest) -> LoginResponse:
    raise NaoImplementadoError()


@router.post("/logout", status_code=204, responses=ERR)
async def logout(_: dict = Depends(get_current_user_stub)) -> None:
    raise NaoImplementadoError()


# -------- usuário logado --------

usuarios_router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@usuarios_router.get("/me", response_model=UsuarioMeResponse, responses=ERR)
async def me(_: dict = Depends(get_current_user_stub)) -> UsuarioMeResponse:
    raise NaoImplementadoError()
