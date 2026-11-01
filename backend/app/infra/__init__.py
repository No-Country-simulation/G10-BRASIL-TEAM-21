"""Implementações concretas das ports: PostgreSQL (SQLAlchemy), OCI, armazenamento local, LLM.

Nunca é importado pelo domínio (docs/07 - Convenções.md, seção 2).
"""
"""Adaptadores de LLM (Gemini, Groq e um falso para testes) e a fábrica que os monta."""

from ...config import Settings
from ...ports.llm import LLMConfigError, LLMProvider


def criar_provedor(nome: str, modelo: str, settings: Settings) -> LLMProvider:
    """Monta o adaptador pelo nome. Importa o SDK só quando o provedor é usado."""
    nome = nome.strip().lower()
    if nome == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider(settings.llm_api_key, modelo, settings.llm_timeout_s)
    if nome == "groq":
        from .groq import GroqProvider

        return GroqProvider(settings.groq_api_key, modelo, settings.llm_timeout_s)
    if nome == "fake":
        from .fake import FakeProvider

        return FakeProvider()
    raise LLMConfigError(f"Provedor de LLM desconhecido: {nome!r}.")


def criar_cadeia(settings: Settings) -> list[LLMProvider]:
    """Principal primeiro, reserva depois. Sem reserva configurado, a cadeia tem só um."""
    cadeia = [criar_provedor(settings.llm_provider, settings.llm_model, settings)]
    if settings.llm_fallback_provider:
        cadeia.append(
            criar_provedor(settings.llm_fallback_provider, settings.llm_fallback_model, settings)
        )
    return cadeia