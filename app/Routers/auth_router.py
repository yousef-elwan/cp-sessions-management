"""Authentication Router

This module defines authentication-related API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.DB.session import get_db
from app.Models.user import User
from app.Schemas.auth import Token
from app.Schemas.user_schema import UserCreate, UserLogin, UserResponse, UserRegister
from app.Services.auth_service import AuthService
from app.Services.auth_dependency import (
    get_current_user,
    get_current_active_admin,
    get_current_super_admin
)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user account (Student only)."""
    return await AuthService.register_user(user_data, db, forced_role="student")


@auth_router.post(
    "/create-trainer",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trainer",
    description="Create a new trainer account (Admin only)"
)
async def create_trainer(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
) -> UserResponse:
    """Create a new trainer account."""
    return await AuthService.register_user(user_data, db, forced_role="trainer")


@auth_router.post(
    "/create-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new admin",
    description="Create a new admin account (Super Admin only)"
)
async def create_admin(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
) -> UserResponse:
    """Create a new admin account."""
    return await AuthService.register_user(user_data, db, forced_role="admin")


@auth_router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and receive JWT access token"
)
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Login and receive access token."""
    return await AuthService.login_user(user_data, db)


@auth_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get currently authenticated user profile"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current authenticated user."""
    return current_user
