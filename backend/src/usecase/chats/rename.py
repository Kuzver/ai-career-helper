from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import ChatModel


class RenameChatUsecase:
    def __init__(self, session: AsyncSession, auth: AuthSchema):
        self.session = session
        self.auth = auth

    async def __call__(self, chat_id: UUID, title: str) -> dict:
        result = await self.session.execute(
            select(ChatModel).where(
                ChatModel.id == chat_id,
                ChatModel.user_id == self.auth.id,
            )
        )
        chat = result.scalar_one_or_none()
        if not chat:
            raise ValueError("Чат не найден")

        chat.title = title
        await self.session.flush()

        response = {"id": str(chat.id), "title": chat.title}

        await self.session.commit()
        return response
