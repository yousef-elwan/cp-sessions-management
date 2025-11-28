from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.Schemas.topic import TopicResponse

class StudentTopicCreate(BaseModel):
    topic_id: UUID

class StudentTopicResponse(BaseModel):
    student_id: UUID
    topic_id: UUID
    completed_at: datetime
    
    topic: Optional[TopicResponse] = None

    class Config:
        from_attributes = True
