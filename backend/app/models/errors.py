"""
errors.py — Defines the consistent shape every error response will have,
no matter where in the app the error originates.
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str          # short, safe, human-readable message
    detail: str | None = None   # optional extra context, safe to show
