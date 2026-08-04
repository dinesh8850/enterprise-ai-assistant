"""
vector.py — Sets up the connection to our Qdrant vector database.
"""

from qdrant_client import QdrantClient
from app.core.config import settings

qdrant_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key or None,
    timeout=120,
)
