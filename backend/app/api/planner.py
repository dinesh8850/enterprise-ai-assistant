"""
planner.py (router) — Exposes our LangGraph workflow as the main
question-answering entry point for the whole system.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.graph_workflow import app_graph

router = APIRouter(prefix="/query", tags=["planner"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    routed_to: str
    sources: list


@router.post("/")
def query(request: QueryRequest):
    result = app_graph.invoke({
        "question": request.question,
        "chosen_agent": "",
        "answer": "",
        "sources": [],
    })

    return QueryResponse(
        answer=result["answer"],
        routed_to=result["chosen_agent"],
        sources=result.get("sources", []),
    )
