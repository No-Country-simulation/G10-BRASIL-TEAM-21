"""Busca dos chunks mais próximos por similaridade de cosseno."""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..infra.db.models import Chunk, Documento
from .embeddings import DIMENSAO_EMBEDDING, gerar_embeddings


@dataclass(frozen=True)
class ResultadoBusca:
    """Chunk recuperado e similaridade estimada (1 - distância cosseno)."""

    chunk: Chunk
    similaridade: float


def buscar_chunks_similares(
    db: Session,
    pergunta: str,
    usuario_id: uuid.UUID,
    limite: int = 3,
) -> list[ResultadoBusca]:
    """Retorna os chunks mais próximos, limitando a busca aos documentos do usuário."""
    pergunta = pergunta.strip()
    if not pergunta:
        return []
    if limite < 1:
        raise ValueError("O limite de resultados deve ser positivo.")

    vetor_pergunta = gerar_embeddings([pergunta], tipo_tarefa="RETRIEVAL_QUERY")[0]
    if len(vetor_pergunta) != DIMENSAO_EMBEDDING:
        raise ValueError("O vetor da pergunta tem dimensão incompatível com os embeddings salvos.")

    distancia = Chunk.embedding.cosine_distance(vetor_pergunta).label("distancia_cosseno")
    consulta = (
        select(Chunk, distancia)
        .join(Documento, Documento.documento_id == Chunk.documento_id)
        .where(Documento.usuario_id == usuario_id, Chunk.embedding.is_not(None))
        .order_by(distancia)
        .limit(limite)
    )

    return [
        ResultadoBusca(chunk=chunk, similaridade=max(-1.0, min(1.0, 1.0 - distancia_cosseno)))
        for chunk, distancia_cosseno in db.execute(consulta).all()
    ]
