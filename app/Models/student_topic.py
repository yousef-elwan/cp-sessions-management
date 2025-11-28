"""Student-Topic Association Model

This module defines the many-to-many relationship tracking which topics students have completed.
"""
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.DB.base import Base


class Studenttopic(Base):
    """Association table tracking completed topics for students."""
    
    __tablename__ = "student_topics"

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    completed_at = Column(DateTime, default=func.now())

    # Relationships
    student = relationship("User", back_populates="student_topics")
    topic = relationship("Topic", back_populates="student_topics")

    def __repr__(self):
        return f"<Studenttopic(student_id={self.student_id}, topic_id={self.topic_id})>"
