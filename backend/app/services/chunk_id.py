import hashlib


def gerar_chunk_id(texto_chunk: str, document_id: str, chunk_index: int) -> str:
    """
    Gera um ID determinístico para um chunk.
    - texto_chunk: conteúdo textual do chunk.
    - document_id: identificador único do documento (ex: nome do arquivo ou UUID).
    - chunk_index: posição do chunk no documento (para diferenciar chunks com texto idêntico).
    """
    base = f"{document_id}|{chunk_index}|{texto_chunk}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
