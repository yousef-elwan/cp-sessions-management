import asyncio
import logging
from sqlalchemy import text
from app.DB.session import AsyncSessionLocal
from app.Models.session import TrainingSession
from app.Schemas.session_schema import SessionCreate
from app.Services.session_service import SessionService
import uuid
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_db():
    async with AsyncSessionLocal() as db:
        try:
            # 1. Check if tables exist
            logger.info("Checking tables...")
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Tables found: {tables}")
            
            if "sessions" not in tables:
                logger.error("CRITICAL: 'sessions' table NOT found!")
            else:
                logger.info("'sessions' table exists.")

            # 2. Check Enum
            logger.info("Checking enums...")
            # This query is specific to PostgreSQL
            result = await db.execute(text("SELECT typname FROM pg_type WHERE typname = 'session_status'"))
            enum_exists = result.scalar_one_or_none()
            if not enum_exists:
                logger.error("CRITICAL: 'session_status' enum NOT found!")
            else:
                logger.info("'session_status' enum exists.")

            # 3. Try to create a session directly
            logger.info("Attempting to create a dummy session...")
            try:
                # We need a user and topic first. Let's just pick the first ones we find.
                from app.Models.user import User
                from app.Models.topic import Topic
                from sqlalchemy import select
                
                user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
                topic = (await db.execute(select(Topic).limit(1))).scalar_one_or_none()
                
                if not user or not topic:
                    logger.warning("Cannot test session creation: No user or topic found.")
                    return

                session_in = SessionCreate(
                    title="Debug Session",
                    start_time=datetime.now(datetime.UTC) + timedelta(days=1),
                    topic_id=topic.id,
                    trainer_id=user.id
                )
                
                await SessionService.create_session(db, session_in, user.id)
                logger.info("Session created successfully via Service!")
                
            except Exception as e:
                logger.error(f"Failed to create session via Service: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            logger.error(f"General DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_db())
