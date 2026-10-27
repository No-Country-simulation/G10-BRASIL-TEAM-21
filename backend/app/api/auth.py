from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..schemas.auth import (
    CadastroRequest,
    CadastroResponse,
    LoginRequest,
    LoginResponse,
    UsuarioMeResponse,
)
from ..schemas.enums import Nivel # Importando o Enum
from ..schemas.common import ErroResposta
from ..infra.db.session import get_db
from ..infra.db.models import Usuario
from ..core.security import hash_senha, verificar_senha, criar_token_jwt, EXPIRA_MINUTOS
from ._deps import get_current_user
from ._errors import ErroApi

router = APIRouter(prefix="/auth", tags=["auth"])

# Correção 1: Tipagem correta do dicionário de erros
ERR: dict[int | str, dict[str, Any]] = {
    401: {"model": ErroResposta},
    400: {"model": ErroResposta}
}


@router.post(
    "/cadastro",
    response_model=CadastroResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERR,
)
async def cadastro(payload: CadastroRequest, db: Session = Depends(get_db)) -> CadastroResponse:
    email_lower = payload.email.lower()
    if db.query(Usuario).filter(func.lower(Usuario.email) == email_lower).first():
        raise ErroApi(400, "EMAIL_EXISTE", "Este e-mail já está cadastrado.")

    novo_user = Usuario(
        nome=payload.nome,
        email=email_lower,
        senha_hash=hash_senha(payload.senha),
        nivel_declarado=payload.nivel_declarado.value
    )
    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return CadastroResponse(
        usuario_id=str(novo_user.usuario_id),
        nome=novo_user.nome,
        email=novo_user.email,
        nivel_atual=payload.nivel_declarado
    )

@router.post("/login", response_model=LoginResponse, responses=ERR)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    email_lower = payload.email.lower()
    user = db.query(Usuario).filter(func.lower(Usuario.email) == email_lower).first()

    if not user or not verificar_senha(payload.senha, user.senha_hash):
        raise ErroApi(401, "CREDENCIAIS_INVALIDAS", "E-mail ou senha incorretos.")

    token = criar_token_jwt(user.usuario_id)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expira_em_segundos=EXPIRA_MINUTOS * 60
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: Usuario = Depends(get_current_user)) -> None:
    return None


# -------- usuário logado --------
usuarios_router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@usuarios_router.get("/me", response_model=UsuarioMeResponse, responses=ERR) # <-- Aqui usa o usuarios_router
async def me(current_user: Usuario = Depends(get_current_user)) -> UsuarioMeResponse:
    return UsuarioMeResponse(
        usuario_id=str(current_user.usuario_id),
        nome=current_user.nome,
        email=current_user.email,
        nivel_atual=Nivel(current_user.nivel_declarado)
    )
