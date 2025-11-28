from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.session import TrainingSession
from app.Schemas.session_schema import SessionCreate, SessionUpdate
from uuid import UUID
from typing import List, Optional

class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, session_in: SessionCreate, trainer_id: UUID) -> TrainingSession:
        db_session = TrainingSession(
            **session_in.dict(),
            trainer_id=trainer_id
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: UUID) -> Optional[TrainingSession]:
        result = await db.execute(select(TrainingSession).where(TrainingSession.id == session_id))
        return result.scalars().first()

    @staticmethod
    async def get_all_sessions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TrainingSession]:
        result = await db.execute(select(TrainingSession).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_session(db: AsyncSession, session_id: UUID, session_in: SessionUpdate) -> Optional[TrainingSession]:
        db_session = await SessionService.get_session_by_id(db, session_id)
        if not db_session:
            return None
        
        update_data = session_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
            
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: UUID) -> bool:
        db_session = await SessionService.get_session_by_id(db, session_id)
        if not db_session:
            return False
        
        await db.delete(db_session)
        await db.commit()
        return True
