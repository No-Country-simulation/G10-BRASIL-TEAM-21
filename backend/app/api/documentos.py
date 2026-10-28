import hashlib
import logging
import uuid

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from pdfminer.pdfparser import PDFSyntaxError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra.db.models import Documento
from ..rag.chunker import dividir_em_chunks
from ..rag.extractor import FormatoNaoSuportadoError, extrair_texto
from ..schemas.common import ErroResposta
from ..schemas.documentos import (
    ChunkIngeridoResponse,
    DocumentoCreateTexto,
    DocumentoResponse,
    UploadDocumentoResponse,
)
from ..schemas.listagens import DocumentosListResponse
from ._deps import get_current_user_stub, get_db
from ._errors import ErroApi, NaoImplementadoError

router = APIRouter(prefix="/documentos", tags=["documentos"])
logger = logging.getLogger(__name__)
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


@router.post("/upload", response_model=UploadDocumentoResponse, status_code=201)
async def upload_documento(
    arquivo: UploadFile = File(...),
    usuario: dict = Depends(get_current_user_stub),
    db: Session = Depends(get_db),
) -> UploadDocumentoResponse:
    """Extrai e fatia PDF/TXT; persiste os metadados e devolve os chunks."""
    nome = arquivo.filename or ""
    if not nome:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "O arquivo precisa ter um nome.")

    limite_bytes = get_settings().max_upload_mb * 1024 * 1024
    conteudo = await arquivo.read(limite_bytes + 1)
    if len(conteudo) > limite_bytes:
        raise ErroApi(400, "ARQUIVO_MUITO_GRANDE", "O arquivo excede o limite de upload.")

    try:
        texto = extrair_texto(conteudo, nome)
    except FormatoNaoSuportadoError as exc:
        raise ErroApi(400, "FORMATO_NAO_SUPORTADO", str(exc)) from exc
    except (PDFSyntaxError, UnicodeDecodeError, ValueError) as exc:
        raise ErroApi(400, "ARQUIVO_INVALIDO", "Não foi possível ler o arquivo enviado.") from exc

    try:
        usuario_id = uuid.UUID(str(usuario["usuario_id"]))
    except (KeyError, ValueError) as exc:
        raise ErroApi(401, "NAO_AUTENTICADO", "Usuário autenticado inválido.") from exc

    chunks = dividir_em_chunks(texto)
    documento = Documento(
        usuario_id=usuario_id,
        titulo=nome,
        formato_origem="pdf" if nome.lower().endswith(".pdf") else "texto",
        hash_conteudo=hashlib.sha256(conteudo).hexdigest(),
        tamanho_bytes=len(conteudo),
        status_upload="concluido",
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)

    logger.info(
        "Documento ingerido: id=%s nome=%s tamanho_bytes=%d chunks=%d",
        documento.documento_id,
        nome,
        len(conteudo),
        len(chunks),
    )
    logger.info(
        "Chunk IDs gerados para %s: %s",
        documento.documento_id,
        [chunk.chunk_id for chunk in chunks],
    )
    return UploadDocumentoResponse(
        documento_id=str(documento.documento_id),
        nome=nome,
        tamanho_bytes=len(conteudo),
        data_upload=documento.criado_em,
        total_chunks=len(chunks),
        chunks=[
            ChunkIngeridoResponse(chunk_id=chunk.chunk_id, ordem=chunk.ordem, texto=chunk.texto)
            for chunk in chunks
        ],
    )


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
