"""
documents.py (router) — Handles file uploads and kicks off the ETL pipeline.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.repository import create_document, update_document_status
from app.models.db_models import Document
from app.etl.extract import extract_text
from app.etl.transform import chunk_text
from app.etl.load import load_chunks_to_qdrant

router = APIRouter(prefix="/documents", tags=["documents"])

# Map uploaded filename extensions to our internal file_type labels.
SUPPORTED_EXTENSIONS = {"pdf": "pdf"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Figure out the file type from its extension.
    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{extension}'. Supported: {list(SUPPORTED_EXTENSIONS)}",
        )
    file_type = SUPPORTED_EXTENSIONS[extension]

    # Save metadata in Postgres first, with status "pending".
    # NOTE: uploaded_by is hardcoded to None for now -- real user
    # association comes once authentication exists, in Step 12.
    document = create_document(db, filename=file.filename, file_type=file_type, uploaded_by=None)

    # Read the actual file bytes and extract text (Extract phase of ETL).
    file_bytes = await file.read()
    try:
        text = extract_text(file_bytes, file_type)
    except Exception:
        update_document_status(db, document.id, status="failed")
        raise HTTPException(status_code=500, detail="Failed to extract text from file")

    # Transform: split the extracted text into overlapping chunks.
    chunks = chunk_text(text)

    # Load: embed each chunk and store it in Qdrant, tagged with this document.
    try:
        stored_count = load_chunks_to_qdrant(chunks, document_id=str(document.id), filename=document.filename)
    except Exception:
        update_document_status(db, document.id, status="failed")
        raise HTTPException(status_code=500, detail="Failed to embed and store document chunks")

    update_document_status(db, document.id, status="processed")

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "status": "processed",
        "extracted_characters": len(text),
        "chunks_created": len(chunks),
        "chunks_stored_in_qdrant": stored_count,
        "preview": text[:200],
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """Returns metadata for every uploaded document -- powers the dashboard."""
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "file_type": d.file_type,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in documents
    ]
