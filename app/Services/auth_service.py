"""Authentication Service

This module provides authentication and user management services.
"""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Dict, Any

from fastapi import HTTPException, status
from app.Models.user import User
from app.Schemas.user_schema import UserCreate, UserLogin
from app.core.hash import get_password_hash, verify_password
from app.core.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Configure logger
logger = logging.getLogger(__name__)


async def register_user_service(user_data: UserCreate, db: AsyncSession) -> User:
    """Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists or database error occurs
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).filter(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
            role=user_data.role or "student"
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"New user registered: {db_user.email}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )


async def login_user_service(user_data: UserLogin, db: AsyncSession) -> Dict[str, Any]:
    """Authenticate user and generate access token.
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        Dictionary containing access token and token type
        
    Raises:
        HTTPException: If credentials are invalid or database error occurs
    """
    try:
        # Retrieve user
        result = await db.execute(
            select(User).filter(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()
        
        # Verify credentials
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


async def get_user_by_id_service(user_id: uuid.UUID, db: AsyncSession) -> User:
    """Retrieve user by ID.
    
    Args:
        user_id: User UUID
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user"
        )
