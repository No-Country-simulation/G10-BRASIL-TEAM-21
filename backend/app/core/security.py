import os
from datetime import datetime, timedelta
from uuid import UUID

import bcrypt
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "chave-secreta-hackathon")
ALGORITHM = "HS256"
EXPIRA_MINUTOS = int(os.getenv("JWT_EXPIRA_MIN", "60"))


def hash_senha(senha: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token_jwt(usuario_id: UUID) -> str:
    expira = datetime.utcnow() + timedelta(minutes=EXPIRA_MINUTOS)
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> UUID | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        return UUID(sub) if sub else None
    except Exception:
        return None
