"""
embeddings.py — Generates embeddings LOCALLY using sentence-transformers.
No API calls, no rate limits, no quotas -- runs directly in this process.
"""

from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Loaded once at import time and reused for every call.
_model = SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()
