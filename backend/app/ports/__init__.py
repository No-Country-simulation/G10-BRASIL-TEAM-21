"""Interfaces: StoragePort, LLMProvider, VectorStore e repositórios.

Permitem testar sem rede (armazenamento local, repositórios em memória, LLM falso) e trocar
provedores sem tocar na regra de negócio.
"""
from .cache_key_builder import CacheKeyBuilder
from .domain_classifier import ClassificacaoDominio, DomainClassifier
from .llm_provider import LLMProvider

__all__ = [
    "CacheKeyBuilder",
    "ClassificacaoDominio",
    "DomainClassifier",
    "LLMProvider",
]
