"""Dependências compartilhadas dos routers (stubs de T1)."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def get_current_user_stub(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Stub de T1: documenta o esquema Bearer e devolve um usuário fixo.

    TODO(T2/semana 2): validar JWT de verdade e retornar o usuário do banco.    
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "erro",
                "codigo": "NAO_AUTENTICADO",
                "mensagem": "Token de acesso ausente ou invalido.",
                "detalhes": [],
                "request_id": "req-stub",
            },
        )
    return {"usuario_id": "usr-stub"}
