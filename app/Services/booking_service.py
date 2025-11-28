from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.booking import Booking
from app.Models.session import TrainingSession
from uuid import UUID
from typing import List, Optional

class BookingService:
    @staticmethod
    async def create_booking(db: AsyncSession, session_id: UUID, student_id: UUID) -> Booking:
        db_booking = Booking(
            session_id=session_id,
            student_id=student_id
        )
        db.add(db_booking)
        
        # Increment current_attendees in session
        result = await db.execute(select(TrainingSession).where(TrainingSession.id == session_id))
        session = result.scalars().first()
        if session:
            session.current_attendees += 1
            db.add(session)
            
        await db.commit()
        await db.refresh(db_booking)
        return db_booking

    @staticmethod
    async def get_bookings_by_student(db: AsyncSession, student_id: UUID) -> List[Booking]:
        result = await db.execute(select(Booking).where(Booking.student_id == student_id))
        return result.scalars().all()

    @staticmethod
    async def get_bookings_by_session(db: AsyncSession, session_id: UUID) -> List[Booking]:
        result = await db.execute(select(Booking).where(Booking.session_id == session_id))
        return result.scalars().all()

    @staticmethod
    async def delete_booking(db: AsyncSession, booking_id: UUID) -> bool:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        db_booking = result.scalars().first()
        if not db_booking:
            return False
        
        # Decrement current_attendees in session
        session_result = await db.execute(select(TrainingSession).where(TrainingSession.id == db_booking.session_id))
        session = session_result.scalars().first()
        if session and session.current_attendees > 0:
            session.current_attendees -= 1
            db.add(session)

        await db.delete(db_booking)
        await db.commit()
        return True
