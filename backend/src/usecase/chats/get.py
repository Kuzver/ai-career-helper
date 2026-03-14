from sqlalchemy.ext.asyncio import AsyncSession
from src.usecase.base import Usecase
from src.application.schemas.auth import AuthSchema
from src.infra.postgres.gateways.chats import GetChatGate
from src.application.schemas.common import RequestPaginationByIDSchema, ResponsePaginationSchema
from src.application.schemas.messages import MessageSchemas
from src.usecase.systems.pagination import Pagination
from dataclasses import dataclass
from loguru import logger


@dataclass(slots=True, frozen=True, kw_only=True)
class GetChatUsecase(Usecase[RequestPaginationByIDSchema, ResponsePaginationSchema]):
    session: AsyncSession
    auth: AuthSchema
    get_chat: GetChatGate
    pagination: Pagination

    async def __call__(self, data: RequestPaginationByIDSchema) -> ResponsePaginationSchema:
        async with self.session.begin():
            chat =  await self.get_chat(data.id)
            pagination =  self.pagination(chat.messages, data.limit, data.offset, schema_class=MessageSchemas)
            chat.messages = pagination.items
            pagination.items = chat
            return pagination


