"""Authentication Service

This module provides authentication and user management services.
"""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Dict, Any, Union

from fastapi import HTTPException, status
from app.Models.user import User
from app.Models.user_role import UserRole
from app.Schemas.user_schema import UserCreate, UserLogin, UserRegister
from app.core.hash import get_password_hash, verify_password
from app.core.jwt import create_access_token
from app.core.config import settings
from app.Services.role_service import get_role_id_by_name

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    async def register_user(
        user_data: Union[UserCreate, UserRegister],
        db: AsyncSession
    ) -> User:
        """
        Register new user.
        🔒 Always creates a STUDENT user and assigns STUDENT role.
        """
        try:
            # 1️⃣ Check if email exists
            result = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # 2️⃣ Create user
            hashed_password = get_password_hash(user_data.password)

            db_user = User(
                name=user_data.name,
                email=user_data.email,
                password=hashed_password,
                is_active=True
            )

            db.add(db_user)
            await db.flush()  # يعطي db_user.id بدون commit

            # 3️⃣ Get STUDENT role id
            student_role_id = await get_role_id_by_name(db, "student")

            # 4️⃣ Create relation in user_roles
            user_role = UserRole(
                user_id=db_user.id,
                role_id=student_role_id,
                is_active=True
            )

            db.add(user_role)

            # 5️⃣ Commit all
            await db.commit()
            await db.refresh(db_user)

            logger.info(f"New student registered: {db_user.email}")
            return db_user

        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            logger.error("Error registering user", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while registering the user"
            )

    @staticmethod
    async def login_user(
        user_data: UserLogin,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Authenticate user and generate JWT."""
        try:
            result = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            user = result.scalar_one_or_none()

            if not user or not verify_password(user_data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )

            access_token = create_access_token(
                user_id=str(user.id),
                roles=["admin", "user", "trainer"],
                permissions=["add", "delete", "update"],
                expires_delta=timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            )

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }

        except HTTPException:
            raise
        except Exception:
            logger.error("Login error", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login"
            )

    @staticmethod
    async def get_user_by_id(
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> User:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
