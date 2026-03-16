'''from sqlalchemy.ext.asyncio import AsyncSession
from src.usecase.base import Usecase
from uuid import UUID
from src.application.schemas.auth import AuthSchema
from src.infra.postgres.gateways.base import GetAllByIdUserGate
from src.application.schemas.common import RequestPaginationSchema, ResponsePaginationSchema
from src.application.schemas.chat import ChatSchemas
from src.usecase.systems.pagination import Pagination
from src.infra.postgres.tables import ChatModel
from dataclasses import dataclass
from src.usecase.users.create import CreateUserUsecase
from src.application.schemas.users import CreateUserSchema
from loguru import logger
from sqlalchemy import select, func
from src.application.schemas.chat import RawChat, RawPagination

@dataclass(slots=True, frozen=True, kw_only=True)
class GetAllChatUsecase(Usecase[RequestPaginationSchema, ResponsePaginationSchema]):
    def __init__(
        self,
        session: AsyncSession,
        auth: AuthSchema,
        get_chats: GetAllByIdUserGate[ChatModel, ChatSchemas, UUID],
        pagination: Pagination,
        create_user: CreateUserUsecase,
    ):
        self.session = session
        self.auth = auth
        self.get_chats = get_chats
        self.pagination = pagination
        self.create_user = create_user

    async def __call__(self, data: RequestPaginationSchema) -> ResponsePaginationSchema:
        async with self.session.begin():
            await self.create_user(CreateUserSchema(id=self.auth.id))
            logger.info(1)
            chats = await self.get_chats(self.auth.id)
            logger.info(1)
            return self.pagination(chats, data.limit, data.offset, schema_class=ChatSchemas)'''

'''from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from src.application.schemas.common import RequestPaginationSchema, ResponsePaginationSchema
from src.application.schemas.chat import ChatSchemas
from src.infra.postgres.gateways.base import GetAllByIdUserGate
from src.usecase.systems.pagination import Pagination
from src.infra.postgres.tables import ChatModel
from src.usecase.users.create import CreateUserUsecase
from src.application.schemas.users import CreateUserSchema

class GetAllChatUsecase:
    def __init__(
        self,
        session: AsyncSession,
        get_chats: GetAllByIdUserGate[ChatModel, ChatSchemas, UUID],
        pagination: Pagination,
        create_user: CreateUserUsecase,
    ):
        self.session = session
        self.get_chats = get_chats
        self.pagination = pagination
        self.create_user = create_user

    async def __call__(self, data: RequestPaginationSchema) -> ResponsePaginationSchema:
        async with self.session.begin():
            # Фиксированный ID пользователя из фронтенда
            user_id = UUID("21dc573d-663b-419e-a1b6-c48e02b97c67")
            await self.create_user(CreateUserSchema(id=user_id))
            logger.info(1)
            chats = await self.get_chats(user_id)
            logger.info(1)
            return self.pagination(chats, data.limit, data.offset, schema_class=ChatSchemas)'''
from src.application.schemas.chat import RawPagination

class GetAllChatUsecase:
    def __init__(self):
        pass

    async def __call__(self, limit: int = 50, offset: int = 0) -> RawPagination:
        return RawPagination(
            items=[],
            lenItems=0,
            leftLimit=None,
            leftOffset=None,
            rightLimit=None,
            rightOffset=None
        )