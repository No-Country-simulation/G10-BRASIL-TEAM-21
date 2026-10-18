from fastapi import APIRouter

from app import __version__
from app.schemas.health import HealthResponse

router = APIRouter(tags=["saude"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    # Por enquanto só confirma que a API está de pé. A checagem do banco e do pgvector
    # entra com US-008 e a do bucket com US-006/US-035 (contrato, seção 2).
    return HealthResponse(status="ok", versao=__version__)
