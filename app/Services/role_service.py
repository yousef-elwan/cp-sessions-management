from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID

from app.Models.role import AppRole
from app.Schemas.role import RoleCreate, RoleUpdate

async def create_role(
    db: AsyncSession,
    role_in: RoleCreate,
) -> AppRole:
    result = await db.execute(
        select(AppRole).where(AppRole.name == role_in.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Role with this name already exists"
        )

    role = AppRole(
        name=role_in.name,
        description=role_in.description
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role




async def get_roles(db: AsyncSession) -> list[AppRole]:
    result = await db.execute(
        select(AppRole).where(AppRole.is_active == True)
    )
    return result.scalars().all()


async def get_role_by_id(
    db: AsyncSession,
    role_id: UUID
) -> AppRole:
    result = await db.execute(
        select(AppRole).where(AppRole.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )
    return role



async def update_role(
    db: AsyncSession,
    role_id: UUID,
    role_in: RoleUpdate
) -> AppRole:
    role = await get_role_by_id(db, role_id)

    for field, value in role_in.model_dump(exclude_unset=True).items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)
    return role



async def delete_role(
    db: AsyncSession,
    role_id: UUID
) -> None:
    role = await get_role_by_id(db, role_id)

    role.is_active = False
    await db.commit()
