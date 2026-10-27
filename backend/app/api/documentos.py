from fastapi import APIRouter, Depends, Query, Request

from ..schemas.common import ErroResposta
from ..schemas.documentos import DocumentoCreateTexto, DocumentoResponse
from ..schemas.listagens import DocumentosListResponse
from ._deps import get_current_user_stub
from ._errors import NaoImplementadoError

router = APIRouter(prefix="/documentos", tags=["documentos"])
ERR = {501: {"model": ErroResposta}}
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
    _: dict = Depends(get_current_user_stub),
) -> DocumentoResponse:
    # Aceita multipart/form-data (campo `arquivo`) OU JSON DocumentoCreateTexto.
    raise NaoImplementadoError()


@router.get("", response_model=DocumentosListResponse, responses=ERR)
async def listar_documentos(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    _: dict = Depends(get_current_user_stub),
) -> DocumentosListResponse:
    raise NaoImplementadoError()


@router.get("/{documento_id}", response_model=DocumentoResponse, responses=ERR)
async def obter_documento(
    documento_id: str,
    _: dict = Depends(get_current_user_stub),
) -> DocumentoResponse:
    raise NaoImplementadoError()
