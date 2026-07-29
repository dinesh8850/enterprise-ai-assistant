"""
ask.py (router) — Exposes the Document Agent as a real HTTP endpoint.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.document_agent import document_agent

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
    result = document_agent(request.question)

    citations = [
        Citation(filename=s["filename"], document_id=s["document_id"], score=s["score"])
        for s in result["sources"]
    ]

    return AskResponse(answer=result["answer"], citations=citations)
