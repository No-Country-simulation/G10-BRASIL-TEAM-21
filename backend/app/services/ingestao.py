import hashlib

from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..infra.db.models import Chunk, Documento
from ..rag.chunker import dividir_em_chunks
from ..rag.embeddings import gerar_embeddings
from ..rag.extractor import extrair_texto
from ..rag.hashing import gerar_chunk_id


def processar_documento(
    file: UploadFile,
    conteudo: bytes,
    db: Session,
    usuario_id: str,
) -> tuple[Documento, list[Chunk]]:
    """
    Extrai o texto, divide em chunks, gera IDs determinísticos,
    salva o documento e os chunks no banco, e retorna ambos.
    """
    # 1. Extrai o texto (PDF ou TXT)
    texto = extrair_texto(conteudo, file.filename or "arquivo")

    # 2. Divide em chunks (retorna lista de objetos ChunkDocumento)
    chunks_objs = dividir_em_chunks(texto)

    # 3. Gera todos os vetores antes de abrir a transação de escrita no banco.
    embeddings = gerar_embeddings(
        [chunk.texto for chunk in chunks_objs], tipo_tarefa="RETRIEVAL_DOCUMENT"
    )

    # 4. Cria e salva o Documento principal
    doc = Documento(
        usuario_id=usuario_id,
        titulo=file.filename or "sem_nome",
        formato_origem="pdf" if (file.filename or "").lower().endswith(".pdf") else "texto",
        hash_conteudo=hashlib.sha256(conteudo).hexdigest(),
        tamanho_bytes=len(conteudo),
        status_upload="concluido",
    )
    db.add(doc)
    db.flush()  # Garante que doc.documento_id seja gerado

    # 5. Salva os chunks e seus vetores no banco
    chunks_criados = []
    for idx, chunk_obj in enumerate(chunks_objs):
        # A MÁGICA AQUI: pegamos a string do texto de dentro do objeto
        texto_do_chunk = chunk_obj.texto

        # Gera o hash único para este chunk
        chunk_id = gerar_chunk_id(
            texto_chunk=texto_do_chunk,
            document_id=str(doc.documento_id),
            chunk_index=idx,
        )

        chunk = Chunk(
            chunk_id=chunk_id,
            documento_id=doc.documento_id,
            ordem=idx,
            texto=texto_do_chunk,
            embedding=embeddings[idx],
        )
        # db.merge evita duplicatas caso o mesmo documento seja upado de novo
        db.merge(chunk)
        chunks_criados.append(chunk)

    db.commit()
    db.refresh(doc)

    return doc, chunks_criados
