"""Trainer-Topic Association Model

This module defines the many-to-many relationship between trainers and topics.
"""
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.DB.base import Base


class Trainertopic(Base):
    """Association table linking trainers to topics they can teach."""
    
    __tablename__ = "trainer_topics"

    trainer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = Column(DateTime, default=func.now())

    # Relationships
    trainer = relationship("User", back_populates="trainer_topics")
    topic = relationship("Topic", back_populates="trainer_topics")

    def __repr__(self):
        return f"<Trainertopic(trainer_id={self.trainer_id}, topic_id={self.topic_id})>"