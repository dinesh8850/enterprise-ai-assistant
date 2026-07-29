"""
extract.py — Extracts raw text from uploaded files, based on file type.

This is the "Extract" phase of ETL: read the raw file, get plain text out.
Cleaning/chunking (the "Transform" phase) happens separately, in Task 7.3.
"""

from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Reads a PDF's bytes and returns all its text, concatenated
    across every page.
    """
    reader = PdfReader(BytesIO(file_bytes))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    return "\n".join(pages_text)


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """
    Dispatches to the correct extractor based on file_type.
    More formats (docx, csv, etc.) get added here in later tasks --
    this function is the single place that decides "how do I read this file?"
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes)
    raise ValueError(f"Unsupported file type: {file_type}")
