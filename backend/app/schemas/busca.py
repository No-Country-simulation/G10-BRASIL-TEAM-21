"""Schemas da busca semântica de chunks."""

from pydantic import BaseModel, ConfigDict, Field


class BuscaChunksRequest(BaseModel):
    """Pergunta usada para localizar trechos relevantes."""

    model_config = ConfigDict(extra="forbid")

    pergunta: str = Field(min_length=1, max_length=2000)


class ChunkBuscaResponse(BaseModel):
    """Trecho recuperado e sua similaridade com a pergunta."""

    documento_id: str
    chunk_id: str
    ordem: int
    texto: str
    similaridade: float


class BuscaChunksResponse(BaseModel):
    """Até três trechos mais relevantes para a pergunta."""

    pergunta: str
    resultados: list[ChunkBuscaResponse]
