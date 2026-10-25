"""Classificador de domínio — stub até o modelo treinado existir.

Substituir por Scikit-learn (TF-IDF + LogisticRegression) na semana 2.
"""

from ...ports.domain_classifier import ClassificacaoDominio, DomainClassifier
from ...schemas.enums import DominioConhecimento


class StubDomainClassifier(DomainClassifier):
    """Stub: retorna Geral com confiança 0.0.

    Quando a confiança é 0.0, o serviço de ingestão cai para o fallback
    (palavras-chave ou API). Serve para o grafo rodar sem depender do modelo.
    """

    def classify(self, texto: str) -> ClassificacaoDominio:
        return ClassificacaoDominio(
            dominio=DominioConhecimento.GERAL,
            confianca=0.0,
            origem="fallback",
        )
