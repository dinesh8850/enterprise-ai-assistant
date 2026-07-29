"""
planner.py (router) — Exposes the Planner Agent as the main
question-answering entry point for the whole system.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.planner import planner_agent

router = APIRouter(prefix="/query", tags=["planner"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    routed_to: str
    sources: list


@router.post("/")
def query(request: QueryRequest):
    result = planner_agent(request.question)
    return QueryResponse(
        answer=result["answer"],
        routed_to=result["routed_by_planner_to"],
        sources=result.get("sources", []),
    )
