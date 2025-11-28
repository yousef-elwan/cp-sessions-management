"""Topic Model

This module defines topics that can be taught in training sessions.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.DB.base import Base


class Topic(Base):
    """Topic model representing subjects available for training.
    
    Topics can have prerequisites and can be taught by multiple trainers.
    """
    
    __tablename__ = "topics"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Topic Information
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    trainer_topics = relationship("Trainertopic", back_populates="topic", cascade="all, delete-orphan")
    sessions = relationship("TrainingSession", back_populates="topic", cascade="all, delete-orphan")
    student_topics = relationship("Studenttopic", back_populates="topic", cascade="all, delete-orphan")

    # Self-referential relationships through TopicPrerequisite
    prerequisites = relationship(
        "TopicPrerequisite",
        back_populates="topic",
        primaryjoin="Topic.id==TopicPrerequisite.topic_id",
        cascade="all, delete-orphan"
    )
    required_for = relationship(
        "TopicPrerequisite",
        back_populates="prerequisite",
        primaryjoin="Topic.id==TopicPrerequisite.prerequisite_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Topic(id={self.id}, name={self.name})>"
