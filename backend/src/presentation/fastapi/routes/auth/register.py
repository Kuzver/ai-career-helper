from uuid import uuid4
from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from src.infra.auth.jwt import hash_password, verify_password, create_token
from src.infra.postgres.tables import UserModel
from src.config import JwtConfig

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register_user(
    body: RegisterRequest,
    session: FromDishka[AsyncSession],
    jwt_config: FromDishka[JwtConfig],
):
    result = await session.execute(
        select(UserModel).where(UserModel.email == body.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        is_active=True,
    )
    session.add(user)
    await session.commit()

    token = create_token(user_id, body.email, jwt_config.secret, jwt_config.expire_days)
    return TokenResponse(token=token, user_id=str(user_id), email=body.email)


@ROUTER.post("/login", response_model=TokenResponse)
async def login_user(
    body: LoginRequest,
    session: FromDishka[AsyncSession],
    jwt_config: FromDishka[JwtConfig],
):
    result = await session.execute(
        select(UserModel).where(UserModel.email == body.email)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    token = create_token(user.id, user.email, jwt_config.secret, jwt_config.expire_days)
    return TokenResponse(token=token, user_id=str(user.id), email=user.email)
