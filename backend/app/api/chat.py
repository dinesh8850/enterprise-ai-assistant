"""
chat.py (router) — Defines the actual /chat endpoint.
"""

import uuid
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def send_message(request: ChatRequest):
    # An expected, deliberate validation rule: don't allow a blank message.
    # Pydantic already guarantees `message` is a string, but it doesn't stop
    # an empty string "" or a message that's just spaces — we check that here.
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return ChatResponse(
        reply=f"You said: {request.message}",
        session_id=str(uuid.uuid4()),
    )
