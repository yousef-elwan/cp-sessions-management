from pydantic import BaseModel
from uuid import UUID

class TopicPrerequisiteCreate(BaseModel):
    topic_id: UUID
    prerequisite_topic_id: UUID
