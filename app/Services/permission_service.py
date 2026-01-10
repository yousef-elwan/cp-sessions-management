from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.Models.permission import Permission
from app.Schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:

    @staticmethod
    async def create_permission(
        data: PermissionCreate,
        db: AsyncSession
    ):
        result = await db.execute(
            select(Permission).where(Permission.name == data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )

        permission = Permission(
            name=data.name,
            description=data.description
        )

        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def get_all_permissions(db: AsyncSession):
        result = await db.execute(select(Permission))
        return result.scalars().all()

    @staticmethod
    async def update_permission(
        permission_id,
        data: PermissionUpdate,
        db: AsyncSession
    ):
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        if data.description is not None:
            permission.description = data.description

        if data.is_active is not None:
            permission.is_active = data.is_active

        await db.commit()
        await db.refresh(permission)
        return permission
