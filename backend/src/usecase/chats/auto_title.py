from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger

from src.infra.postgres.tables import ChatModel, MessageModel
from src.infra.gigachat.chat import Gigachat, OFF_TOPIC_RESPONSE


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
            .order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
            .limit(6)
        )
        messages = result.all()
        if not messages:
            return None

        # Если последнее сообщение бота — off-topic ответ, ставим нейтральное название
        bot_messages = [m for m in messages if m.sender_type_id == "chat"]
        if bot_messages and OFF_TOPIC_RESPONSE[:40] in bot_messages[-1].text:
            try:
                chat_result = await self.session.execute(
                    select(ChatModel).where(ChatModel.id == chat_id)
                )
                chat = chat_result.scalar_one_or_none()
                if chat:
                    chat.title = "Новый диалог"
                    await self.session.commit()
            except Exception:
                pass
            return "Новый диалог"

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
        except Exception as e:
            logger.error(f"Auto-title gigachat error: {e}")
            return None

        try:
            chat_result = await self.session.execute(
                select(ChatModel).where(ChatModel.id == chat_id)
            )
            chat = chat_result.scalar_one_or_none()
            if chat:
                chat.title = title
                await self.session.commit()
            return title
        except Exception as e:
            logger.error(f"Auto-title db error: {e}")
            return None
