# backend/app/services/ingestao.py
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.rag.extraction import extrair_texto          # tarefa 1
from app.rag.chunking import dividir_em_chunks        # tarefa 2
from app.rag.hashing import gerar_chunk_id            # tarefa 3
from app.infra.models import Document, Chunk

def processar_documento(
    file: UploadFile,
    conteudo: bytes,
    db: Session,
) -> Tuple[str, int]:
    """
    Recebe o arquivo, extrai o texto, faz o chunking,
    gera os IDs determinísticos e persiste documento + chunks.

    Retorna (document_id, quantidade_de_chunks).
    """
    # 1. Extrair texto (PDF ou TXT) – já implementado na tarefa 1
    texto = extrair_texto(conteudo, file.filename)

    # 2. Dividir em chunks (900 caracteres, overlap 150) – tarefa 2
    chunks_texto: List[str] = dividir_em_chunks(texto, tamanho=900, overlap=150)

    # 3. Metadados do documento
    doc = Document(
        filename=file.filename,
        size_bytes=len(conteudo),
    )
    db.add(doc)
    db.flush()                     # garante que doc.id já exista

    # 4. Persistir chunks com chunk_id determinístico
    for idx, txt in enumerate(chunks_texto):
        chunk_id = gerar_chunk_id(
            texto_chunk=txt,
            document_id=file.filename,   # ou hash do arquivo, se preferir
            chunk_index=idx,
        )
        chunk = Chunk(
            chunk_id=chunk_id,
            document_id=doc.id,
            chunk_index=idx,
            text=txt,
        )
        # merge evita duplicatas: se o chunk_id já existir, ele é ignorado/atualizado
        db.merge(chunk)

    db.commit()
    return str(doc.id), len(chunks_texto)