"""Orquestrador do agente: principal -> reserva, com validação e nova tentativa (T11, RNF-06)."""

import logging
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from ..ports.llm import (
    LLMConfigError,
    LLMError,
    LLMIndisponivelError,
    LLMProvider,
    SaidaInvalidaError,
)

logger = logging.getLogger(__name__)

# 1 chamada + 1 nova tentativa quando o JSON vem fora do schema (RNF-06).
TENTATIVAS_VALIDACAO = 2
TENTATIVAS_PROVEDOR = 3


def _gerar_json_com_retry(
    provedor: LLMProvider, sistema: str, usuario: str, schema: type[BaseModel]
) -> str:
    """Repete apenas falhas transitórias antes de avançar para o próximo provedor."""

    def registrar_espera(retry_state) -> None:
        logger.warning(
            "LLM retry agendado: provider=%s model=%s tentativa=%d espera_s=%.2f",
            provedor.nome,
            provedor.modelo,
            retry_state.attempt_number + 1,
            retry_state.next_action.sleep if retry_state.next_action else 0,
        )

    @retry(
        retry=retry_if_exception_type(LLMIndisponivelError),
        stop=stop_after_attempt(TENTATIVAS_PROVEDOR),
        wait=wait_random_exponential(multiplier=1, min=1, max=4),
        before_sleep=registrar_espera,
        reraise=True,
    )
    def tentativa() -> str:
        return provedor.gerar_json(sistema, usuario, schema)

    return tentativa()


class AgenteFalhouError(LLMError):
    """Nenhum provedor da cadeia entregou um JSON válido."""

    def __init__(self, falhas: list[str], so_saida_invalida: bool) -> None:
        super().__init__("; ".join(falhas))
        self.falhas = falhas
        self.so_saida_invalida = so_saida_invalida


@dataclass(frozen=True)
class ResultadoLLM:
    saida: BaseModel
    provedor: str
    modelo: str
    usou_fallback: bool


def _chamar_e_validar(
    provedor: LLMProvider, sistema: str, usuario: str, schema: type[BaseModel]
) -> BaseModel:
    """Chama um provedor e valida o JSON; se a validação falhar, tenta de novo (tenacity)."""
    dica = {"erro": ""}

    @retry(
        stop=stop_after_attempt(TENTATIVAS_VALIDACAO),
        retry=retry_if_exception_type(SaidaInvalidaError),
        reraise=True,
    )
    def tentativa() -> BaseModel:
        prompt = usuario
        if dica["erro"]:
            prompt += (
                "\n\nA resposta anterior não passou na validação. Corrija e responda só o JSON. "
                f"Erro: {dica['erro']}"
            )
        texto = _gerar_json_com_retry(provedor, sistema, prompt, schema)
        try:
            return schema.model_validate_json(texto)
        except ValidationError as exc:
            dica["erro"] = str(exc)[:600]
            raise SaidaInvalidaError(f"JSON fora do schema: {dica['erro']}") from exc

    return tentativa()


def executar_cadeia(
    cadeia: list[LLMProvider], sistema: str, usuario: str, schema: type[BaseModel]
) -> ResultadoLLM:
    """Percorre os provedores na ordem. Falha passageira, config ou JSON inválido -> próximo."""
    falhas: list[str] = []
    so_saida_invalida = True
    for posicao, provedor in enumerate(cadeia):
        try:
            saida = _chamar_e_validar(provedor, sistema, usuario, schema)
        except SaidaInvalidaError as exc:
            falhas.append(f"{provedor.nome}: {exc}")
        except (LLMIndisponivelError, LLMConfigError) as exc:
            so_saida_invalida = False
            falhas.append(f"{provedor.nome}: {exc}")
        else:
            return ResultadoLLM(saida, provedor.nome, provedor.modelo, posicao > 0)
        logger.warning("LLM %s falhou (%s); tentando o próximo.", provedor.nome, falhas[-1][:200])
    raise AgenteFalhouError(falhas, so_saida_invalida)
