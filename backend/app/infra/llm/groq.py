"""Provedor reserva: Groq com saída JSON."""

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
            # Os retries são controlados pelo orquestrador.
            self._client = groq_sdk.Groq(
                api_key=self._api_key,
                timeout=self._timeout_s,
                max_retries=0,
            )
        return self._client

    def gerar_json(self, sistema: str, usuario: str, schema: type[BaseModel]) -> str:
        try:
            cliente = self._cliente()
            parametros_extras = (
                {"reasoning_effort": "low"} if self.modelo.startswith("openai/gpt-oss-") else None
            )

            resposta = cliente.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario},
                ],
                response_format={"type": "json_object"},
                max_tokens=4096,
                extra_body=parametros_extras,
                temperature=0.4,
            )

            escolha = resposta.choices[0] if resposta.choices else None
            mensagem = escolha.message if escolha else None
            texto = mensagem.content.strip() if mensagem and mensagem.content else None

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
            logger.warning(
                "Falha de transporte Groq: model=%s detail=%s",
                self.modelo,
                exc,
            )
            raise LLMIndisponivelError(f"Falha de rede ao chamar a Groq: {exc}") from exc

        except LLMConfigError as exc:
            logger.error(
                "Configuração Groq inválida: model=%s detail=%s",
                self.modelo,
                exc,
            )
            raise

        except Exception as exc:
            logger.exception(
                "Erro inesperado no adaptador Groq: model=%s detail=%s",
                self.modelo,
                exc,
            )
            raise LLMIndisponivelError(
                f"Erro inesperado ao chamar Groq: {type(exc).__name__}: {exc}"
            ) from exc

        if not texto:
            uso = resposta.usage
            logger.warning(
                "Groq devolveu resposta vazia: model=%s finish_reason=%s "
                "prompt_tokens=%s completion_tokens=%s reasoning_present=%s "
                "refusal_present=%s",
                self.modelo,
                escolha.finish_reason if escolha else None,
                uso.prompt_tokens if uso else None,
                uso.completion_tokens if uso else None,
                bool(mensagem and getattr(mensagem, "reasoning", None)),
                bool(mensagem and getattr(mensagem, "refusal", None)),
            )
            raise LLMIndisponivelError("A Groq devolveu uma resposta vazia.")

        return texto
