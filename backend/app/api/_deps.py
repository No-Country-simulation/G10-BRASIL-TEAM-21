"""Dependências compartilhadas dos routers."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.security import decodificar_token
from ..infra.db.models import Usuario
from ..infra.db.session import get_db
from ._errors import ErroApi

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida o JWT e retorna o usuário logado do banco de dados."""
    if credentials is None:
        raise ErroApi(401, "NAO_AUTENTICADO", "Token de acesso ausente ou inválido.")

    usuario_id = decodificar_token(credentials.credentials)
    if not usuario_id:
        raise ErroApi(401, "TOKEN_INVALIDO", "Token inválido ou expirado.")

    user = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if not user:
        raise ErroApi(401, "USUARIO_NAO_ENCONTRADO", "Usuário do token não existe.")

    return user
