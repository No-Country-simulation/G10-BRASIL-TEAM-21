"""App FastAPI do AdaptAI. Stubs de T1: rotas retornam 501 até semana 2."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import adaptacoes, auth, documentos, health, perfil, testes_nivel
from .api._errors import NaoImplementadoError


def create_app() -> FastAPI:
    app = FastAPI(
        title="AdaptAI",
        version="1.0.0",
        description="Sistema inteligente de adaptacao e geracao de conteudo educacional.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ajustar via CORS_ORIGINS em config.py
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NaoImplementadoError)
    async def handler_nao_implementado(request: Request, exc: NaoImplementadoError):
        return JSONResponse(
            status_code=501,
            content={
                "status": "erro",
                "codigo": "NAO_IMPLEMENTADO",
                "mensagem": "Esta rota ainda nao foi implementada.",
                "detalhes": [],
                "request_id": getattr(request.state, "request_id", "req-desconhecido"),
            },
        )

    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(auth.usuarios_router, prefix=api_prefix)
    app.include_router(documentos.router, prefix=api_prefix)
    app.include_router(adaptacoes.router, prefix=api_prefix)
    app.include_router(perfil.router, prefix=api_prefix)
    app.include_router(testes_nivel.router, prefix=api_prefix)
    app.include_router(health.router, prefix=api_prefix)

    return app


app = create_app()
