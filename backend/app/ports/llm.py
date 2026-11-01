"""Porta de LLM: o resto do sistema só conhece esta interface (ADR-0011, US-020).

Trocar ou acrescentar provedores (Gemini, Groq, falso para testes) não exige mexer nos
prompts, na validação nem nas rotas.
"""

from typing import Protocol

from pydantic import BaseModel


class LLMError(Exception):
    """Base dos erros de provedor de LLM. Qualquer um deles faz o orquestrador tentar o reserva."""


class LLMIndisponivelError(LLMError):
    """Falha passageira: limite de uso (429), instabilidade (5xx), timeout ou rede."""


class LLMConfigError(LLMError):
    """Chave ausente ou recusada, modelo inexistente: repetir no mesmo provedor não adianta."""


class SaidaInvalidaError(LLMError):
    """O provedor respondeu, mas o texto não é um JSON válido para o schema pedido."""


class LLMProvider(Protocol):
    nome: str  # "gemini", "groq"... aparece nos logs e na resposta
    modelo: str

    def gerar_json(self, sistema: str, usuario: str, schema: type[BaseModel]) -> str:
        """Devolve o TEXTO JSON gerado (ainda não validado) para o schema pedido.

        Levanta LLMIndisponivelError ou LLMConfigError quando o provedor falha.
        """
        ...