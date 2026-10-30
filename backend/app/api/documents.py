# backend/app/api/documents.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infra.database import get_db
from app.services.ingestao import processar_documento
from app.schemas.document import UploadResponse

router = APIRouter(prefix="/documents", tags=["documentos"])

@router.post("/upload", response_model=UploadResponse)
async def upload_documento(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Recebe um PDF ou TXT, processa (extração → chunking → hash)
    e salva os metadados e chunks no banco.
    """
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Formato não suportado. Envie PDF ou TXT.")

    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    try:
        doc_id, n_chunks = processar_documento(file, conteudo, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        chunks_gerados=n_chunks,
    )