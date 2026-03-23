from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import UserModel


async def require_admin(session: AsyncSession, auth: AuthSchema) -> None:
    result = await session.execute(
        select(UserModel.role).where(UserModel.id == auth.id)
    )
    role = result.scalar_one_or_none()
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
