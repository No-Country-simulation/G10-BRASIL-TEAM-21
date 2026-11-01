"""Provedor principal: Gemini com JSON estruturado (response_json_schema)."""

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from ...ports.llm import LLMConfigError, LLMIndisponivelError

# Códigos HTTP em que vale tentar o reserva: limite de uso, instabilidade, tempo esgotado.
_PASSAGEIROS = {408, 429, 500, 502, 503, 504}


class GeminiProvider:
    nome = "gemini"

    def __init__(self, api_key: str | None, modelo: str, timeout_s: float) -> None:
        self.modelo = modelo
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._client: genai.Client | None = None

    def _cliente(self) -> genai.Client:
        if not self._api_key:
            raise LLMConfigError("LLM_API_KEY (Gemini) não está configurada.")
        if self._client is None:
            self._client = genai.Client(
                api_key=self._api_key,
                # timeout do SDK é em milissegundos
                http_options=types.HttpOptions(timeout=int(self._timeout_s * 1000)),
            )
        return self._client

    def gerar_json(self, sistema: str, usuario: str, schema: type[BaseModel]) -> str:
        cliente = self._cliente()
        try:
            resposta = cliente.models.generate_content(
                model=self.modelo,
                contents=usuario,
                config=types.GenerateContentConfig(
                    system_instruction=sistema,
                    response_mime_type="application/json",
                    # O schema Pydantic obriga o Gemini a devolver exatamente esse JSON.
                    response_json_schema=schema.model_json_schema(),
                    temperature=0.4,
                ),
            )
        except errors.APIError as exc:
            codigo = getattr(exc, "code", None)
            if codigo in _PASSAGEIROS:
                raise LLMIndisponivelError(f"Gemini indisponível (HTTP {codigo}).") from exc
            raise LLMConfigError(f"Gemini recusou a chamada (HTTP {codigo}): {exc}") from exc
        except (httpx.HTTPError, TimeoutError, OSError) as exc:
            raise LLMIndisponivelError(f"Falha de rede ao chamar o Gemini: {exc}") from exc

        texto = resposta.text
        if not texto:
            # Resposta vazia (bloqueio de segurança ou corte): tratada como falha passageira.
            raise LLMIndisponivelError("O Gemini devolveu uma resposta vazia.")
        return texto