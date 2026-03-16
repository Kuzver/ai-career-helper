from dishka import Provider, provide, Scope
from fastapi import Request
from loguru import logger

from src.application.schemas.auth import AuthSchema
from src.config import JwtConfig
from src.infra.auth.jwt import verify_token


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_auth(self, request: Request, jwt_config: JwtConfig) -> AuthSchema:
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                data = verify_token(token, jwt_config.secret)
                return AuthSchema(id=data["sub"], email=data.get("email", ""))
            except ValueError as e:
                logger.warning(f"Invalid JWT: {e}")

        # Fallback for unauthenticated requests (chat creation will still need user)
        return AuthSchema(id="21dc573d-663b-419e-a1b6-c48e02b97c67", email="anonymous@local")
