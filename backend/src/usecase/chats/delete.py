from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import ChatModel, MessageModel


class DeleteChatUsecase:
    def __init__(self, session: AsyncSession, auth: AuthSchema):
        self.session = session
        self.auth = auth

    async def __call__(self, chat_id: UUID) -> None:
        async with self.session.begin():
            result = await self.session.execute(
                select(ChatModel).where(
                    ChatModel.id == chat_id,
                    ChatModel.user_id == self.auth.id,
                )
            )
            chat = result.scalar_one_or_none()
            if not chat:
                raise ValueError("Чат не найден")

            await self.session.execute(
                delete(MessageModel).where(MessageModel.chat_id == chat_id)
            )
            await self.session.execute(
                delete(ChatModel).where(ChatModel.id == chat_id)
            )
