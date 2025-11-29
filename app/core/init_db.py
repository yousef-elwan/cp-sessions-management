"""Database Initialization Script

This module handles initial database seeding, particularly for the Super Admin user.
"""
import logging
import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.DB.session import AsyncSessionLocal
from app.Models.user import User
from app.core.config import settings
from app.core.hash import get_password_hash

# Configure logger
logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database with seed data."""
    async with AsyncSessionLocal() as db:
        try:
            # 1. Ensure 'super_admin' is in user_roles enum
            # This is a bit hacky for asyncpg, but necessary if we don't have full migrations
            try:
                await db.execute(text("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'super_admin'"))
                await db.commit()
            except Exception as e:
                # Ignore if it fails (likely already exists or not supported in transaction block)
                logger.warning(f"Could not alter enum type: {e}")
                await db.rollback()

            # 2. Check if Super Admin exists
            result = await db.execute(
                select(User).filter(User.role == "super_admin")
            )
            super_admin = result.scalar_one_or_none()

            if not super_admin:
                logger.info("Creating Super Admin user...")
                hashed_password = get_password_hash(settings.SUPER_ADMIN_PASSWORD)
                super_admin = User(
                    name="Super Admin",
                    email=settings.SUPER_ADMIN_EMAIL,
                    password=hashed_password,
                    role="super_admin",
                    is_active=True,
                    is_verified=True
                )
                db.add(super_admin)
                await db.commit()
                logger.info(f"Super Admin created: {settings.SUPER_ADMIN_EMAIL}")
            else:
                logger.info("Super Admin already exists.")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            await db.rollback()
            # Don't raise, just log, so app startup doesn't fail completely if DB is flaky
