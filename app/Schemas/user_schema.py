"""User Schemas

This module defines Pydantic models for user data validation and serialization.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    STUDENT = "student"
    TRAINER = "trainer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        example="Ahmed Mohamed",
        description="User's full name"
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
        example="ahmed@example.com",
        description="User's email address"
    )
    role: Optional[UserRole] = Field( # Role is not required in base, but useful for response
        default=UserRole.STUDENT,
        example=UserRole.STUDENT,
        description="User role: student, trainer, or admin"
    )


class UserRegister(UserBase):
    """Schema for user registration (public)."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        example="SecurePass123!",
        description="Password (minimum 8 characters)"
    )
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserCreate(UserRegister):
    """Schema for user creation (internal/admin)."""
    role: Optional[UserRole] = Field(
        default=UserRole.STUDENT,
        description="User role"
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(
        ...,
        example="ahmed@example.com",
        description="User's email address"
    )
    password: str = Field(
        ...,
        example="SecurePass123!",
        description="User's password"
    )


class UserResponse(UserBase):
    """Schema for user response (without password)."""
    id: UUID = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Ahmed Mohamed",
                "email": "ahmed@example.com",
                "role": "student",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-02T12:00:00Z"
            }
        }
    }
