from typing import Any

from fastapi import APIRouter, Depends, Query, Request

from ..infra.db.models import Usuario
from ..schemas.common import ErroResposta
from ..schemas.documentos import DocumentoCreateTexto, DocumentoResponse
from ..schemas.listagens import DocumentosListResponse
from ._deps import get_current_user
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/documentos", tags=["documentos"])

ERR: dict[int | str, dict[str, Any]] = {501: {"model": ErroResposta}}

CORPO_DOCUMENTO = {
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "arquivo": {
                            "type": "string",
                            "format": "binary",
                            "description": "PDF, Markdown ou TXT.",
                        }
                    },
                    "required": ["arquivo"],
                }
            },
            "application/json": {"schema": DocumentoCreateTexto.model_json_schema()},
        },
    }
}


@router.post(
    "",
    response_model=DocumentoResponse,
    status_code=201,
    responses=ERR,
    openapi_extra=CORPO_DOCUMENTO,
)
async def criar_documento(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
) -> DocumentoResponse:
    # Aceita multipart/form-data (campo `arquivo`) OU JSON DocumentoCreateTexto.
    raise NaoImplementadoError()


@router.get("", response_model=DocumentosListResponse, responses=ERR)
async def listar_documentos(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
) -> DocumentosListResponse:
    raise NaoImplementadoError()


@router.get("/{documento_id}", response_model=DocumentoResponse, responses=ERR)
async def obter_documento(
    documento_id: str,
    current_user: Usuario = Depends(get_current_user),
) -> DocumentoResponse:
    raise NaoImplementadoError()
