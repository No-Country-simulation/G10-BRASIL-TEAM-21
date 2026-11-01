"""Provedor reserva: Groq (llama-3.1-8b-instant ou openai/gpt-oss-20b), modo JSON."""

import groq as groq_sdk
from pydantic import BaseModel

from ...ports.llm import LLMConfigError, LLMIndisponivelError


class GroqProvider:
    nome = "groq"

    def __init__(self, api_key: str | None, modelo: str, timeout_s: float) -> None:
        self.modelo = modelo
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._client: groq_sdk.Groq | None = None

    def _cliente(self) -> groq_sdk.Groq:
        if not self._api_key:
            raise LLMConfigError("GROQ_API_KEY não está configurada.")
        if self._client is None:
            # max_retries=0: quem decide repetir é o orquestrador, não o SDK.
            self._client = groq_sdk.Groq(
                api_key=self._api_key, timeout=self._timeout_s, max_retries=0
            )
        return self._client

    def gerar_json(self, sistema: str, usuario: str, schema: type[BaseModel]) -> str:
        cliente = self._cliente()
        try:
            resposta = cliente.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario},
                ],
                # json_object funciona em todos os modelos da Groq; o formato exato vem no prompt.
                response_format={"type": "json_object"},
                temperature=0.4,
            )
        except (groq_sdk.RateLimitError, groq_sdk.InternalServerError) as exc:
            raise LLMIndisponivelError(f"Groq indisponível: {exc}") from exc
        except (groq_sdk.APIConnectionError, groq_sdk.APITimeoutError) as exc:
            raise LLMIndisponivelError(f"Falha de rede ao chamar a Groq: {exc}") from exc
        except groq_sdk.APIStatusError as exc:
            raise LLMConfigError(f"Groq recusou a chamada (HTTP {exc.status_code}): {exc}") from exc

        texto = resposta.choices[0].message.content if resposta.choices else None
        if not texto:
            raise LLMIndisponivelError("A Groq devolveu uma resposta vazia.")
        return texto