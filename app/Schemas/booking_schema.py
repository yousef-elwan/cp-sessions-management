"""Booking Schemas

This module defines Pydantic models for booking data validation.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.Schemas.user_schema import UserResponse
from app.Schemas.session_schema import SessionResponse


class BookingBase(BaseModel):
    """Base booking schema."""
    feedback: Optional[str] = Field(
        None,
        max_length=1000,
        description="Student feedback about the session",
        example="Great session! Learned a lot."
    )
    rating: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Rating from 1 to 5",
        example=5
    )


class BookingCreate(BaseModel):
    """Schema for creating a booking."""
    session_id: UUID = Field(..., description="Session ID to book")


class BookingFeedback(BaseModel):
    """Schema for submitting feedback."""
    feedback: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Feedback text (5-1000 characters)",
        example="The session was very informative and well-structured."
    )
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 to 5",
        example=4
    )


class BookingAttendance(BaseModel):
    """Schema for marking attendance."""
    attended: bool = Field(
        ...,
        description="Whether student attended the session",
        example=True
    )


class BookingResponse(BookingBase):
    """Schema for booking response."""
    id: UUID = Field(..., description="Booking ID")
    session_id: UUID = Field(..., description="Session ID")
    student_id: UUID = Field(..., description="Student ID")
    attended: bool = Field(..., description="Attendance status")
    created_at: datetime = Field(..., description="Booking creation timestamp")
    
    session: Optional[SessionResponse] = Field(None, description="Session details")
    student: Optional[UserResponse] = Field(None, description="Student details")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "student_id": "123e4567-e89b-12d3-a456-426614174002",
                "attended": True,
                "feedback": "Great session!",
                "rating": 5,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )
