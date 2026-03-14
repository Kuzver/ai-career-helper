from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.schemas.chat import RawChatWithMessages, RawMessage, RawPagination
from src.infra.postgres.tables import ChatModel, MessageModel

class GetChatByIdUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, chat_id: str, limit: int = 50, offset: int = 0) -> RawPagination:
        # Получаем чат
        chat_result = await self.session.execute(
            select(ChatModel).where(ChatModel.id == chat_id)
        )
        chat = chat_result.scalar_one_or_none()
        if not chat:
            raise ValueError("Chat not found")
        
        # Получаем сообщения с пагинацией
        messages_query = select(MessageModel).where(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at)
        total = await self.session.scalar(select(func.count()).select_from(messages_query.subquery()))
        
        messages_result = await self.session.execute(
            messages_query.limit(limit).offset(offset)
        )
        messages = messages_result.scalars().all()
        
        raw_messages = [RawMessage.model_validate(msg) for msg in messages]
        
        chat_with_msgs = RawChatWithMessages(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            messages=raw_messages
        )
        
        return RawPagination(
            items=[chat_with_msgs],  # фронтенд ожидает массив, даже если один элемент
            lenItems=total,
            leftLimit=limit,
            leftOffset=max(0, offset - limit) if offset > 0 else None,
            rightLimit=limit,
            rightOffset=offset + limit if offset + limit < total else None
        )