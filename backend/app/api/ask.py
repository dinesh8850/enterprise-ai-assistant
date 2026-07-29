"""
ask.py (router) — The real RAG endpoint: retrieves relevant chunks
and generates a grounded, cited answer.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.retrieval import retrieve_relevant_chunks, rerank_chunks
from app.core.generation import generate_answer

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    filename: str
    document_id: str
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


@router.post("/", response_model=AskResponse)
def ask_question(request: AskRequest):
    # Retrieve: cast a WIDER net first (more candidates than we'll actually use).
    candidates = retrieve_relevant_chunks(request.question, limit=8)

    # Filter out very weak vector matches before spending effort reranking them.
    RELEVANCE_THRESHOLD = 0.5
    candidates = [c for c in candidates if c["score"] >= RELEVANCE_THRESHOLD]

    # Rerank: precisely re-score the remaining candidates, keep only the best few.
    chunks = rerank_chunks(request.question, candidates, top_n=3)

    # Drop anything the reranker itself scored as not actually relevant.
    chunks = [c for c in chunks if c["rerank_score"] >= 5]

    if not chunks:
        return AskResponse(
            answer="I don't have any relevant documents to answer that question.",
            citations=[],
        )

    # Generate: ask Gemini to answer, grounded in only these chunks.
    context_texts = [chunk["text"] for chunk in chunks]
    answer = generate_answer(request.question, context_texts)

    # Build citations from the same chunks we retrieved -- this is
    # exactly why we stored filename/document_id back in Task 7.3.
    citations = [
        Citation(filename=c["filename"], document_id=c["document_id"], score=c["score"])
        for c in chunks
    ]

    return AskResponse(answer=answer, citations=citations)
