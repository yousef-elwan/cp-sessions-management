from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.DB.session import get_db
from app.Schemas.user_role import UserRoleCreate, UserRoleResponse
from app.Services.user_role_service import (
    assign_role_to_user,
    remove_role_from_user,
    get_user_roles
)

user_roles_router = APIRouter(prefix="/user-roles", tags=["User Roles"])

@user_roles_router.post("/", response_model=UserRoleResponse)
async def assign_role(
    data: UserRoleCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await assign_role_to_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_roles_router.delete("/")
async def remove_role(
    user_id,
    role_id,
    db: AsyncSession = Depends(get_db)
):
    try:
        await remove_role_from_user(db, user_id, role_id)
        return {"message": "Role removed from user"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_roles_router.get("/{user_id}", response_model=list[UserRoleResponse])
async def list_user_roles(
    user_id,
    db: AsyncSession = Depends(get_db)
):
    return await get_user_roles(db, user_id)

