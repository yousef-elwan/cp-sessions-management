"""Topic Prerequisite Model

This module defines prerequisite relationships between topics.
"""
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.DB.base import Base


class TopicPrerequisite(Base):
    """Association table defining prerequisite relationships between topics.
    
    Example: If Topic A requires Topic B as a prerequisite:
    - topic_id = A
    - prerequisite_id = B
    """
    
    __tablename__ = "topic_prerequisites"

    # Composite Primary Key
    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    prerequisite_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    topic = relationship(
        "Topic",
        back_populates="prerequisites",
        primaryjoin="TopicPrerequisite.topic_id==Topic.id"
    )
    prerequisite = relationship(
        "Topic",
        back_populates="required_for",
        primaryjoin="TopicPrerequisite.prerequisite_id==Topic.id"
    )

    def __repr__(self):
        return f"<TopicPrerequisite(topic_id={self.topic_id}, prerequisite_id={self.prerequisite_id})>"
