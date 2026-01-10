import uuid
from sqlalchemy import Column, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.DB.base import Base


class UserRole(Base):
    __tablename__ = "app_user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("app_roles.id", ondelete="CASCADE"),
        nullable=False
    )

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )
