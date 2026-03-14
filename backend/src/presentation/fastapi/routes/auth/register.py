from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from src.application.schemas.users import CreateUserSchema
from src.usecase.users.create import CreateUserUsecase

ROUTER = APIRouter(route_class=DishkaRoute)

@ROUTER.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(usecase: FromDishka[CreateUserUsecase], user: CreateUserSchema) -> None:
    """Registration callback: creates a user if not exists."""
    await usecase(user)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created"})
