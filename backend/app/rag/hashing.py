# backend/app/rag/hashing.py
import hashlib
from typing import Optional

def gerar_chunk_id(
    texto_chunk: str,
    document_id: str,
    chunk_index: int,
) -> str:
    """
    Gera um ID determinístico para um chunk.

    Parâmetros
    ----------
    texto_chunk : str
        Conteúdo textual do chunk.
    document_id : str
        Identificador único do documento (ex.: nome do arquivo ou hash do conteúdo completo).
    chunk_index : int
        Posição do chunk no documento (para diferenciar chunks com texto idêntico).

    Retorna
    -------
    str
        Hash SHA-256 em formato hexadecimal.
    """
    base = f"{document_id}|{chunk_index}|{texto_chunk}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()