"""
cache.py — A simple Redis-backed cache for /query/ responses.

Caching identical questions avoids redundant Gemini API calls --
directly relevant given free-tier rate limits (5/min) and daily
quotas (20/day) we hit repeatedly during development.
"""

import hashlib
import json
import redis
from app.core.config import settings

_redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=2,
)


def _cache_key(question: str) -> str:
    """
    Turns a question into a fixed-length, safe cache key using a hash.
    Two identical questions always produce the same key; hashing avoids
    issues with special characters, length limits, or case differences.
    """
    normalized = question.strip().lower()
    return "query_cache:" + hashlib.sha256(normalized.encode()).hexdigest()


def get_cached_response(question: str) -> dict | None:
    """Returns a cached response dict if one exists, else None."""
    try:
        cached = _redis_client.get(_cache_key(question))
        return json.loads(cached) if cached else None
    except Exception:
        # ANY failure talking to Redis (unreachable, misconfigured, etc.)
        # should degrade to a cache miss, never crash the request.
        return None


def set_cached_response(question: str, response: dict) -> None:
    """Stores a response, expiring automatically after cache_ttl_seconds."""
    try:
        _redis_client.setex(
            _cache_key(question),
            settings.cache_ttl_seconds,
            json.dumps(response),
        )
    except Exception:
        pass  # Caching is an optimization, not a hard requirement -- never let a cache failure break the actual response.
