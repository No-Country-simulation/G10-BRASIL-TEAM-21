"""App FastAPI do AdaptAI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import adaptacoes, auth, documentos, health, perfil, teste_nivel
from .api._errors import registrar_erros
from .schemas.common import VERSAO_SCHEMA

def create_app() -> FastAPI:
    app = FastAPI(
        title="AdaptAI",
        version=VERSAO_SCHEMA,
        description="Sistema inteligente de adaptacao e geracao de conteudo educacional.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ajustar via CORS_ORIGINS em config.py
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_erros(app)

    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(auth.usuarios_router, prefix=api_prefix) # Rota do /me
    app.include_router(documentos.router, prefix=api_prefix)
    app.include_router(adaptacoes.router, prefix=api_prefix)
    app.include_router(perfil.router, prefix=api_prefix)
    app.include_router(teste_nivel.router, prefix=api_prefix)
    app.include_router(health.router, prefix=api_prefix)

    return app

app = create_app()
