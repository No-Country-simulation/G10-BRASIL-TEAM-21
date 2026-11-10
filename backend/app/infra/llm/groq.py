"""Provedor reserva: Groq (llama-3.1-8b-instant ou openai/gpt-oss-20b), modo JSON."""

import logging

import groq as groq_sdk
from pydantic import BaseModel

from ...ports.llm import LLMConfigError, LLMIndisponivelError

logger = logging.getLogger(__name__)
_PASSAGEIROS = {408, 429, 500, 502, 503, 504}


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
        try:
            cliente = self._cliente()
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
            texto = resposta.choices[0].message.content if resposta.choices else None
        except groq_sdk.APIStatusError as exc:
            status = exc.status_code
            logger.warning(
                "Groq API falhou: model=%s status=%s detail=%s",
                self.modelo,
                status,
                str(exc),
            )
            if status in _PASSAGEIROS:
                raise LLMIndisponivelError(f"Groq indisponível (HTTP {status}): {exc}") from exc
            raise LLMConfigError(f"Groq recusou a chamada (HTTP {status}): {exc}") from exc
        except groq_sdk.APIConnectionError as exc:
            logger.warning("Falha de transporte Groq: model=%s detail=%s", self.modelo, exc)
            raise LLMIndisponivelError(f"Falha de rede ao chamar a Groq: {exc}") from exc
        except LLMConfigError as exc:
            logger.error("Configuração Groq inválida: model=%s detail=%s", self.modelo, exc)
            raise
        except Exception as exc:
            logger.exception(
                "Erro inesperado no adaptador Groq: model=%s detail=%s", self.modelo, exc
            )
            raise LLMIndisponivelError(
                f"Erro inesperado ao chamar Groq: {type(exc).__name__}: {exc}"
            ) from exc

        if not texto:
            logger.warning("Groq devolveu resposta vazia: model=%s", self.modelo)
            raise LLMIndisponivelError("A Groq devolveu uma resposta vazia.")
        return texto
