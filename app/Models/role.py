from sqlalchemy import Column, String, ForeignKey,DateTime,Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.DB.base import Base
import uuid


class AppRole(Base):
    __tablename__ = "app_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role_permissions = relationship("RolePermission",back_populates="role",cascade="all, delete-orphan")
    users = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan"
    )

