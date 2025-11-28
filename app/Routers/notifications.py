from fastapi import APIRouter, Depends, HTTPException
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
    return await NotificationService.get_notifications_by_user(db, current_user.id)

@notifications_router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check ownership
    # We need to fetch notification first to check owner
    # For now assuming service handles it or we trust ID if we don't check owner
    # Ideally check owner.
    
    notification = await NotificationService.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return notification
