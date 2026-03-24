from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.application.schemas.profile import ProfileResponse, ProfileUpdateRequest
from src.usecase.profile.get import GetProfileUsecase
from src.usecase.profile.update import UpdateProfileUsecase
from src.infra.auth.admin import get_user_role
from src.infra.auth.jwt import verify_password, hash_password
from src.infra.postgres.tables import UserModel

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.get("", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def get_profile(
    auth: FromDishka[AuthSchema],
    usecase: FromDishka[GetProfileUsecase],
) -> ProfileResponse:
    return await usecase(user_id=auth.id)


@ROUTER.put("", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def update_profile(
    auth: FromDishka[AuthSchema],
    usecase: FromDishka[UpdateProfileUsecase],
    body: ProfileUpdateRequest,
) -> ProfileResponse:
    return await usecase(user_id=auth.id, data=body)


@ROUTER.get("/role")
async def get_my_role(
    auth: FromDishka[AuthSchema],
    session: FromDishka[AsyncSession],
):
    role = await get_user_role(session, auth)
    return {"role": role}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@ROUTER.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    auth: FromDishka[AuthSchema],
    session: FromDishka[AsyncSession],
):
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Новый пароль должен быть не менее 8 символов")

    result = await session.execute(
        select(UserModel).where(UserModel.id == auth.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.password_hash or not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    user.password_hash = hash_password(body.new_password)
    await session.commit()

    return {"detail": "Пароль успешно изменён"}
