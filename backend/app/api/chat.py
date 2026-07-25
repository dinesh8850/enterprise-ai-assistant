"""
chat.py (router) — Defines the actual /chat endpoint.

For now this just echoes the message back, wrapped in the correct
response shape. Real AI logic gets connected here starting in Step 9,
once the Planner and specialist agents exist.
"""

import uuid
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse

# APIRouter lets us define routes in this file, separate from main.py,
# then "include" them into the main app later.
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def send_message(request: ChatRequest):
    # request.message is already validated — guaranteed to exist and be a string.
    # This placeholder just proves the full request -> response cycle works.
    return ChatResponse(
        reply=f"You said: {request.message}",
        session_id=str(uuid.uuid4()),
    )
