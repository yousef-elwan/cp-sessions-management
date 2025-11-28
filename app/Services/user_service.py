from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.user import User
from uuid import UUID
from typing import List, Optional

class UserService:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
