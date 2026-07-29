"""
repository.py — Functions for reading/writing our SQLAlchemy models
to and from Postgres. Keeping this separate from API route code means
our endpoints stay focused on HTTP concerns, while this file owns
all the actual database read/write logic.
"""

from sqlalchemy.orm import Session
from app.models.db_models import Document


def create_document(db: Session, filename: str, file_type: str, uploaded_by) -> Document:
    """Creates a new document record with status 'pending'."""
    document = Document(
        filename=filename,
        file_type=file_type,
        uploaded_by=uploaded_by,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)   # refreshes `document` with DB-generated values (like `id`)
    return document


def update_document_status(db: Session, document_id, status: str) -> None:
    """Updates a document's status, e.g. to 'processed' or 'failed'."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        document.status = status
        db.commit()
