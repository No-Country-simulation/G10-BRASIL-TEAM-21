"""Fatiamento determinístico de texto para uso em pipelines de RAG."""

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkDocumento:
    """Um bloco de texto e seu identificador estável."""

    chunk_id: str
    texto: str
    ordem: int


def dividir_em_chunks(
    texto: str, tamanho: int = 900, sobreposicao: int = 150
) -> list[ChunkDocumento]:
    """Divide texto em blocos sobrepostos e calcula SHA-256 de cada bloco."""
    if tamanho <= 0:
        raise ValueError("O tamanho do chunk deve ser positivo.")
    if sobreposicao < 0 or sobreposicao >= tamanho:
        raise ValueError("A sobreposição deve estar entre zero e tamanho - 1.")

    blocos: list[ChunkDocumento] = []
    passo = tamanho - sobreposicao
    for inicio in range(0, len(texto), passo):
        trecho = texto[inicio : inicio + tamanho]
        if not trecho:
            break
        blocos.append(
            ChunkDocumento(
                chunk_id=hashlib.sha256(trecho.encode("utf-8")).hexdigest(),
                texto=trecho,
                ordem=len(blocos),
            )
        )
    return blocos
