from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM as pg_ENUM
import uuid
from sqlalchemy.sql import func
from app.DB.base import Base

class TrainingSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    capacity = Column(Integer, default=10)
    current_attendees = Column(Integer, default=0)
    meet_link = Column(String(255), nullable=True)
    calendar_event_id = Column(String(255), nullable=True)
    status = Column(
        pg_ENUM("active", "cancelled", "completed", "upcoming",
                name="session_status"),
        default="upcoming"
    )
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
