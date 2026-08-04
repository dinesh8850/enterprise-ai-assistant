"""
vector.py — Sets up the connection to our Qdrant vector database.
"""

from qdrant_client import QdrantClient
from app.core.config import settings

qdrant_client = QdrantClient(url=settings.qdrant_url, timeout=60)
