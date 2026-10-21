"""Itens por formato (contrato, seção 5.3)."""
from typing import Union
from pydantic import BaseModel, ConfigDict


class Alternativa(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    texto: str


class ItemFlashcard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frente: str
    verso: str
    dica_didatica: str
    conceito_ref: str
    analogia_ref: str | None = None
    fontes_chunks: list[str]


class ItemQuiz(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pergunta: str
    alternativas: list[Alternativa]
    resposta_correta: str       # id da alternativa correta
    justificativa: str
    conceito_ref: str
    analogia_ref: str | None = None
    fontes_chunks: list[str]


class ItemTutorial(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passo: int
    titulo: str
    instrucao: str
    exemplo: str | None = None
    conceito_ref: str
    fontes_chunks: list[str]


class ItemResumo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topico: str
    resumo: str
    impacto_negocio: str
    conceito_ref: str
    fontes_chunks: list[str]


class ItemRoteiroAula(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bloco: int
    titulo: str
    fala: str
    duracao_min: int
    recurso_visual: str | None = None
    conceito_ref: str
    fontes_chunks: list[str]


# União discriminada por `extra="forbid"`: cada tipo só aceita seus próprios campos.
ItemConteudo = (
    ItemFlashcard | ItemQuiz | ItemTutorial | ItemResumo | ItemRoteiroAula
)
