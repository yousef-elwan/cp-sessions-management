from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from uuid import UUID
from app.DB.session import get_db
from app.Models.topic import Topic
from app.Models.user import User
from app.Schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from app.Services.auth_dependency import get_current_active_admin


topic_router = APIRouter(prefix="/topics", tags=["Topics"])

@topic_router.post("/", response_model=TopicResponse)
async def create_topic(
    data: TopicCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    topic = Topic(**data.dict())
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic

@topic_router.get("/", response_model=list[TopicResponse])
async def get_topics(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Topic).where(Topic.deleted_at == None).offset(skip).limit(limit)
    )
    return result.scalars().all()

@topic_router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Topic).where(Topic.id == topic_id, Topic.deleted_at == None))
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return topic

@topic_router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: UUID, 
    data: TopicUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id, Topic.deleted_at == None))
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(topic, key, value)

    await db.commit()
    await db.refresh(topic)
    return topic

@topic_router.delete("/{topic_id}")
async def delete_topic(
    topic_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    result = await db.execute(select(Topic).where(Topic.id == topic_id, Topic.deleted_at == None))
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.deleted_at = func.now()
    await db.commit()
    return {"detail": "Topic deleted"}
