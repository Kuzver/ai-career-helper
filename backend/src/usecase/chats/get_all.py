from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infra.postgres.tables import ChatModel
from src.application.schemas.chat import RawChat, RawPagination
from src.application.schemas.auth import AuthSchema


class GetAllChatUsecase:
    def __init__(self, session: AsyncSession, auth: AuthSchema):
        self.session = session
        self.auth = auth

    async def __call__(self, limit: int = 50, offset: int = 0) -> RawPagination:
        result = await self.session.execute(
            select(ChatModel)
            .where(ChatModel.user_id == self.auth.id)
            .order_by(ChatModel.last_activity_time.desc())
        )
        chats = result.scalars().all()
        items = [RawChat.model_validate(chat) for chat in chats]
        return RawPagination(
            items=items,
            lenItems=len(items),
            leftLimit=None,
            leftOffset=None,
            rightLimit=None,
            rightOffset=None,
        )