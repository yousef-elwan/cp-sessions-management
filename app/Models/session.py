"""Training Session Model

This module defines training sessions scheduled by trainers.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM as pg_ENUM
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.sql import func
from app.DB.base import Base


class TrainingSession(Base):
    """Training session model representing scheduled learning sessions.
    
    Sessions are created by trainers for specific topics and can have multiple student bookings.
    """
    
    __tablename__ = "sessions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    trainer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session Information
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    start_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Capacity Management
    capacity = Column(Integer, default=10, nullable=False)
    current_attendees = Column(Integer, default=0, nullable=False)
    
    # External Integration
    meet_link = Column(String(255), nullable=True)
    calendar_event_id = Column(String(255), nullable=True)
    
    # Status
    status = Column(
        pg_ENUM("active", "cancelled", "completed", "upcoming", name="session_status"),
        default="upcoming",
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    trainer = relationship("User", back_populates="sessions")
    topic = relationship("Topic", back_populates="sessions")
    bookings = relationship("Booking", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TrainingSession(id={self.id}, title={self.title}, status={self.status})>"
    
    @property
    def is_full(self) -> bool:
        """Check if session has reached capacity."""
        return self.current_attendees >= self.capacity
    
    @property
    def available_seats(self) -> int:
        """Get number of available seats."""
        return max(0, self.capacity - self.current_attendees)
