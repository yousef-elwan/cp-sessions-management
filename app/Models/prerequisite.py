from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.DB.base import Base

class TopicPrerequisite(Base):
    __tablename__ = "topic_prerequisites"

    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    prerequisite_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=func.now())
