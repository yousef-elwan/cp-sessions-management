"""Authentication Schemas

This module defines Pydantic models for authentication data validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    user_id: Optional[UUID] = Field(None, description="User ID from token")

    roles: List[str] = Field(
        default_factory=list,
        description="List of role names assigned to the user"
    )

    permissions: List[str] = Field(
        default_factory=list,
        description="Flattened list of permission names for the user"
    )