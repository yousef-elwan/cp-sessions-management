"""Session Service

This module handles training session management operations.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.Models.session import TrainingSession
from app.Schemas.session_schema import SessionCreate, SessionUpdate
from uuid import UUID
from typing import List, Optional

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing training sessions."""
    
    @staticmethod
    async def create_session(db: AsyncSession, session_in: SessionCreate, trainer_id: UUID) -> TrainingSession:
        """Create a new training session.
        
        Args:
            db: Database session
            session_in: Session creation data
            trainer_id: ID of the trainer for this session
            
        Returns:
            Created training session
        """
        db_session = TrainingSession(
            **session_in.model_dump(exclude={'trainer_id'}),
            trainer_id=trainer_id
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        # Eagerly load relationships to avoid lazy loading issues
        result = await db.execute(
            select(TrainingSession)
            .options(selectinload(TrainingSession.trainer), selectinload(TrainingSession.topic))
            .where(
                TrainingSession.id == db_session.id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        db_session = result.scalar_one()
        
        logger.info(f"Created session {db_session.id} for trainer {trainer_id}")
        return db_session

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: UUID) -> Optional[TrainingSession]:
        """Get a training session by ID.
        
        Args:
            db: Database session
            session_id: Session UUID
            
        Returns:
            Training session if found, None otherwise
        """
        result = await db.execute(
            select(TrainingSession)
            .options(selectinload(TrainingSession.trainer), selectinload(TrainingSession.topic))
            .where(
                TrainingSession.id == session_id,
                TrainingSession.deleted_at.is_(None)
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_sessions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TrainingSession]:
        """Get all training sessions with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of training sessions
        """
        result = await db.execute(
            select(TrainingSession)
            .options(selectinload(TrainingSession.trainer), selectinload(TrainingSession.topic))
            .where(TrainingSession.deleted_at.is_(None))
            .order_by(TrainingSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_session(db: AsyncSession, session_id: UUID, session_in: SessionUpdate) -> Optional[TrainingSession]:
        """Update an existing training session.
        
        Args:
            db: Database session
            session_id: Session UUID to update
            session_in: Updated session data
            
        Returns:
            Updated training session if found, None otherwise
        """
        db_session = await SessionService.get_session_by_id(db, session_id)
        if not db_session:
            return None
        
        update_data = session_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
            
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        logger.info(f"Updated session {session_id}")
        return db_session

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: UUID) -> bool:
        """Delete a training session.
        
        Args:
            db: Database session
            session_id: Session UUID to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_session = await SessionService.get_session_by_id(db, session_id)
        if not db_session:
            return False
        
        await db.delete(db_session)
        await db.commit()
        logger.info(f"Deleted session {session_id}")
        return True
