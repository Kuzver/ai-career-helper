from dishka import Provider, Scope, provide, FromDishka
from fastapi import HTTPException, Request
from src.infra.auth.token import TokenParser
from src.application.schemas.auth import AuthSchema
from loguru import logger


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_token_processor(self) -> TokenParser:
        return TokenParser()

    @provide(provides=AuthSchema)
    async def get_token_data(
            self,
            processor: FromDishka[TokenParser],
            request: FromDishka[Request],
    ) -> AuthSchema:
        logger.info("provider")
        auth_header = request.headers.get("Authorization")
        try:
            return await processor(auth_header)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))