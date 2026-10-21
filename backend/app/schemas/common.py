"""Formatos compartilhados: erro, paginação."""

from pydantic import BaseModel, ConfigDict, Field


class ErroDetalhe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    campo: str | None = None
    mensagem: str


class ErroResposta(BaseModel):
    """Formato único de erro (contrato, seção 8)."""

    model_config = ConfigDict(extra="forbid")
    status: str = "erro"
    codigo: str
    mensagem: str
    detalhes: list[ErroDetalhe] = Field(default_factory=list)
    request_id: str


class Paginacao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total: int
    limite: int
    deslocamento: int
