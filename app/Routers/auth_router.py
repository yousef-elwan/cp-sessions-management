"""Authentication Router

This module defines authentication-related API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.DB.session import get_db
from app.Models.user import User
from app.Schemas.auth import Token
from app.Schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.Services.auth_service import (
    register_user_service,
    login_user_service,
    get_user_by_id_service
)
from app.Services.auth_dependency import get_current_user

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
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user account."""
    return await register_user_service(user_data, db)


@auth_router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and receive JWT access token"
)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Login and receive access token."""
    return await login_user_service(user_data, db)


@auth_router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve user information by user ID"
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID."""
    return await get_user_by_id_service(user_id, db)


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
