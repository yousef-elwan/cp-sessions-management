"""Notification Schemas

This module defines Pydantic models for notification data validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: UUID = Field(..., description="Notification ID")
    user_id: UUID = Field(..., description="User ID")
    type: str = Field(..., description="Notification type", example="booking_confirmation")
    message: str = Field(..., description="Notification message", example="Your session has been confirmed")
    is_read: bool = Field(..., description="Read status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "type": "booking_confirmation",
                "message": "Your session booking has been confirmed",
                "is_read": False,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )
