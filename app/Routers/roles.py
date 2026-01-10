from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.DB.session import get_db
from app.Models.role import AppRole
from app.Schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse
)
from app.Services import role_service



role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@role_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await role_service.create_role(db, role_in)


@role_router.get("/", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
):
    return await role_service.get_roles(db)


@role_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await role_service.get_role_by_id(db, role_id)

@role_router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await role_service.update_role(db, role_id, role_in)

@role_router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    await role_service.delete_role(db, role_id)
    return {"message": "Role deleted successfully"}

