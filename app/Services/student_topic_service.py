from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.student_topic import Studenttopic
from uuid import UUID
from typing import List, Optional

class StudentTopicService:
    @staticmethod
    async def add_topic_to_student(db: AsyncSession, student_id: UUID, topic_id: UUID) -> Studenttopic:
        db_student_topic = Studenttopic(
            student_id=student_id,
            topic_id=topic_id
        )
        db.add(db_student_topic)
        await db.commit()
        await db.refresh(db_student_topic)
        return db_student_topic

    @staticmethod
    async def get_student_topics(db: AsyncSession, student_id: UUID) -> List[Studenttopic]:
        result = await db.execute(select(Studenttopic).where(Studenttopic.student_id == student_id))
        return result.scalars().all()

    @staticmethod
    async def remove_topic_from_student(db: AsyncSession, student_id: UUID, topic_id: UUID) -> bool:
        result = await db.execute(select(Studenttopic).where(
            Studenttopic.student_id == student_id,
            Studenttopic.topic_id == topic_id
        ))
        db_student_topic = result.scalars().first()
        
        if not db_student_topic:
            return False
            
        await db.delete(db_student_topic)
        await db.commit()
        return True
