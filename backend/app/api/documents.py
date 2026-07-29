"""
documents.py (router) — Handles file uploads and kicks off the ETL pipeline.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.repository import create_document, update_document_status
from app.etl.extract import extract_text

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

    # For now, just confirm extraction worked -- chunking/embedding/storing
    # (the rest of ETL) gets built in Task 7.3.
    update_document_status(db, document.id, status="processed")

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "status": "processed",
        "extracted_characters": len(text),
        "preview": text[:200],   # just the first 200 characters, so we can eyeball it worked
    }
