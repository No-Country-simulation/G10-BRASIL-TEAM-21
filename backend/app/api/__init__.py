"""Routers da API v1."""

from . import adaptacoes, auth, documentos, health, perfil
from . import teste_nivel as testes_nivel

__all__ = ["adaptacoes", "auth", "documentos", "health", "perfil", "testes_nivel"]
