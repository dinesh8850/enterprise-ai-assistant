"""
main.py — Entry point of the FastAPI backend.
"""

from fastapi import FastAPI
from app.api import chat
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend for the multi-agent enterprise AI assistant",
    version="0.1.0",
)

app.include_router(chat.router)


@app.get("/")
def read_root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.environment,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
