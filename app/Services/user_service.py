"""User Service

This module handles user data retrieval operations.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.Models.user import User
from uuid import UUID
from typing import List, Optional

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user data."""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
