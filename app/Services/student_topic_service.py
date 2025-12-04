"""Student Topic Service

This module handles student completed topics management.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.Models.student_topic import Studenttopic
from uuid import UUID
from typing import List

logger = logging.getLogger(__name__)


class StudentTopicService:
    """Service for managing student completed topics."""
    
    @staticmethod
    async def add_topic_to_student(db: AsyncSession, student_id: UUID, topic_id: UUID) -> Studenttopic:
        """Mark a topic as completed by a student.
        
        Args:
            db: Database session
            student_id: Student UUID
            topic_id: Topic UUID
            
        Returns:
            Created student-topic record
        """
        db_student_topic = Studenttopic(
            student_id=student_id,
            topic_id=topic_id
        )
        db.add(db_student_topic)
        await db.commit()
        
        # Eagerly load the topic relationship to avoid MissingGreenlet error
        result = await db.execute(
            select(Studenttopic)
            .options(joinedload(Studenttopic.topic))
            .where(
                Studenttopic.student_id == student_id,
                Studenttopic.topic_id == topic_id
            )
        )
        db_student_topic = result.scalars().first()
        
        logger.info(f"Student {student_id} completed topic {topic_id}")
        return db_student_topic

    @staticmethod
    async def get_student_topics(db: AsyncSession, student_id: UUID) -> List[Studenttopic]:
        """Get all topics completed by a student.
        
        Args:
            db: Database session
            student_id: Student UUID
            
        Returns:
            List of completed topics
        """
        result = await db.execute(
            select(Studenttopic)
            .options(joinedload(Studenttopic.topic))
            .where(Studenttopic.student_id == student_id)
        )
        return result.scalars().all()

    @staticmethod
    async def remove_topic_from_student(db: AsyncSession, student_id: UUID, topic_id: UUID) -> bool:
        """Remove a completed topic from a student's record.
        
        Args:
            db: Database session
            student_id: Student UUID
            topic_id: Topic UUID
            
        Returns:
            True if removed, False if not found
        """
        result = await db.execute(select(Studenttopic).where(
            Studenttopic.student_id == student_id,
            Studenttopic.topic_id == topic_id
        ))
        db_student_topic = result.scalars().first()
        
        if not db_student_topic:
            return False
            
        await db.delete(db_student_topic)
        await db.commit()
        logger.info(f"Removed topic {topic_id} from student {student_id}")
        return True
