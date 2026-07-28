"""
embeddings.py — Wraps Google's embedding model behind one simple function.
"""

from google import genai
from google.genai import types
from app.core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


def embed_text(text: str) -> list[float]:
    response = _client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=settings.embedding_dimensions
        ),
    )
    return response.embeddings[0].values
