"""Booking Model

This module defines student bookings for training sessions.
"""
from sqlalchemy import Column, ForeignKey, Boolean, Text, Integer, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.sql import func
from app.DB.base import Base


class Booking(Base):
    """Booking model representing student enrollment in training sessions.
    
    Tracks attendance, feedback, and ratings for completed sessions.
    """
    
    __tablename__ = "bookings"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Attendance Tracking
    attended = Column(Boolean, default=False, nullable=False)
    
    # Post-Session Feedback
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint('session_id', 'student_id', name='uc_session_student'),
    )

    # Relationships
    session = relationship("TrainingSession", back_populates="bookings")
    student = relationship("User", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, session_id={self.session_id}, student_id={self.student_id})>"
