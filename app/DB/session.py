"""Database Session Management

This module handles database connection and session management.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Echo SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_recycle=1800,    # Recycle connections after 30 minutes
    pool_size=5,          # Maintain 5 connections
    max_overflow=10,      # Allow up to 10 additional connections
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db():
    """Dependency that provides database session.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        >>> async def endpoint(db: AsyncSession = Depends(get_db)):
        >>>     result = await db.execute(select(User))
        >>>     return result.scalars().all()
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
