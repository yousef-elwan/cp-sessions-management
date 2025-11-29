"""JWT Token Management

This module handles JWT token creation and encoding.
"""
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Optional
from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
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
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
