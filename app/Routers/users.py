from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.DB.session import get_db
from app.Schemas.user_schema import UserResponse
from app.Services.user_service import UserService
from app.Services.auth_dependency import get_current_user
from app.Models.user import User

users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await UserService.get_all_users(db, skip, limit)

@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
