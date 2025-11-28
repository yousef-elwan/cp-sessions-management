"""
Models package - SQLAlchemy ORM models
Import order is important for relationships to work correctly
"""
from app.Models.user import User
from app.Models.topic import Topic
from app.Models.prerequisite import TopicPrerequisite
from app.Models.trainer_topic import Trainertopic
from app.Models.student_topic import Studenttopic
from app.Models.session import TrainingSession
from app.Models.booking import Booking
from app.Models.notification import Notification

__all__ = [
    "User",
    "Topic",
    "TopicPrerequisite",
    "Trainertopic",
    "Studenttopic",
    "TrainingSession",
    "Booking",
    "Notification",
]
