import logging
from typing import Any

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from pdfminer.pdfparser import PDFSyntaxError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra.db.models import Usuario
from ..rag.embeddings import ErroEmbedding
from ..rag.extractor import FormatoNaoSuportadoError
from ..rag.retrieval import buscar_chunks_similares
from ..schemas.busca import BuscaChunksRequest, BuscaChunksResponse, ChunkBuscaResponse
from ..schemas.common import ErroResposta
from ..schemas.documentos import (
    ChunkIngeridoResponse,
    DocumentoCreateTexto,
    DocumentoResponse,
    UploadDocumentoResponse,
)
from ..schemas.listagens import DocumentosListResponse
from ..services.ingestao import processar_documento
from ._deps import get_current_user, get_db
from ._errors import ErroApi, NaoImplementadoError

router = APIRouter(prefix="/documentos", tags=["documentos"])
logger = logging.getLogger(__name__)

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


@router.post("/upload", response_model=UploadDocumentoResponse, status_code=201)
async def upload_documento(
    arquivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadDocumentoResponse:
    """Extrai e fatia PDF/TXT; persiste os metadados e devolve os chunks."""
    nome = arquivo.filename or ""
    if not nome:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "O arquivo precisa ter um nome.")

    # Valida o tamanho do arquivo (pega do .env)
    limite_bytes = get_settings().max_upload_mb * 1024 * 1024
    conteudo = await arquivo.read(limite_bytes + 1)

    if len(conteudo) > limite_bytes:
        raise ErroApi(400, "ARQUIVO_MUITO_GRANDE", "O arquivo excede o limite de upload.")

    try:
        # Chama o serviço para fazer o trabalho pesado
        doc, chunks = processar_documento(
            file=arquivo, conteudo=conteudo, db=db, usuario_id=str(current_user.usuario_id)
        )
    except FormatoNaoSuportadoError as exc:
        raise ErroApi(400, "FORMATO_NAO_SUPORTADO", str(exc)) from exc
    except (PDFSyntaxError, UnicodeDecodeError, ValueError) as exc:
        raise ErroApi(400, "ARQUIVO_INVALIDO", "Não foi possível ler o arquivo enviado.") from exc
    except ErroEmbedding as exc:
        logger.exception("Falha ao gerar embeddings durante o upload")
        raise ErroApi(503, "EMBEDDING_INDISPONIVEL", str(exc)) from exc
    except Exception as exc:
        logger.error("Erro ao processar documento: %s", str(exc))
        raise ErroApi(500, "ERRO_INTERNO", "Erro ao processar o documento.") from exc

    logger.info("Documento ingerido: id=%s | total chunks=%d", doc.documento_id, len(chunks))

    # Monta a resposta usando os schemas
    return UploadDocumentoResponse(
        documento_id=str(doc.documento_id),
        nome=doc.titulo,
        tamanho_bytes=doc.tamanho_bytes,
        data_upload=doc.criado_em,
        total_chunks=len(chunks),
        chunks=[
            ChunkIngeridoResponse(chunk_id=c.chunk_id, ordem=c.ordem, texto=c.texto) for c in chunks
        ],
    )


@router.post("/buscar", response_model=BuscaChunksResponse)
def buscar_documentos(
    payload: BuscaChunksRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BuscaChunksResponse:
    """Busca os três chunks semanticamente mais próximos da pergunta."""
    try:
        resultados = buscar_chunks_similares(
            db=db,
            pergunta=payload.pergunta,
            usuario_id=current_user.usuario_id,
            limite=3,
        )
    except ErroEmbedding as exc:
        logger.exception("Falha ao gerar embedding da consulta")
        raise ErroApi(503, "EMBEDDING_INDISPONIVEL", str(exc)) from exc

    return BuscaChunksResponse(
        pergunta=payload.pergunta,
        resultados=[
            ChunkBuscaResponse(
                documento_id=str(resultado.chunk.documento_id),
                chunk_id=resultado.chunk.chunk_id,
                ordem=resultado.chunk.ordem,
                texto=resultado.chunk.texto,
                similaridade=resultado.similaridade,
            )
            for resultado in resultados
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
    current_user: Usuario = Depends(get_current_user),
) -> DocumentoResponse:
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
