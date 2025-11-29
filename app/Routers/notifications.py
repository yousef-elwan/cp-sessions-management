"""Notification Router

This module handles notification-related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.DB.session import get_db
from app.Schemas.notification_schema import NotificationResponse
from app.Services.notification_service import NotificationService
from app.Services.auth_dependency import get_current_user
from app.Models.user import User

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@notifications_router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications for the current user.
    
    Returns notifications sorted by creation date (newest first).
    """
    return await NotificationService.get_notifications_by_user(db, current_user.id)


@notifications_router.get("/unread/count", response_model=dict)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications for current user."""
    count = await NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@notifications_router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read.
    
    Only the notification owner can mark it as read.
    """
    # SECURITY FIX: Check ownership BEFORE modifying
    notification = await NotificationService.get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Now safe to mark as read
    notification = await NotificationService.mark_as_read(db, notification_id)
    return notification


@notifications_router.patch("/read-all", response_model=dict)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for current user."""
    count = await NotificationService.mark_all_as_read(db, current_user.id)
    return {"marked_read": count}


@notifications_router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification.
    
    Only the notification owner can delete it.
    """
    # Check ownership before deleting
    notification = await NotificationService.get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await NotificationService.delete_notification(db, notification_id)
    return None
