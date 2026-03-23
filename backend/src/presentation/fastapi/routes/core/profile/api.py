from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.application.schemas.profile import ProfileResponse, ProfileUpdateRequest
from src.usecase.profile.get import GetProfileUsecase
from src.usecase.profile.update import UpdateProfileUsecase
from src.infra.auth.admin import get_user_role

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
