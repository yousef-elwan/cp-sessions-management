import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import traceback
import sys

from app.DB.session import get_db
from app.Models.user import User
from app.Schemas.auth import UserCreate, UserLogin, Token, UserInDB
from app.Services.hash import get_password_hash, verify_password
from app.Services.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def log_db_error(e, detail):
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

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    try:
        result = await db.execute(
            select(User).filter(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
    except Exception as e:
        log_db_error(e, "Error occurred during user existence check.")

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
        log_db_error(e, "An unexpected database error occurred during registration commit.")

    return db_user

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(user_data: UserLogin, db: AsyncSession = Depends(get_db)):

    try:
        result = await db.execute(select(User).filter(User.email == user_data.email))
        user = result.scalar_one_or_none()
    except Exception as e:
        log_db_error(e, "Error occurred during user login retrieval.")

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/get/{user_id}", response_model=UserInDB)
async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return user
