"""Dependências compartilhadas dos routers (stubs de T1)."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..infra.db.session import get_db  # noqa: F401
from ._errors import ErroApi

security = HTTPBearer(auto_error=False)


async def get_current_user_stub(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Stub de T1: documenta o esquema Bearer e devolve um usuário fixo.

    TODO(T2/semana 2): validar JWT de verdade e retornar o usuário do banco.
    """
    if credentials is None:
        raise ErroApi(401, "NAO_AUTENTICADO", "Token de acesso ausente ou invalido.")
    return {"usuario_id": "usr-stub"}
