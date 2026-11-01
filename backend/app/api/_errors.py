"""Erros padronizados (contrato, secao 8)."""

import re
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

_RID_VALIDO = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_CODIGOS = {400: "REQUISICAO_INVALIDA", 401: "NAO_AUTENTICADO", 404: "RECURSO_NAO_ENCONTRADO"}
_MENSAGENS = {
    400: "Requisicao invalida.",
    401: "Token de acesso ausente ou invalido.",
    404: "Recurso nao encontrado.",
}


class NaoImplementadoError(Exception):
    """Sinaliza rota documentada mas ainda não implementada (HTTP 501)."""


class ErroApi(Exception):
    def __init__(self, status: int, codigo: str, mensagem: str, detalhes: list | None = None):
        self.status, self.codigo, self.mensagem = status, codigo, mensagem
        self.detalhes = detalhes or []


def _resposta(request: Request, status: int, codigo: str, mensagem: str, detalhes=None):
    return JSONResponse(
        status_code=status,
        content={
            "status": "erro",
            "codigo": codigo,
            "mensagem": mensagem,
            "detalhes": detalhes or [],
            "request_id": getattr(request.state, "request_id", "req-desconhecido"),
        },
    )


def _detalhes(exc: RequestValidationError) -> list[dict]:
    return [
        {"campo": ".".join(str(p) for p in e["loc"][1:]) or None, "mensagem": e["msg"]}
        for e in exc.errors()
    ]


def registrar_erros(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id(request: Request, call_next):
        rid = request.headers.get("X-Request-ID", "")
        if not _RID_VALIDO.match(rid):
            rid = f"req-{uuid.uuid4().hex[:12]}"
        request.state.request_id = rid
        resposta = await call_next(request)
        resposta.headers["X-Request-ID"] = rid
        return resposta

    @app.exception_handler(NaoImplementadoError)
    async def _501(request: Request, exc: NaoImplementadoError):
        return _resposta(request, 501, "NAO_IMPLEMENTADO", "Esta rota ainda nao foi implementada.")

    @app.exception_handler(ErroApi)
    async def _erro_api(request: Request, exc: ErroApi):
        return _resposta(request, exc.status, exc.codigo, exc.mensagem, exc.detalhes)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        return _resposta(
            request,
            exc.status_code,
            _CODIGOS.get(exc.status_code, f"HTTP_{exc.status_code}"),
            _MENSAGENS.get(exc.status_code, "Nao foi possivel concluir a requisicao."),
        )

    @app.exception_handler(RequestValidationError)
    async def _validacao(request: Request, exc: RequestValidationError):
        detalhes = _detalhes(exc)
        if any(e["type"] == "requisicao_invalida" for e in exc.errors()):
            return _resposta(
                request,
                400,
                "REQUISICAO_INVALIDA",
                "Requisicao invalida. Confira os campos enviados.",
                detalhes,
            )
        return _resposta(
            request, 422, "VALIDACAO_FALHOU", "Alguns campos estao invalidos.", detalhes
        )

    @app.exception_handler(Exception)
    async def _500(request: Request, exc: Exception):
        return _resposta(
            request, 500, "ERRO_INTERNO", "Erro interno. Tente novamente em instantes."
        )
