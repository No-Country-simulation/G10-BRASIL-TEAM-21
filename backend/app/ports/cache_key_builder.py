"""Contrato do construtor de cache_key (RN-20)."""
from abc import ABC, abstractmethod


class CacheKeyBuilder(ABC):
    """Constrói a chave determinística de cache de adaptação.

    A implementação padrão é sha256 de uma serialização canônica dos
    parâmetros. Mudanças de parâmetro → chave diferente → novo cálculo.
    """

    @abstractmethod
    def build(
        self,
        hash_conteudo: str,
        perfil_destinatario: str,
        formato_saida: str,
        nicho_setor: str,
        nivel_detalhe: str,
        incluir_analogias: bool,
        incluir_microlearning: bool,
    ) -> str:
        ...
