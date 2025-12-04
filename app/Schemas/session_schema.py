"""Session Schemas

This module defines Pydantic models for training session data validation.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.Schemas.user_schema import UserResponse
from app.Schemas.topic import TopicResponse


class SessionBase(BaseModel):
    """Base session schema."""
    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Session title",
        example="Python Basics Workshop"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Session description",
        example="Learn Python fundamentals"
    )
    start_time: datetime = Field(
        ...,
        description="Session start time",
        example="2025-01-15T10:00:00Z"
    )
    duration_minutes: int = Field(
        default=60,
        ge=15,
        le=480,
        description="Session duration in minutes (15-480)",
        example=90
    )
    capacity: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of attendees (1-100)",
        example=20
    )
    meet_link: Optional[str] = Field(
        None,
        max_length=255,
        description="Meeting link (Google Meet, Zoom, etc.)",
        example="https://meet.google.com/abc-defg-hij"
    )
    
    @field_validator('start_time', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Remove timezone info to match database TIMESTAMP WITHOUT TIME ZONE."""
        if isinstance(v, datetime):
            # If timezone-aware, convert to naive UTC datetime
            if v.tzinfo is not None:
                return v.replace(tzinfo=None)
        elif isinstance(v, str):
            # Parse ISO format string
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)
        return v



class SessionCreate(SessionBase):
    """Schema for creating a session."""
    topic_id: UUID = Field(..., description="Topic ID for this session")
    trainer_id: Optional[UUID] = Field(
        None,
        description="Trainer ID (Admin only, otherwise uses current user)"
    )


class SessionUpdate(BaseModel):
    """Schema for updating a session."""
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150,
        description="Session title"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Session description"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Session start time"
    )
    duration_minutes: Optional[int] = Field(
        None,
        ge=15,
        le=480,
        description="Session duration (15-480 minutes)"
    )
    capacity: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Maximum attendees (1-100)"
    )
    meet_link: Optional[str] = Field(
        None,
        max_length=255,
        description="Meeting link"
    )
    status: Optional[str] = Field(
        None,
        description="Session status"
    )

    @field_validator('start_time', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Remove timezone info to match database TIMESTAMP WITHOUT TIME ZONE."""
        if v is None:
            return v
        if isinstance(v, datetime):
            if v.tzinfo is not None:
                return v.replace(tzinfo=None)
        elif isinstance(v, str):
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)
        return v


class SessionResponse(SessionBase):
    """Schema for session response."""
    id: UUID = Field(..., description="Session ID")
    trainer_id: UUID = Field(..., description="Trainer ID")
    topic_id: UUID = Field(..., description="Topic ID")
    current_attendees: int = Field(..., description="Current number of bookings")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    trainer: Optional[UserResponse] = Field(None, description="Trainer details")
    topic: Optional[TopicResponse] = Field(None, description="Topic details")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Python Basics Workshop",
                "description": "Learn fundamentals",
                "start_time": "2025-01-15T10:00:00Z",
                "duration_minutes": 90,
                "capacity": 20,
                "current_attendees": 5,
                "status": "upcoming",
                "trainer_id": "123e4567-e89b-12d3-a456-426614174001",
                "topic_id": "123e4567-e89b-12d3-a456-426614174002",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    )
