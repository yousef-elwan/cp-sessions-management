from pydantic import BaseModel, UUID4
from datetime import datetime
from pydantic import ConfigDict

class TrainerTopicBase(BaseModel):
    trainer_id: UUID4
    topic_id: UUID4

class TrainerTopicCreate(TrainerTopicBase):
    pass

class TrainerTopicResponse(TrainerTopicBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
