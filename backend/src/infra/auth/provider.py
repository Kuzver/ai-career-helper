from dishka import Provider, provide, Scope
from fastapi import Request, HTTPException, status
from loguru import logger

from src.application.schemas.auth import AuthSchema
from src.config import JwtConfig
from src.infra.auth.jwt import verify_token


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_auth(self, request: Request, jwt_config: JwtConfig) -> AuthSchema:
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется авторизация",
            )

        token = auth_header[7:]
        try:
            data = verify_token(token, jwt_config.secret)
            return AuthSchema(id=data["sub"], email=data.get("email", ""))
        except ValueError as e:
            logger.warning(f"Invalid JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен",
            )
