"""
planner.py (router) — Exposes our LangGraph workflow as the main
question-answering entry point for the whole system.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.agents.graph_workflow import app_graph
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.cache import get_cached_response, set_cached_response
from app.models.db_models import User

router = APIRouter(prefix="/query", tags=["planner"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    routed_to: str
    sources: list
    cached: bool = False


@router.post("/")
def query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    cached_response = get_cached_response(request.question)
    if cached_response:
        return QueryResponse(**cached_response, cached=True)

    if settings.mock_mode:
        return QueryResponse(
            answer=f"[MOCK] This is a fake answer to: {request.question}",
            routed_to="mock_agent",
            sources=[{"filename": "mock_document.pdf", "document_id": "mock-id", "score": 0.99}],
        )

    result = app_graph.invoke({
        "question": request.question,
        "chosen_agent": "",
        "answer": "",
        "sources": [],
    })

    response_data = {
        "answer": result["answer"],
        "routed_to": result["chosen_agent"],
        "sources": result.get("sources", []),
    }
    set_cached_response(request.question, response_data)
    return QueryResponse(**response_data)
