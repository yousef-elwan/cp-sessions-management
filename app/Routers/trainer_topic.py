from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.DB.session import get_db
from app.Schemas.trainer_topic import TrainerTopicCreate, TrainerTopicResponse
from app.Services.trainer_topic_service import TrainerTopicService
from app.Services.auth_dependency import get_current_active_admin
from app.Models.user import User

trainer_topic_router = APIRouter(prefix="/trainer-topics", tags=["Trainer Topics"])

@trainer_topic_router.post("/", response_model=TrainerTopicResponse)
async def assign_topic(
    data: TrainerTopicCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    result = await TrainerTopicService.assign_topic_to_trainer(
        db, data.trainer_id, data.topic_id
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Trainer already assigned to this topic")

    return result


@trainer_topic_router.get("/{trainer_id}", response_model=list[TrainerTopicResponse])
async def get_topics(trainer_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await TrainerTopicService.get_trainer_topics(db, trainer_id)
    return result
