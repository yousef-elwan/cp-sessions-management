"""Trainer Topic Service

This module handles trainer-topic assignment operations.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.Models.trainer_topic import Trainertopic
from uuid import UUID
from typing import List, Optional

logger = logging.getLogger(__name__)


class TrainerTopicService:
    """Service for managing trainer-topic assignments."""

    @staticmethod
    async def assign_topic_to_trainer(
        db: AsyncSession, 
        trainer_id: UUID, 
        topic_id: UUID
    ) -> Optional[Trainertopic]:
        """Assign a topic to a trainer.
        
        Args:
            db: Database session
            trainer_id: Trainer UUID
            topic_id: Topic UUID
            
        Returns:
            Created trainer-topic record if new, None if already exists
        """
        exists = await db.execute(
            select(Trainertopic).where(
                Trainertopic.trainer_id == trainer_id,
                Trainertopic.topic_id == topic_id
            )
        )
        if exists.scalar_one_or_none():
            logger.warning(f"Trainer {trainer_id} already assigned to topic {topic_id}")
            return None  # Already exists

        record = Trainertopic(trainer_id=trainer_id, topic_id=topic_id)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(f"Assigned trainer {trainer_id} to topic {topic_id}")
        return record

    @staticmethod
    async def get_trainer_topics(db: AsyncSession, trainer_id: UUID) -> List[Trainertopic]:
        """Get all topics assigned to a trainer.
        
        Args:
            db: Database session
            trainer_id: Trainer UUID
            
        Returns:
            List of trainer-topic assignments
        """
        result = await db.execute(
            select(Trainertopic).where(Trainertopic.trainer_id == trainer_id)
        )
        return result.scalars().all()
