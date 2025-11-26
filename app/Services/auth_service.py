import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import traceback
import sys

from fastapi import HTTPException, status
from app.Models.user import User
from app.Schemas.auth import UserCreate, UserLogin
from app.core.hash import get_password_hash, verify_password
from app.core.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


def log_db_error(e: Exception, detail: str):
    print("-------------------------------------------------------")
    print(f"🔥 خطأ قاعدة بيانات حرج تم اكتشافه: {detail}")
    print(f"رسالة الاستثناء: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    print("-------------------------------------------------------")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected database error occurred. Check the server console for details."
    )


async def register_user_service(user_data: UserCreate, db: AsyncSession):
    try:
        result = await db.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
    except Exception as e:
        log_db_error(e, "Error checking if user exists")

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role or "student"
    )
    db.add(db_user)

    try:
        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        await db.rollback()
        log_db_error(e, "Error committing new user to DB")

    return db_user


async def login_user_service(user_data: UserLogin, db: AsyncSession):
    try:
        result = await db.execute(select(User).filter(User.email == user_data.email))
        user = result.scalar_one_or_none()
    except Exception as e:
        log_db_error(e, "Error retrieving user for login")

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


async def get_user_by_id_service(user_id: uuid.UUID, db: AsyncSession):
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
    except Exception as e:
        log_db_error(e, f"Error retrieving user with id {user_id}")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user
