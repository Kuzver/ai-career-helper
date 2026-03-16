from dishka import Provider, provide, Scope
from src.application.schemas.auth import AuthSchema


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_auth(self) -> AuthSchema:
        # TODO: restore JWT validation via TokenParser when auth is ready
        return AuthSchema(id="21dc573d-663b-419e-a1b6-c48e02b97c67")