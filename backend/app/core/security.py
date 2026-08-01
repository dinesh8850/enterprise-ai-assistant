"""
security.py — Password hashing and JWT creation/verification.

Centralizes all authentication-related crypto in one place, following
the same "one function, one job" pattern used throughout this project.
"""

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings

# CryptContext manages hashing -- bcrypt specifically, with salting
# handled automatically.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hashes a plain-text password for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plain-text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, role: str) -> str:
    """
    Creates a signed JWT containing the user's id and role,
    with an expiration time.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,      # "sub" (subject) is the JWT-standard field for "who this token is about"
        "role": role,
        "exp": expire,        # "exp" is the JWT-standard expiration field
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Verifies a JWT's signature and expiration, returning its payload if valid."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
