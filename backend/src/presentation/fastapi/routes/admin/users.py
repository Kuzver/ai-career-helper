from uuid import UUID
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.auth.admin import require_admin
from src.infra.postgres.tables import UserModel

ROUTER = APIRouter(route_class=DishkaRoute)

VALID_ROLES = {"user", "editor", "admin"}


class UserListItem(BaseModel):
    id: UUID
    email: str
    first_name: str | None
    role: str
    is_active: bool


class SetRoleRequest(BaseModel):
    role: str


@ROUTER.get("", response_model=list[UserListItem])
async def list_users(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_admin(session, auth)

    result = await session.execute(
        select(UserModel).order_by(UserModel.created_at.desc())
    )
    users = result.scalars().all()

    return [
        UserListItem(
            id=u.id, email=u.email, first_name=u.first_name,
            role=u.role, is_active=u.is_active,
        )
        for u in users
    ]


@ROUTER.patch("/{user_id}/role")
async def set_user_role(
    user_id: UUID,
    body: SetRoleRequest,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_admin(session, auth)

    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Допустимые роли: {', '.join(VALID_ROLES)}")

    if user_id == auth.id:
        raise HTTPException(status_code=400, detail="Нельзя менять свою роль")

    async with session.begin():
        result = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.role = body.role

    return {"id": str(user_id), "role": body.role}
