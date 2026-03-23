from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from src.infra.postgres.tables import ChatModel, MessageModel
from src.infra.gigachat.chat import Gigachat


class AutoTitleUsecase:
    def __init__(self, session: AsyncSession, gigachat: Gigachat):
        self.session = session
        self.gigachat = gigachat

    async def __call__(self, chat_id: UUID) -> str | None:
        msg_count = await self.session.scalar(
            select(func.count()).where(MessageModel.chat_id == chat_id)
        )
        if msg_count not in (2, 6):
            return None

        result = await self.session.execute(
            select(MessageModel.text, MessageModel.sender_type_id)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at)
            .limit(6)
        )
        messages = result.all()
        if not messages:
            return None

        conversation = "\n".join(
            f"{'User' if m.sender_type_id == 'user' else 'Bot'}: {m.text[:200]}"
            for m in messages
        )

        try:
            title = await self.gigachat(
                f"Придумай короткое название (максимум 5 слов) для этого диалога. "
                f"Верни ТОЛЬКО название, без кавычек и пояснений.\n\n{conversation}"
            )
            title = title.strip().strip('"').strip("«»")[:100]

            chat_result = await self.session.execute(
                select(ChatModel).where(ChatModel.id == chat_id)
            )
            chat = chat_result.scalar_one_or_none()
            if chat:
                chat.title = title
                await self.session.commit()
            return title
        except Exception as e:
            logger.error(f"Auto-title error: {e}")
            return None
