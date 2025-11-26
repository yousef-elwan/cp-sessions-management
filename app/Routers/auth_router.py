from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.DB.session import get_db
from app.Models.user import User
from app.Schemas.auth import UserCreate, UserLogin, Token, UserInDB
from app.Services.auth_service import (
    register_user_service,
    login_user_service,
    get_user_by_id_service
)
from app.Services.auth_dependency import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserInDB)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user_service(user_data, db)

@auth_router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user_service(user_data, db)

@auth_router.get("/get/{user_id}", response_model=UserInDB)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await get_user_by_id_service(user_id, db)

@auth_router.get("/me", response_model=UserInDB)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
