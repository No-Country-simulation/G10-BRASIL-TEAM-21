from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..schemas.health import HealthResponse
from ._deps import get_db

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
def health(response: Response, db: Session = Depends(get_db)) -> dict:
    estado = {"api": "ok", "db": "ok", "pgvector": "ok"}
    try:
        db.execute(text("SELECT 1"))
        if db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).first() is None:
            estado["pgvector"] = "falha"
            response.status_code = 503
    except Exception:
        estado.update(db="falha", pgvector="desconhecido")
        response.status_code = 503
    return estado
