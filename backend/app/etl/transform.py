"""
transform.py — The "Transform" phase of ETL: takes raw extracted text
and splits it into overlapping chunks, ready for embedding.
"""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
