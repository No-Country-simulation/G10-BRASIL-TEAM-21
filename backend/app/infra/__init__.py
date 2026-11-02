"""Implementações concretas das ports: PostgreSQL (SQLAlchemy), OCI, armazenamento local, LLM.

Nunca é importado pelo domínio (docs/07 - Convenções.md, seção 2).
Inclui os adaptadores de LLM (Gemini, Groq e um falso para testes) e a fábrica que os monta.
"""

# Correção do caminho relativo: '..' em vez de '...'
from ..config import Settings
from ..ports.llm import LLMConfigError, LLMProvider


def criar_provedor(nome: str, modelo: str, settings: Settings) -> LLMProvider:
    """Monta o adaptador pelo nome. Importa o SDK só quando o provedor é usado."""
    nome = nome.strip().lower()
    if nome == "gemini":
        # CORREÇÃO: Apontando para a subpasta llm
        from .llm.gemini import GeminiProvider

        return GeminiProvider(settings.llm_api_key, modelo, settings.llm_timeout_s)
    if nome == "groq":
        # CORREÇÃO: Apontando para a subpasta llm
        from .llm.groq import GroqProvider

        return GroqProvider(settings.groq_api_key, modelo, settings.llm_timeout_s)
    if nome == "fake":
        # Se o fake também estiver na subpasta llm:
        from .llm.fake import FakeProvider

        return FakeProvider()
    raise LLMConfigError(f"Provedor de LLM desconhecido: {nome!r}.")


def criar_cadeia(settings: Settings) -> list[LLMProvider]:
    """Principal primeiro, reserva depois. Sem reserva configurado, a cadeia tem só um."""
    # O 'or "fake"' resolve o erro de tipagem: se for None, ele vira uma string.
    provedor_principal = settings.llm_provider or "fake"
    modelo_principal = settings.llm_model or "default"

    cadeia = [criar_provedor(provedor_principal, modelo_principal, settings)]

    if settings.llm_fallback_provider:
        # Aqui a mesma coisa: garante que o modelo de fallback nunca seja None
        modelo_fallback = settings.llm_fallback_model or "default"
        cadeia.append(criar_provedor(settings.llm_fallback_provider, modelo_fallback, settings))
    return cadeia
