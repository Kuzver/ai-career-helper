from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter
from fastapi import status, HTTPException
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import UserCareersModel
from src.application.schemas.cards import GeneratedCardsResponse
from src.infra.gigachat.chat import Gigachat
from src.application.schemas.user_careers import CreateUserCareersSchema, UserCareersSchema
from src.usecase.user_careers.create import CreateUserCareerUsecase

ROUTER = APIRouter(route_class=DishkaRoute)

@ROUTER.post('', status_code=status.HTTP_200_OK)
async def create_users_career(
    usecase: FromDishka[CreateUserCareerUsecase],
    user: CreateUserCareersSchema) -> UserCareersSchema:
    return await usecase(user)