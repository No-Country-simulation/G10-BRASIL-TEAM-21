"""Perfil, respostas de quiz, testes de nível."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from .adaptacao import TrilhaEvolucao
from .enums import Nivel
from .itens import Alternativa


# ---------- Quiz ----------

class RespostaQuizItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_indice: int = Field(ge=0)
    alternativa_escolhida: str


class RespostasQuizRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    respostas: list[RespostaQuizItem] = Field(min_length=1)


class FeedbackQuizItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_indice: int
    correta: bool
    justificativa: str


class TrilhaResumo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nivel_atual: Nivel
    xp_total: int
    teste_nivel_disponivel: bool


class RespostasQuizResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acertos: int
    total: int
    xp_ganho: int
    feedback: list[FeedbackQuizItem]
    trilha_evolucao: TrilhaResumo


# ---------- Perfil ----------

class EventoHistorico(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: str
    xp: int
    criado_em: datetime


class PerfilResponse(TrilhaEvolucao):
    model_config = ConfigDict(extra="forbid")
    historico: list[EventoHistorico] = Field(default_factory=list)


# ---------- Teste de Nível ----------

class PerguntaTeste(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    pergunta: str
    alternativas: list[Alternativa]
    conceito_ref: str


class TesteNivelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    teste_id: str
    nivel_avaliado: Nivel
    tentativa: int
    perguntas: list[PerguntaTeste]


class RespostaTesteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pergunta_id: str
    alternativa_escolhida: str


class RespostasTesteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    respostas: list[RespostaTesteItem] = Field(min_length=1)


class FeedbackTesteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pergunta_id: str
    correta: bool
    justificativa: str


class RespostasTesteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    percentual_dominio: float
    aprovado: bool
    nivel_atual: Nivel
    conceitos_fracos: list[str]
    feedback: list[FeedbackTesteItem]
