"""Contrato do provedor de LLM e embeddings (ADR-0011)."""
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstração sobre o provedor de LLM e embeddings."""

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        schema: type,
        timeout_s: float = 30.0,
    ) -> dict[str, Any]:
        """Gera uma resposta e valida com `schema` (Pydantic). Devolve dict."""
        ...

    @abstractmethod
    def embed(self, texto: str) -> list[float]:
        """Devolve o embedding do texto (dimensão configurável)."""
        ...
