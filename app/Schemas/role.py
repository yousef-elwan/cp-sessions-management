from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# =====================
# Base
# =====================
class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


# =====================
# Create
# =====================
class RoleCreate(RoleBase):
    """
    Schema used when creating a new role
    """
    pass


# =====================
# Update
# =====================
class RoleUpdate(BaseModel):
    """
    Schema used when updating an existing role
    All fields are optional
    """
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


# =====================
# Response
# =====================
class RoleResponse(RoleBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # for SQLAlchemy ORM
