from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.role_permission import RolePermission

class RolePermissionService:

    @staticmethod
    async def create(role_id: int, permission_id: int, db: AsyncSession):
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(rp)
        await db.commit()
        await db.refresh(rp)
        return rp

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(RolePermission))
        return result.scalars().all()

    @staticmethod
    async def toggle_active(rp_id: int, db: AsyncSession):
        result = await db.execute(select(RolePermission).where(RolePermission.id == rp_id))
        rp = result.scalar_one_or_none()
        if not rp:
            return None
        rp.is_active = not rp.is_active
        db.add(rp)
        await db.commit()
        await db.refresh(rp)
        return rp

    @staticmethod
    async def delete(rp_id: int, db: AsyncSession):
        result = await db.execute(select(RolePermission).where(RolePermission.id == rp_id))
        rp = result.scalar_one_or_none()
        if not rp:
            return None
        await db.delete(rp)
        await db.commit()
        return True
