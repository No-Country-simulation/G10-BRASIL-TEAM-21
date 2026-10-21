from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..infra.db.session import get_db  # (Você precisará criar o session.py se ainda não tem)

router = APIRouter(tags=["health"])

@router.get("/health")
async def health(db: Session = Depends(get_db)) -> dict:
    status = {"api": "ok", "db": "ok", "pgvector": "ok"}
    try:
        db.execute(text("SELECT 1"))
        # Verifica se a extensão vector está ativa
        result = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).fetchone()
        if not result:
            status["pgvector"] = "falha"
    except Exception as e:
        status["db"] = "falha"
        status["pgvector"] = "desconhecido"

    return status
