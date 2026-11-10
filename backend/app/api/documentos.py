import logging
import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from pdfminer.pdfparser import PDFSyntaxError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra.db.models import Chunk, Documento, Usuario
from ..rag.embeddings import ErroEmbedding
from ..rag.extractor import FormatoNaoSuportadoError
from ..rag.retrieval import buscar_chunks_similares
from ..schemas.busca import BuscaChunksRequest, BuscaChunksResponse, ChunkBuscaResponse
from ..schemas.documentos import (
    ChunkIngeridoResponse,
    DocumentoResponse,
    DocumentoResumo,
    UploadDocumentoResponse,
)
from ..schemas.enums import ClassificadorUsado, DominioConhecimento, Nivel, StatusUpload
from ..schemas.listagens import DocumentosListResponse
from ..services import xp
from ..services.ingestao import processar_documento
from ._deps import get_current_user, get_db
from ._errors import ErroApi

router = APIRouter(prefix="/documentos", tags=["documentos"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadDocumentoResponse, status_code=201)
async def upload_documento(
    arquivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadDocumentoResponse:
    """Extrai e fatia PDF/TXT/MD; persiste os metadados e devolve os chunks."""
    nome = arquivo.filename or ""
    if not nome:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "O arquivo precisa ter um nome.")

    # Valida o tamanho do arquivo (pega do .env)
    limite_bytes = get_settings().max_upload_mb * 1024 * 1024
    conteudo = await arquivo.read(limite_bytes + 1)

    if len(conteudo) > limite_bytes:
        raise ErroApi(413, "ARQUIVO_MUITO_GRANDE", "O arquivo excede o limite de upload.")

    try:
        # Chama o serviço para fazer o trabalho pesado
        doc, chunks = processar_documento(
            file=arquivo, conteudo=conteudo, db=db, usuario_id=str(current_user.usuario_id)
        )
    except ErroApi:
        raise  # ex.: 409 de documento duplicado; não pode virar 500 no except genérico
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

    # +10 XP só na primeira vez deste documento (reenvio do mesmo arquivo dá 409 antes daqui).
    xp_ganho = xp.registrar_upload(db, current_user, doc.documento_id)
    db.commit()

    # Monta a resposta usando os schemas
    return UploadDocumentoResponse(
        documento_id=str(doc.documento_id),
        nome=doc.titulo,
        tamanho_bytes=doc.tamanho_bytes,
        data_upload=doc.criado_em,
        total_chunks=len(chunks),
        xp_ganho=xp_ganho,
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


@router.get("", response_model=DocumentosListResponse)
def listar_documentos(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentosListResponse:
    filtro_usuario = Documento.usuario_id == current_user.usuario_id
    total = db.scalar(select(func.count()).select_from(Documento).where(filtro_usuario)) or 0
    documentos = db.scalars(
        select(Documento)
        .where(filtro_usuario)
        .order_by(Documento.criado_em.desc(), Documento.documento_id.desc())
        .limit(limite)
        .offset(deslocamento)
    ).all()

    return DocumentosListResponse(
        itens=[
            DocumentoResumo(
                documento_id=str(doc.documento_id),
                titulo=doc.titulo,
                formato_origem=doc.formato_origem,
                nivel_documento_estimado=(
                    Nivel(doc.nivel_documento_estimado)
                    if doc.nivel_documento_estimado is not None
                    else None
                ),
                dominio_conhecimento=(
                    DominioConhecimento(doc.dominio_conhecimento)
                    if doc.dominio_conhecimento is not None
                    else None
                ),
                classificador_usado=(
                    ClassificadorUsado(doc.classificador_usado)
                    if doc.classificador_usado is not None
                    else None
                ),
                status_upload=StatusUpload(doc.status_upload),
                criado_em=doc.criado_em,
            )
            for doc in documentos
        ],
        total=total,
    )


@router.get("/{documento_id}", response_model=DocumentoResponse)
def obter_documento(
    documento_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentoResponse:
    try:
        documento_uuid = uuid.UUID(documento_id)
    except ValueError:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "documento_id inválido.") from None

    documento = db.scalars(
        select(Documento).where(
            Documento.documento_id == documento_uuid,
            Documento.usuario_id == current_user.usuario_id,
        )
    ).first()
    if documento is None:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Documento não encontrado.")

    chunks_indexados = (
        db.scalar(
            select(func.count())
            .select_from(Chunk)
            .where(Chunk.documento_id == documento.documento_id)
        )
        or 0
    )

    return DocumentoResponse(
        documento_id=str(documento.documento_id),
        titulo=documento.titulo,
        formato_origem=documento.formato_origem,
        chunks_indexados=chunks_indexados,
        nivel_documento_estimado=(
            Nivel(documento.nivel_documento_estimado)
            if documento.nivel_documento_estimado is not None
            else None
        ),
        dominio_conhecimento=(
            DominioConhecimento(documento.dominio_conhecimento)
            if documento.dominio_conhecimento is not None
            else None
        ),
        classificador_usado=(
            ClassificadorUsado(documento.classificador_usado)
            if documento.classificador_usado is not None
            else None
        ),
        status_upload=StatusUpload(documento.status_upload),
    )
