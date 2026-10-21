"""Contrato do classificador de domínio (RN-21)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..schemas.enums import DominioConhecimento


@dataclass(frozen=True)
class ClassificacaoDominio:
    """Resultado da classificação de domínio de um texto."""

    dominio: DominioConhecimento
    confianca: float  # 0.0 a 1.0
    origem: str  # "local" | "api" | "fallback"


class DomainClassifier(ABC):
    """Classifica o domínio do conhecimento de um documento.

    Implementações:
      - Scikit-learn local (TF-IDF + LogisticRegression)
      - Stub (retorna Geral) — usado até o modelo treinado estar disponível
      - API fallback (quando a confiança local < limiar)
    """

    @abstractmethod
    def classify(self, texto: str) -> ClassificacaoDominio: ...
