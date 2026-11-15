"""Geração de embeddings Gemini para indexação e busca semântica."""

from functools import lru_cache
from typing import Literal

from google import genai
from google.genai import types

from ..config import get_settings

DIMENSAO_EMBEDDING = 3072
MODELO_EMBEDDING_PADRAO = "gemini-embedding-001"
TAMANHO_LOTE = 100
TipoTarefaEmbedding = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]


class ErroEmbedding(RuntimeError):
    """Falha de configuração ou comunicação com o provedor de embeddings."""


@lru_cache(maxsize=4)
def _cliente_gemini(api_key: str) -> genai.Client:
    """Reutiliza o cliente entre requisições sem armazenar a chave no código."""
    return genai.Client(api_key=api_key)


def gerar_embeddings(textos: list[str], *, tipo_tarefa: TipoTarefaEmbedding) -> list[list[float]]:
    """Gera vetores de 3072 dimensões, processando entradas em lotes."""
    if not textos:
        return []

    configuracao = get_settings()
    api_key = configuracao.llm_api_key
    if not api_key:
        raise ErroEmbedding("LLM_API_KEY não está configurada.")
    if configuracao.embedding_dim not in (None, DIMENSAO_EMBEDDING):
        raise ErroEmbedding(
            f"EMBEDDING_DIM deve ser {DIMENSAO_EMBEDDING}; "
            f"valor configurado: {configuracao.embedding_dim}."
        )

    modelo = configuracao.embedding_model or MODELO_EMBEDDING_PADRAO
    cliente = _cliente_gemini(api_key)
    vetores: list[list[float]] = []

    try:
        for inicio in range(0, len(textos), TAMANHO_LOTE):
            lote = textos[inicio : inicio + TAMANHO_LOTE]
            resposta = cliente.models.embed_content(
                model=modelo,
                contents=lote,
                config=types.EmbedContentConfig(
                    task_type=tipo_tarefa,
                    output_dimensionality=DIMENSAO_EMBEDDING,
                ),
            )
            embeddings = resposta.embeddings or []
            if len(embeddings) != len(lote):
                raise ErroEmbedding("Gemini retornou quantidade inesperada de embeddings.")

            for embedding in embeddings:
                valores = embedding.values
                if valores is None or len(valores) != DIMENSAO_EMBEDDING:
                    tamanho = len(valores) if valores is not None else 0
                    raise ErroEmbedding(
                        f"Embedding retornado com {tamanho} dimensões; "
                        f"esperado {DIMENSAO_EMBEDDING}."
                    )
                vetores.append([float(valor) for valor in valores])
    except ErroEmbedding:
        raise
    except Exception as exc:
        raise ErroEmbedding("Não foi possível gerar embeddings no Gemini.") from exc

    return vetores
