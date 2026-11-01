"""Formato que o LLM deve devolver (AdaptacaoOutput), um por formato de saída.

É o miolo do contrato (seção 5 do doc 05): título, introdução, itens do formato e alguns
metadados que só o LLM sabe estimar. O restante da resposta (request_id, armazenamento,
trilha de XP...) é montado pelo backend.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .enums import FormatoSaida
from .itens import (
    ItemFlashcard,
    ItemQuiz,
    ItemResumo,
    ItemRoteiroAula,
    ItemTutorial,
)

TItem = TypeVar("TItem", ItemFlashcard, ItemQuiz, ItemTutorial, ItemResumo, ItemRoteiroAula)


class AdaptacaoOutput(BaseModel, Generic[TItem]):  # noqa: UP046 (compatível com Python 3.11)
    """Saída validada do LLM. `AdaptacaoOutput[ItemFlashcard]` exige itens de flashcard."""

    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1)
    introducao_contextualizada: str = Field(min_length=1)
    tempo_estimado_estudo_minutos: int = Field(ge=1, le=600)
    conceitos_chave: list[str] = Field(min_length=1)
    pre_requisitos: list[str]
    itens: list[TItem] = Field(min_length=1)


# Um modelo concreto por formato: é ele que vai como schema para o Gemini e para a validação.
SAIDA_POR_FORMATO: dict[FormatoSaida, type[AdaptacaoOutput]] = {
    FormatoSaida.FLASHCARDS: AdaptacaoOutput[ItemFlashcard],
    FormatoSaida.QUIZ: AdaptacaoOutput[ItemQuiz],
    FormatoSaida.TUTORIAL: AdaptacaoOutput[ItemTutorial],
    FormatoSaida.RESUMO: AdaptacaoOutput[ItemResumo],
    FormatoSaida.ROTEIRO_DE_AULA: AdaptacaoOutput[ItemRoteiroAula],
}