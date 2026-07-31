"""
deps.py — Shared FastAPI dependencies for authentication.

get_current_user is used by any endpoint that requires a logged-in
user -- it reads the Authorization header, verifies the JWT, and
returns the real User row from Postgres.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.db_models import User

# HTTPBearer is FastAPI's built-in tool for extracting a "Bearer <token>"
# header. It also automatically adds the "Authorize" button in /docs.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_role(*allowed_roles: str):
    """
    Returns a dependency that only allows users with one of the given
    roles. Usage: Depends(require_role("admin"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
