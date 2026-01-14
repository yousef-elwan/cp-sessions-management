"""JWT Token Management

This module handles JWT token creation and encoding.
"""
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Optional
from app.core.config import settings

def create_access_token(
    *,
    user_id: str,
    roles: list[str],
    permissions: list[str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload (e.g., {"sub": user_id, "role": "admin"})
        expires_delta: Optional custom expiration time. If None, uses default from settings.
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token({"sub": "user123", "role": "student"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: Dict[str, Any] = {
        "sub": user_id,          # standard JWT subject
        "user_id": user_id,      # explicit for clarity
        "roles": roles,          # list of role names
        "permissions": permissions,  # flattened permissions
        "iat": now,              # issued at
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt