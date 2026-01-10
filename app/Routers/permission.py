from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.DB.session import get_db
from app.Services.permission_service import PermissionService
from app.Schemas.permission import (
    PermissionCreate,
    PermissionOut,
    PermissionUpdate
)

permission_router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@permission_router.post("/", response_model=PermissionOut)
async def create_permission(
    data: PermissionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await PermissionService.create_permission(data, db)


@permission_router.get("/", response_model=List[PermissionOut])
async def list_permissions(
    db: AsyncSession = Depends(get_db)
):
    return await PermissionService.get_all_permissions(db)


@permission_router.patch("/{permission_id}", response_model=PermissionOut)
async def update_permission(
    permission_id: str,
    data: PermissionUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await PermissionService.update_permission(permission_id, data, db)
