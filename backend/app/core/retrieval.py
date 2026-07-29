"""
retrieval.py — Searches Qdrant for chunks relevant to a question.

This is the "Retrieval" half of RAG: given a question, find the most
semantically similar stored chunks, using the same embedding model
that was used to store them (Task 6.3/7.3).
"""

from app.db.vector import qdrant_client
from app.core.embeddings import embed_text


def retrieve_relevant_chunks(question: str, limit: int = 3) -> list[dict]:
    """
    Returns the top `limit` chunks most relevant to `question`,
    each as a dict with text, filename, document_id, and score.
    """
    question_vector = embed_text(question)

    results = qdrant_client.query_points(
        collection_name="document_chunks",
        query=question_vector,
        limit=limit,
    )

    chunks = []
    for point in results.points:
        chunks.append({
            "text": point.payload["text"],
            "filename": point.payload["filename"],
            "document_id": point.payload["document_id"],
            "score": point.score,
        })
    return chunks
