"""User Model

This module defines the User model representing students, trainers, and admins.
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM as pg_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.DB.base import Base


class User(Base):
    """User model for authentication and role management.
    
    Supports three roles: student, trainer, and admin.
    """
    
    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User Information
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    
    # Role and Status
    role = Column(
        pg_ENUM("student", "trainer", "admin", "super_admin", name="user_roles"),
        default="student",
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    trainer_topics = relationship("Trainertopic", back_populates="trainer", cascade="all, delete-orphan")
    sessions = relationship("TrainingSession", back_populates="trainer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="student", cascade="all, delete-orphan")
    student_topics = relationship("Studenttopic", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("UserRole",backref="user",cascade="all, delete-orphan")



    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
