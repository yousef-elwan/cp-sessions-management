from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.Schemas.user_schema import UserResponse
from app.Schemas.topic import TopicResponse

class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    duration_minutes: Optional[int] = 60
    capacity: Optional[int] = 10
    meet_link: Optional[str] = None

class SessionCreate(SessionBase):
    topic_id: UUID

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    capacity: Optional[int] = None
    meet_link: Optional[str] = None
    status: Optional[str] = None

class SessionResponse(SessionBase):
    id: UUID
    trainer_id: UUID
    topic_id: UUID
    current_attendees: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    trainer: Optional[UserResponse] = None
    topic: Optional[TopicResponse] = None

    class Config:
        from_attributes = True
