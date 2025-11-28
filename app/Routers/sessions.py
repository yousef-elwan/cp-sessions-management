from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.DB.session import get_db
from app.Schemas.session_schema import SessionCreate, SessionUpdate, SessionResponse
from app.Schemas.booking_schema import BookingResponse
from app.Services.session_service import SessionService
from app.Services.booking_service import BookingService
from app.Services.auth_dependency import get_current_user
from app.Models.user import User

sessions_router = APIRouter(prefix="/sessions", tags=["Sessions"])

@sessions_router.post("/", response_model=SessionResponse)
async def create_session(
    session_in: SessionCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Only trainers can create sessions")
    return await SessionService.create_session(db, session_in, current_user.id)

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
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Only trainers can update sessions")
    
    session = await SessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this session")

    updated_session = await SessionService.update_session(db, session_id, session_in)
    return updated_session

@sessions_router.delete("/{session_id}")
async def delete_session(
    session_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Only trainers can delete sessions")
    
    session = await SessionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.trainer_id != current_user.id:
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
