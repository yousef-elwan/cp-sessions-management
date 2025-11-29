"""Student Topic Schemas

This module defines Pydantic models for student completed topics validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.Schemas.topic import TopicResponse


class StudentTopicCreate(BaseModel):
    """Schema for marking a topic as completed by a student."""
    topic_id: UUID = Field(..., description="Topic ID that was completed")


class StudentTopicResponse(BaseModel):
    """Schema for student-topic response."""
    student_id: UUID = Field(..., description="Student ID")
    topic_id: UUID = Field(..., description="Completed topic ID")
    completed_at: datetime = Field(..., description="Completion timestamp")
    
    topic: Optional[TopicResponse] = Field(None, description="Topic details")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "topic_id": "123e4567-e89b-12d3-a456-426614174001",
                "completed_at": "2024-01-01T12:00:00Z"
            }
        }
    )
