"""
load.py — The "Load" phase of ETL: embeds each chunk and stores it
in Qdrant, tagged with metadata linking it back to its source document.
"""

import uuid
from qdrant_client.models import PointStruct
from app.db.vector import qdrant_client
from app.core.embeddings import embed_text


def load_chunks_to_qdrant(chunks: list[str], document_id: str, filename: str) -> int:
    points = []
    for chunk in chunks:
        vector = embed_text(chunk)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "document_id": document_id,
                    "filename": filename,
                },
            )
        )

    if points:
        qdrant_client.upsert(collection_name="document_chunks", points=points)

    return len(points)
