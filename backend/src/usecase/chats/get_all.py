from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists
from src.infra.postgres.tables import ChatModel, MessageModel
from src.application.schemas.chat import RawChat, RawPagination
from src.application.schemas.auth import AuthSchema


class GetAllChatUsecase:
    def __init__(self, session: AsyncSession, auth: AuthSchema):
        self.session = session
        self.auth = auth

    async def __call__(self, limit: int = 50, offset: int = 0) -> RawPagination:
        has_messages = exists(
            select(MessageModel.id).where(MessageModel.chat_id == ChatModel.id)
        ).correlate(ChatModel)

        base_filter = [ChatModel.user_id == self.auth.id, has_messages]

        total = await self.session.scalar(
            select(func.count()).select_from(ChatModel).where(*base_filter)
        )

        result = await self.session.execute(
            select(ChatModel)
            .where(*base_filter)
            .order_by(ChatModel.last_activity_time.desc(), ChatModel.id.asc())
            .limit(limit)
            .offset(offset)
        )
        chats = result.scalars().all()
        items = [RawChat.model_validate(chat) for chat in chats]

        return RawPagination(
            items=items,
            lenItems=total,
            leftLimit=limit,
            leftOffset=max(0, offset - limit) if offset > 0 else None,
            rightLimit=limit,
            rightOffset=offset + limit if offset + limit < total else None,
        )
