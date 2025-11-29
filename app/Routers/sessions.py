from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.DB.session import get_db
from app.Schemas.session_schema import SessionCreate, SessionUpdate, SessionResponse
from app.Schemas.booking_schema import BookingResponse
from app.Services.session_service import SessionService
from app.Services.booking_service import BookingService
from app.Services.auth_dependency import get_current_user, get_current_trainer_or_admin
from app.Models.user import User

sessions_router = APIRouter(prefix="/sessions", tags=["Sessions"])

@sessions_router.post("/", response_model=SessionResponse)
async def create_session(
    session_in: SessionCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    trainer_id = current_user.id
    
    # If Admin, check if they provided a trainer_id
    if current_user.role in ["admin", "super_admin"]:
        if session_in.trainer_id:
            trainer_id = session_in.trainer_id
        # If admin doesn't provide trainer_id, they become the trainer (if that's desired behavior)
        # Or we could enforce it. Let's assume Admin assigns, so if not provided, maybe error?
        # But for now let's default to current_user if not provided, allowing Admin to be trainer.
    
    return await SessionService.create_session(db, session_in, trainer_id)

@sessions_router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    return await SessionService.get_all_sessions(db, skip, limit)

@sessions_router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID, 
    db: AsyncSession = Depends(get_db)
):
    session = await SessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@sessions_router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID, 
    session_in: SessionUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    # Permission check handled by dependency, but we need to check ownership if not admin
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Allow Admin to update any session, Trainer only their own
    if current_user.role not in ["admin", "super_admin"] and session.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this session")

    updated_session = await SessionService.update_session(db, session_id, session_in)
    return updated_session

@sessions_router.delete("/{session_id}")
async def delete_session(
    session_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    # Permission check handled by dependency
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Allow Admin to delete any session, Trainer only their own
    if current_user.role not in ["admin", "super_admin"] and session.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this session")

    await SessionService.delete_session(db, session_id)
    return {"message": "Session deleted successfully"}

@sessions_router.post("/{session_id}/book", response_model=BookingResponse)
async def book_session(
    session_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check prerequisites logic could be added here
    
    # Check if session exists
    session = await SessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check capacity
    if session.capacity <= session.current_attendees:
        raise HTTPException(status_code=400, detail="Session is full")

    # Check if already booked
    existing_bookings = await BookingService.get_bookings_by_student(db, current_user.id)
    for booking in existing_bookings:
        if booking.session_id == session_id:
             raise HTTPException(status_code=400, detail="Already booked")

    return await BookingService.create_booking(db, session_id, current_user.id)

@sessions_router.get("/{session_id}/bookings", response_model=List[BookingResponse])
async def get_session_bookings(
    session_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Allow trainer or admin? Or maybe student too?
    # Assuming trainer of the session or admin
    session = await SessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if current_user.role != "admin" and (current_user.role != "trainer" or session.trainer_id != current_user.id):
         raise HTTPException(status_code=403, detail="Not authorized")

    return await BookingService.get_bookings_by_session(db, session_id)
