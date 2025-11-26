from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.Models.trainer_topic import Trainertopic

class TrainerTopicService:

    @staticmethod
    async def assign_topic_to_trainer(db: AsyncSession, trainer_id, topic_id):
        exists = await db.execute(
            select(Trainertopic).where(
                Trainertopic.trainer_id == trainer_id,
                Trainertopic.topic_id == topic_id
            )
        )
        if exists.scalar_one_or_none():
            return None  # Already exists

        record = Trainertopic(trainer_id=trainer_id, topic_id=topic_id)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_trainer_topics(db: AsyncSession, trainer_id):
        result = await db.execute(
            select(Trainertopic).where(Trainertopic.trainer_id == trainer_id)
        )
        return result.scalars().all()
