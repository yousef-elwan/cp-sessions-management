from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.notification import Notification
from uuid import UUID
from typing import List, Optional

class NotificationService:
    @staticmethod
    async def get_notifications_by_user(db: AsyncSession, user_id: UUID) -> List[Notification]:
        result = await db.execute(select(Notification).where(Notification.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalars().first()
        if not notification:
            return None
            
        notification.is_read = True
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
