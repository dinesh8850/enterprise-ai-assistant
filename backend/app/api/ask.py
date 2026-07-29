"""
ask.py (router) — The real RAG endpoint: retrieves relevant chunks
and generates a grounded, cited answer.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.retrieval import retrieve_relevant_chunks
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
    # Retrieve: find the most relevant chunks for this question.
    chunks = retrieve_relevant_chunks(request.question, limit=3)

    # Filter out weak matches -- a low similarity score means this
    # chunk probably isn't actually relevant, even if it was the
    # "closest" thing we had.
    RELEVANCE_THRESHOLD = 0.6
    chunks = [c for c in chunks if c["score"] >= RELEVANCE_THRESHOLD]

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
