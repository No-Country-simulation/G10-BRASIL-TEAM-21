"""Criação da aplicação FastAPI. Rode com: uvicorn app.main:app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.health import router as health_router
from app.config import get_settings

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="adaptai API", version=__version__)

    # CORS restrito à(s) origem(ns) do front-end (RNF-04). O token vai no cabeçalho
    # Authorization, não em cookie, então não há credenciais cross-site.
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.include_router(health_router, prefix=API_PREFIX)
    return app


app = create_app()
