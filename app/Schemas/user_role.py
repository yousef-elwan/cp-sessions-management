from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID

class UserRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

