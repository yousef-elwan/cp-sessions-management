"""Notification Service

This module handles notification management operations.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.Models.notification import Notification
from uuid import UUID
from typing import List, Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications."""
    
    @staticmethod
    async def get_notifications_by_user(db: AsyncSession, user_id: UUID) -> List[Notification]:
        """Get all notifications for a user.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            List of notifications
        """
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_notification_by_id(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
        """Get a notification by ID.
        
        Args:
            db: Database session
            notification_id: Notification UUID
            
        Returns:
            Notification if found, None otherwise
        """
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        return result.scalars().first()

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: UUID) -> Optional[Notification]:
        """Mark a notification as read.
        
        Args:
            db: Database session
            notification_id: Notification UUID
            
        Returns:
            Updated notification if found, None otherwise
        """
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notification = result.scalars().first()
        if not notification:
            return None
            
        notification.is_read = True
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        logger.info(f"Marked notification {notification_id} as read")
        return notification
    
    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
        """Mark all notifications for a user as read.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Number of notifications updated
        """
        result = await db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        await db.commit()
        count = result.rowcount
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count
    
    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
        """Get count of unread notifications for a user.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Number of unread notifications
        """
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return len(result.scalars().all())
    
    @staticmethod
    async def delete_notification(db: AsyncSession, notification_id: UUID) -> bool:
        """Delete a notification.
        
        Args:
            db: Database session
            notification_id: Notification UUID
            
        Returns:
            True if deleted, False if not found
        """
        notification = await NotificationService.get_notification_by_id(db, notification_id)
        if not notification:
            return False
        
        await db.delete(notification)
        await db.commit()
        logger.info(f"Deleted notification {notification_id}")
        return True
