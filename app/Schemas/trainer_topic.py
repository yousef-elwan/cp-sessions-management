"""Trainer Topic Schemas

This module defines Pydantic models for trainer-topic assignment validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class TrainerTopicBase(BaseModel):
    """Base trainer-topic schema."""
    trainer_id: UUID = Field(..., description="Trainer ID")
    topic_id: UUID = Field(..., description="Topic ID")


class TrainerTopicCreate(TrainerTopicBase):
    """Schema for creating a trainer-topic assignment."""
    pass


class TrainerTopicResponse(TrainerTopicBase):
    """Schema for trainer-topic response."""
    created_at: datetime = Field(..., description="Assignment creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "trainer_id": "123e4567-e89b-12d3-a456-426614174000",
                "topic_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )
