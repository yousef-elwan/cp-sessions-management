"""Topic Prerequisites Router

Endpoints for managing topic prerequisite relationships.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.DB.session import get_db
from app.Models.prerequisite import TopicPrerequisite
from app.Models.topic import Topic
from app.Services.auth_dependency import get_current_active_admin
from app.Models.user import User


router = APIRouter(prefix="/topic-prerequisites", tags=["Topic Prerequisites"])


from app.Schemas.topic_prerequisite_schema import TopicPrerequisiteCreate

@router.post("/", status_code=200)
async def add_prerequisite(
    prerequisite_data: TopicPrerequisiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Add a prerequisite relationship between topics.
    Only admins can manage prerequisites.
    """
    topic_id = prerequisite_data.topic_id
    prerequisite_topic_id = prerequisite_data.prerequisite_topic_id

    # Validate that both topics exist
    topic_result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = topic_result.scalars().first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    prereq_result = await db.execute(select(Topic).where(Topic.id == prerequisite_topic_id))
    prereq = prereq_result.scalars().first()
    if not prereq:
        raise HTTPException(status_code=404, detail="Prerequisite topic not found")
    
    # Check for self-reference
    if topic_id == prerequisite_topic_id:
        raise HTTPException(status_code=400, detail="A topic cannot be its own prerequisite")
    
    # Check for circular dependency
    if await has_circular_dependency(db, topic_id, prerequisite_topic_id):
        raise HTTPException(status_code=400, detail="Circular dependency detected")
    
    # Check if relationship already exists
    existing = await db.execute(
        select(TopicPrerequisite).where(
            TopicPrerequisite.topic_id == topic_id,
            TopicPrerequisite.prerequisite_id == prerequisite_topic_id
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Prerequisite relationship already exists")
    
    # Create the prerequisite relationship
    prerequisite = TopicPrerequisite(
        topic_id=topic_id,
        prerequisite_id=prerequisite_topic_id
    )
    db.add(prerequisite)
    await db.commit()
    
    return {"message": "Prerequisite added successfully"}


@router.delete("/")
async def remove_prerequisite(
    topic_id: UUID,
    prerequisite_topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Remove a prerequisite relationship."""
    result = await db.execute(
        select(TopicPrerequisite).where(
            TopicPrerequisite.topic_id == topic_id,
            TopicPrerequisite.prerequisite_id == prerequisite_topic_id
        )
    )
    prerequisite = result.scalars().first()
    
    if not prerequisite:
        raise HTTPException(status_code=404, detail="Prerequisite relationship not found")
    
    await db.delete(prerequisite)
    await db.commit()
    
    return {"message": "Prerequisite removed successfully"}


@router.get("/{topic_id}")
async def get_topic_prerequisites(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all prerequisites for a topic."""
    result = await db.execute(
        select(Topic).join(
            TopicPrerequisite,
            TopicPrerequisite.prerequisite_id == Topic.id
        ).where(TopicPrerequisite.topic_id == topic_id)
    )
    prerequisites = result.scalars().all()
    
    return [{"id": str(p.id), "name": p.name} for p in prerequisites]


async def has_circular_dependency(db: AsyncSession, topic_id: UUID, new_prerequisite_id: UUID) -> bool:
    """
    Check if adding new_prerequisite_id as a prerequisite of topic_id 
    would create a circular dependency.
    
    Algorithm: Do a depth-first search starting from new_prerequisite_id.
    If we can reach topic_id, then adding this relationship would create a cycle.
    """
    async def dfs(current_id: UUID, visited: set) -> bool:
        if current_id in visited:
            return False
        
        if current_id == topic_id:
            return True  # Found a path back to the original topic
        
        visited.add(current_id)
        
        # Get all prerequisites of current_id (topics that current_id depends on)
        result = await db.execute(
            select(TopicPrerequisite.prerequisite_id).where(
                TopicPrerequisite.topic_id == current_id
            )
        )
        dependent_topics = result.scalars().all()
        
        for dependent_id in dependent_topics:
            if await dfs(dependent_id, visited):
                return True
        
        return False
    
    return await dfs(new_prerequisite_id, set())
