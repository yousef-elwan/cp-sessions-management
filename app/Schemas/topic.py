"""Topic Schemas

This module defines Pydantic models for topic data validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class TopicBase(BaseModel):
    """Base topic schema."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Topic name",
        example="Python Basics"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Topic description",
        example="Introduction to Python programming"
    )


class TopicCreate(TopicBase):
    """Schema for creating a topic."""
    pass


class TopicUpdate(BaseModel):
    """Schema for updating a topic."""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=120,
        description="Topic name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Topic description"
    )


class TopicResponse(TopicBase):
    """Schema for topic response."""
    id: UUID = Field(..., description="Topic ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Python Basics",
                "description": "Introduction to Python",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    )
