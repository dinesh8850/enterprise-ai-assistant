"""
retrieval.py — Searches Qdrant for chunks relevant to a question.

This is the "Retrieval" half of RAG: given a question, find the most
semantically similar stored chunks, using the same embedding model
that was used to store them (Task 6.3/7.3).
"""

from app.db.vector import qdrant_client
from app.core.embeddings import embed_text
from google import genai
from google.genai import types
from app.core.config import settings

_rerank_client = genai.Client(api_key=settings.gemini_api_key)


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

def rerank_chunks(question: str, chunks: list[dict], top_n: int = 3) -> list[dict]:
    """
    Re-scores retrieved chunks for relevance to the question using Gemini,
    then returns the top_n best. This is a lightweight, LLM-based reranker:
    it looks at the question and EACH chunk together for a more precise
    relevance judgment than raw vector similarity alone provides.
    """
    if not chunks:
        return []

    scored = []
    for chunk in chunks:
        prompt = (
            f"Question: {question}\n\n"
            f"Passage: {chunk['text']}\n\n"
            "On a scale of 0 to 10, how directly does this passage answer "
            "the question? Reply with ONLY a number, nothing else."
        )
        response = _rerank_client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        try:
            relevance_score = float(response.text.strip())
        except (ValueError, AttributeError):
            relevance_score = 0.0

        scored.append({**chunk, "rerank_score": relevance_score})

    # Sort by the new, more precise relevance score, best first.
    scored.sort(key=lambda c: c["rerank_score"], reverse=True)
    return scored[:top_n]
