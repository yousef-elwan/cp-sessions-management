"""Notification Model

This module defines user notifications for system events.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM as pg_ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.DB.base import Base


class Notification(Base):
    """Notification model for user alerts and messages.
    
    Supports different notification types: booking confirmations, session updates,
    reminders, and system announcements.
    """
    
    __tablename__ = "notifications"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Notification Details
    type = Column(
        pg_ENUM("booking", "session_update", "reminder", "system", name="notification_types"),
        nullable=False
    )
    message = Column(String(500), nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, is_read={self.is_read})>"
