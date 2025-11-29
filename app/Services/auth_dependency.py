"""Authentication Dependencies

This module provides FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from app.DB.session import get_db
from app.Models.user import User
from app.Schemas.auth import TokenData
from app.core.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
        
    Returns:
        Authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        token_data = TokenData(
            user_id=payload.get("sub"),
            role=payload.get("role")
        )

        if token_data.user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is an admin or super admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if authorized
        
    Raises:
        HTTPException: If user is not admin/super_admin
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is a super admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if authorized
        
    Raises:
        HTTPException: If user is not super_admin
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_current_trainer_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is a trainer, admin, or super admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if authorized
        
    Raises:
        HTTPException: If user is not trainer/admin/super_admin
    """
    if current_user.role not in ["trainer", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
