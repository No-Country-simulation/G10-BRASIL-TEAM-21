"""Listagens paginadas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from .enums import DominioConhecimento, FormatoSaida, Nicho, PerfilSaida, StatusUpload
from .documentos import DocumentoResumo


class DocumentosListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    itens: list[DocumentoResumo]
    total: int


class AdaptacaoResumo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    adaptacao_id: str
    documento_id: str
    titulo: str
    perfil_aplicado: PerfilSaida
    formato_gerado: FormatoSaida
    nicho_aplicado: Nicho
    dominio_conhecimento: DominioConhecimento | None = None
    ancoragem_fonte_score: float
    status_upload: StatusUpload
    criado_em: datetime


class AdaptacoesListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    itens: list[AdaptacaoResumo]
    total: int
