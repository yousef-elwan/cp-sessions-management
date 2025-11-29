from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.DB.session import get_db
from app.Schemas.booking_schema import BookingCreate, BookingResponse, BookingFeedback, BookingAttendance
from app.Services.booking_service import BookingService
from app.Services.auth_dependency import get_current_user, get_current_trainer_or_admin
from app.Models.user import User

bookings_router = APIRouter(prefix="/bookings", tags=["Bookings"])

@bookings_router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_session(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Book a session (Student only)."""
    # Only students can book sessions
    if current_user.role not in ["student"]:
        raise HTTPException(status_code=403, detail="Only students can book sessions")
    
    return await BookingService.create_booking(db, booking_data.session_id, current_user.id)


@bookings_router.patch("/{booking_id}/attendance", response_model=BookingResponse)
async def mark_attendance(
    booking_id: UUID,
    attendance_data: BookingAttendance,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_trainer_or_admin)
):
    """Mark student attendance (Trainer/Admin only)."""
    booking = await BookingService.mark_attendance(db, booking_id, attendance_data.attended)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@bookings_router.patch("/{booking_id}/feedback", response_model=BookingResponse)
async def submit_feedback(
    booking_id: UUID,
    feedback_data: BookingFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for a booking (Student owner only)."""
    # Check ownership
    booking = await BookingService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to submit feedback for this booking")
    
    updated_booking = await BookingService.add_feedback(db, booking_id, feedback_data.feedback, feedback_data.rating)
    return updated_booking


@bookings_router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking (Student owner or Admin)."""
    # Check ownership
    booking = await BookingService.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if current_user.role not in ["admin", "super_admin"] and booking.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    
    success = await BookingService.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled successfully"}
