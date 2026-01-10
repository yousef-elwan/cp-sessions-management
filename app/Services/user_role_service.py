from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.user_role import UserRole
from app.Schemas.user_role import UserRoleCreate



async def assign_role_to_user(
    db: AsyncSession,
    data: UserRoleCreate
):
    stmt = select(UserRole).where(
        UserRole.user_id == data.user_id,
        UserRole.role_id == data.role_id
    )

    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if user_role:
        if not user_role.is_active:
            user_role.is_active = True
            await db.commit()
            return user_role
        raise ValueError("Role already assigned to user")

    new_user_role = UserRole(
        user_id=data.user_id,
        role_id=data.role_id
    )

    db.add(new_user_role)
    await db.commit()
    await db.refresh(new_user_role)
    return new_user_role

async def remove_role_from_user(
    db: AsyncSession,
    user_id,
    role_id
):
    stmt = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.is_active == True
    )

    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise ValueError("User role not found")

    user_role.is_active = False
    await db.commit()
    return user_role



async def get_user_roles(db: AsyncSession, user_id):
    stmt = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalars().all()
