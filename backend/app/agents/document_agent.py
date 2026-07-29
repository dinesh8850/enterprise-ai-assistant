"""
document_agent.py — Answers questions using our RAG pipeline
(retrieval + reranking + generation), wrapped in the shared agent shape.

This agent doesn't contain new logic -- it reuses everything built in
Step 8 (retrieval.py, generation.py), just packaged consistently so
the Planner (Task 9.5) can call it the same way as any other agent.
"""

from app.core.retrieval import retrieve_relevant_chunks, rerank_chunks
from app.core.generation import generate_answer

RELEVANCE_THRESHOLD = 0.5
RERANK_SCORE_THRESHOLD = 5


def document_agent(question: str) -> dict:
    """
    The Document Agent's main entry point. Same shared shape as
    sql_agent(): takes a question, returns agent_name/answer/sources.
    """
    candidates = retrieve_relevant_chunks(question, limit=8)
    candidates = [c for c in candidates if c["score"] >= RELEVANCE_THRESHOLD]

    chunks = rerank_chunks(question, candidates, top_n=3)
    chunks = [c for c in chunks if c["rerank_score"] >= RERANK_SCORE_THRESHOLD]

    if not chunks:
        return {
            "agent_name": "document_agent",
            "answer": "I don't have any relevant documents to answer that question.",
            "sources": [],
        }

    context_texts = [chunk["text"] for chunk in chunks]
    answer = generate_answer(question, context_texts)

    sources = [
        {"filename": c["filename"], "document_id": c["document_id"], "score": c["score"]}
        for c in chunks
    ]

    return {
        "agent_name": "document_agent",
        "answer": answer,
        "sources": sources,
    }
