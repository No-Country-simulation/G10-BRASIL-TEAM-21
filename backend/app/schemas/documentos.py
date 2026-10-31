"""Documentos: criação e listagem (com domínio)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .enums import (
    ClassificadorUsado,
    DominioConhecimento,
    Nivel,
    StatusUpload,
)


class DocumentoCreateTexto(BaseModel):
    """Entrada JSON para texto bruto (alternativa ao multipart)."""

    model_config = ConfigDict(extra="forbid")
    titulo: str
    conteudo: str


class ChunkIngeridoResponse(BaseModel):
    """Chunk extraído durante o upload; não implica persistência do bloco."""

    chunk_id: str
    ordem: int
    texto: str


class UploadDocumentoResponse(BaseModel):
    """Resultado da extração, chunking e registro dos metadados."""

    documento_id: str
    nome: str
    tamanho_bytes: int
    data_upload: datetime
    total_chunks: int
    chunks: list[ChunkIngeridoResponse]


class DocumentoResponse(BaseModel):
    """Saída de POST /documentos."""

    model_config = ConfigDict(extra="forbid")
    documento_id: str
    titulo: str
    formato_origem: str  # "pdf" | "markdown" | "texto"
    chunks_indexados: int
    nivel_documento_estimado: Nivel | None = None
    dominio_conhecimento: DominioConhecimento | None = None
    classificador_usado: ClassificadorUsado | None = None
    status_upload: StatusUpload


class DocumentoResumo(BaseModel):
    """Item de GET /documentos."""

    model_config = ConfigDict(extra="forbid")
    documento_id: str
    titulo: str
    formato_origem: str
    nivel_documento_estimado: Nivel | None = None
    dominio_conhecimento: DominioConhecimento | None = None
    classificador_usado: ClassificadorUsado | None = None
    status_upload: StatusUpload
    criado_em: datetime
