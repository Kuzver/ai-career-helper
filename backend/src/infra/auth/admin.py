from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import UserModel


async def get_user_role(session: AsyncSession, auth: AuthSchema) -> str:
    result = await session.execute(
        select(UserModel.role).where(UserModel.id == auth.id)
    )
    return result.scalar_one_or_none() or "user"


async def require_admin(session: AsyncSession, auth: AuthSchema) -> None:
    role = await get_user_role(session, auth)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )


async def require_editor(session: AsyncSession, auth: AuthSchema) -> None:
    role = await get_user_role(session, auth)
    if role not in ("admin", "editor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права редактора или администратора",
        )
