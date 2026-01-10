from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionOut(PermissionBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
