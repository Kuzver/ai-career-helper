from src.usecase.base import Usecase
from uuid import UUID
from src.infra.postgres.gateways.base import CreateGate, GetByIdGate
from src.application.schemas.users import CreateUserSchema, UserSchemas
from src.infra.postgres.tables import UserModel
from dataclasses import dataclass
from src.infra.postgres.gateways.base import GetByEmailGate
from src.application.errors import DuplicateError, NotFoundError

@dataclass(slots=True, frozen=True, kw_only=True)
class CreateUserUsecase(Usecase[CreateUserSchema, None]):
    create_user: CreateGate[UserModel, CreateUserSchema]
    get_user: GetByIdGate[UserModel, UUID, UserSchemas]
    get_user_by_email: GetByEmailGate[UserModel, UserSchemas]
    
    async def __call__(self, data: CreateUserSchema) -> None:
        # Если пользователь с таким email уже существует то происходит конфликт
        existing = await self.get_user_by_email(data.email)
        if existing is not None:
            raise DuplicateError(message=f"Пользователь с email {data.email} уже существует")

        # Если пользователь существует, ничего не делаем; иначе создаем
        try:
            await self.get_user(data.id)
        except NotFoundError:
            await self.create_user(data)
