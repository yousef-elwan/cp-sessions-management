from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.DB.session import get_db
from app.Services.Role_Permission_Service import RolePermissionService

Role_Permission_router = APIRouter(prefix="/role-permissions", tags=["RolePermissions"])

@Role_Permission_router.post("/")
async def create_role_permission(role_id: UUID, permission_id: UUID, db: AsyncSession = Depends(get_db)):
    return await RolePermissionService.create(role_id, permission_id, db)

@Role_Permission_router.get("/")
async def get_role_permissions(db: AsyncSession = Depends(get_db)):
    return await RolePermissionService.get_all(db)

@Role_Permission_router.patch("/toggle/{rp_id}")
async def toggle_role_permission(rp_id: UUID, db: AsyncSession = Depends(get_db)):
    rp = await RolePermissionService.toggle_active(rp_id, db)
    if not rp:
        raise HTTPException(status_code=404, detail="RolePermission not found")
    return rp

@Role_Permission_router.delete("/{rp_id}")
async def delete_role_permission(rp_id: UUID, db: AsyncSession = Depends(get_db)):
    success = await RolePermissionService.delete(rp_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="RolePermission not found")
    return {"detail": "Deleted"}
