"""FastAPI Application Entry Point

This module initializes the FastAPI application with all configurations and routes.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import models to ensure they are registered with SQLAlchemy
from app.Models import (
    User, Topic, TopicPrerequisite, Trainertopic, Studenttopic,
    TrainingSession, Booking, Notification
)

# Import routers
from app.Routers.auth_router import auth_router
from app.Routers.topic import topic_router
from app.Routers.trainer_topic import trainer_topic_router
from app.Routers.topic_prerequisites import router as topic_prerequisites_router
from app.Routers.users import users_router
from app.Routers.sessions import sessions_router
from app.Routers.bookings import bookings_router
from app.Routers.student_subjects import student_subjects_router
from app.Routers.notifications import notifications_router
from app.core.init_db import init_db
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure SQLAlchemy logging (set to DEBUG in development)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

# Initialize FastAPI app
app = FastAPI(
    title="CP Sessions Management API",
    description="API for managing competitive programming training sessions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - Read from environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # Split comma-separated origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Include routers
app.include_router(auth_router)
app.include_router(topic_router)
app.include_router(trainer_topic_router)
app.include_router(topic_prerequisites_router)
app.include_router(users_router)
app.include_router(sessions_router)
app.include_router(bookings_router)
app.include_router(student_subjects_router)
app.include_router(notifications_router)


@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    await init_db()


@app.get("/", tags=["Health"])
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint for health check."""
    return {
        "status": "online",
        "message": "CP Sessions Management API is running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}