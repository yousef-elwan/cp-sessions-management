from sqlalchemy import Column, String, Boolean,DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM as pg_ENUM
from sqlalchemy.sql import func
import uuid
from app.DB.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(
        pg_ENUM("booking", "session_update", "reminder", "system",
                name="notification_types"),
        nullable=False
    )
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
