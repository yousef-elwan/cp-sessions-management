from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.Models.booking import Booking
from app.Models.session import TrainingSession
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from app.Models.student_topic import Studenttopic
from app.Models.topic import Topic
from app.Models.prerequisite import TopicPrerequisite
from datetime import datetime, timezone

class BookingService:
    @staticmethod
    async def create_booking(db: AsyncSession, session_id: UUID, student_id: UUID) -> Booking:
        # Check prerequisites
        await BookingService.check_prerequisites(db, session_id, student_id)
        
        # Get session with SELECT FOR UPDATE lock to prevent race conditions
        # This ensures only one transaction can modify the session at a time
        result = await db.execute(
            select(TrainingSession)
            .where(TrainingSession.id == session_id)
            .with_for_update()  # Database-level lock
        )
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session is full
        if session.current_attendees >= session.capacity:
            raise HTTPException(status_code=400, detail="Session is full")
        
        # Check session status
        if session.status not in ["active", "upcoming"]:
            raise HTTPException(status_code=400, detail=f"Cannot book {session.status} session")
        
        # Check if session is in the past (use naive datetime for comparison)
        if session.start_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Cannot book past sessions")
        
        # Check if already booked
        existing = await db.execute(
            select(Booking).where(
                Booking.session_id == session_id,
                Booking.student_id == student_id
            )
        )
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Already booked this session")
        
        # Create booking
        db_booking = Booking(
            session_id=session_id,
            student_id=student_id
        )
        db.add(db_booking)
        
        # Increment current_attendees (session already fetched above with lock)
        session.current_attendees += 1
        db.add(session)
        
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            # Handle unique constraint violation (double booking)
            if "uc_session_student" in str(e) or "duplicate key" in str(e).lower():
                raise HTTPException(status_code=400, detail="Already booked this session")
            # Re-raise other exceptions
            raise
            
        await db.refresh(db_booking)
        
        # Eagerly load relationships including nested ones
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.session).selectinload(TrainingSession.trainer),
                selectinload(Booking.session).selectinload(TrainingSession.topic)
            )
            .where(Booking.id == db_booking.id)
        )
        db_booking = result.scalar_one()
        
        return db_booking

    @staticmethod
    async def get_bookings_by_student(db: AsyncSession, student_id: UUID) -> List[Booking]:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.session).selectinload(TrainingSession.trainer),
                selectinload(Booking.session).selectinload(TrainingSession.topic)
            )
            .where(Booking.student_id == student_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_bookings_by_session(db: AsyncSession, session_id: UUID) -> List[Booking]:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.session).selectinload(TrainingSession.trainer),
                selectinload(Booking.session).selectinload(TrainingSession.topic)
            )
            .where(Booking.session_id == session_id)
        )
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

    @staticmethod
    async def get_booking_by_id(db: AsyncSession, booking_id: UUID) -> Optional[Booking]:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalars().first()

    @staticmethod
    async def mark_attendance(db: AsyncSession, booking_id: UUID, attended: bool) -> Optional[Booking]:
        booking = await BookingService.get_booking_by_id(db, booking_id)
        if not booking:
            return None
        
        booking.attended = attended
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def add_feedback(db: AsyncSession, booking_id: UUID, feedback: str, rating: int) -> Optional[Booking]:
        booking = await BookingService.get_booking_by_id(db, booking_id)
        if not booking:
            return None
        
        booking.feedback = feedback
        booking.rating = rating
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def check_prerequisites(db: AsyncSession, session_id: UUID, student_id: UUID):
        """Check if student meets prerequisites for the session's topic."""
        # Get session topic
        result = await db.execute(select(TrainingSession).where(TrainingSession.id == session_id))
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get topic prerequisites
        # We need to load prerequisites relationship or query it
        # Assuming Topic model has 'prerequisites' relationship loaded or we query it
        # Let's query TopicPrerequisite directly or join
        
        # Fetch topic with prerequisites
        stmt = select(Topic).where(Topic.id == session.topic_id)
        # We might need to use selectinload if lazy loading is issue, but let's try direct access if loaded
        # Or better, query TopicPrerequisite
        
        # Find all prerequisite topic IDs for this topic
        prereq_result = await db.execute(
            select(TopicPrerequisite.prerequisite_id)
            .where(TopicPrerequisite.topic_id == session.topic_id)
        )
        prereq_ids = prereq_result.scalars().all()
        
        if not prereq_ids:
            return
            
        # Check which of these the student has completed
        completed_result = await db.execute(
            select(Studenttopic.topic_id)
            .where(
                Studenttopic.student_id == student_id,
                Studenttopic.topic_id.in_(prereq_ids)
            )
        )
        completed_ids = completed_result.scalars().all()
        
        # Compare
        missing_prereqs = set(prereq_ids) - set(completed_ids)
        
        if missing_prereqs:
            # Get names of missing topics for better error message
            missing_topics_result = await db.execute(select(Topic.name).where(Topic.id.in_(missing_prereqs)))
            missing_names = missing_topics_result.scalars().all()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prerequisites not met. Missing topics: {', '.join(missing_names)}"
            )
