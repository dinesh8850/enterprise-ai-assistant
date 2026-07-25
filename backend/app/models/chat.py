"""
chat.py — Defines the exact shape of data going in and out of the /chat endpoint.

Pydantic automatically validates incoming requests against ChatRequest,
and automatically formats outgoing data to match ChatResponse.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """What the client must send us."""
    message: str          # the user's question, required, must be text


class ChatResponse(BaseModel):
    """What we promise to send back."""
    reply: str             # the AI's answer (placeholder for now — real agents come in Step 9)
    session_id: str        # identifies which conversation this belongs to
