from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.DB.session import get_db
from app.Schemas.student_topic_schema import StudentTopicCreate, StudentTopicResponse
from app.Schemas.booking_schema import BookingResponse
from app.Services.student_topic_service import StudentTopicService
from app.Services.booking_service import BookingService
from app.Services.auth_dependency import get_current_user, get_current_trainer_or_admin
from app.Models.user import User

student_subjects_router = APIRouter(prefix="/students", tags=["Student Subjects"])

@student_subjects_router.post("/{student_id}/subjects", response_model=StudentTopicResponse)
async def add_completed_subject(
    student_id: UUID,
    topic_data: StudentTopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    # Only Trainer or Admin can add completed subjects
    # Dependency handles role check
    pass # Just to satisfy syntax if I removed the body, but I'm replacing the signature and check
        
    return await StudentTopicService.add_topic_to_student(db, student_id, topic_data.topic_id)

@student_subjects_router.get("/{student_id}/subjects", response_model=List[StudentTopicResponse])
async def get_student_subjects(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != student_id:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    return await StudentTopicService.get_student_topics(db, student_id)

@student_subjects_router.delete("/{student_id}/subjects/{topic_id}")
async def remove_completed_subject(
    student_id: UUID,
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    # Only Trainer or Admin can remove
    pass

    success = await StudentTopicService.remove_topic_from_student(db, student_id, topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found for student")
    return {"message": "Subject removed successfully"}

@student_subjects_router.get("/{student_id}/bookings", response_model=List[BookingResponse])
async def get_student_bookings(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != student_id:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    return await BookingService.get_bookings_by_student(db, student_id)
