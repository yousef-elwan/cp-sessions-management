from sqlalchemy import Column, ForeignKey, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.DB.base import Base
from sqlalchemy.orm import relationship
class Trainertopic(Base):
        __tablename__ = "trainer_topics"

        trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
        topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
        created_at = Column(DateTime, default=func.now())
        trainer = relationship("User", back_populates="trainer_topics")
        topic = relationship("Topic", back_populates="trainer_topics")