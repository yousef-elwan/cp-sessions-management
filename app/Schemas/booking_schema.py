from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.Schemas.user_schema import UserResponse
from app.Schemas.session_schema import SessionResponse

class BookingBase(BaseModel):
    feedback: Optional[str] = None
    rating: Optional[int] = None

class BookingCreate(BaseModel):
    session_id: UUID

class BookingResponse(BookingBase):
    id: UUID
    session_id: UUID
    student_id: UUID
    attended: bool
    created_at: datetime
    
    session: Optional[SessionResponse] = None
    student: Optional[UserResponse] = None

    class Config:
        from_attributes = True
