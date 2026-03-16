from typing import Dict, List, Optional
from gigachat import GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger

SYSTEM_PROMPT = (
    "Ты — дружелюбный ИИ-помощник по карьере и обучению. "
    "Ты отвечаешь на любые вопросы пользователя — как на профессиональные, "
    "так и на повседневные. Будь вежливым, полезным и кратким. "
    "Если вопрос связан с карьерой, резюме, обучением или IT — "
    "давай экспертные советы. На остальные вопросы отвечай как умный собеседник."
)


class Gigachat:
    def __init__(self) -> None:
        self.model = GigaChatAsyncClient(
            credentials=config.gigachat.authorization_key,
            verify_ssl_certs=False,
        )

    async def __call__(
        self,
        user_query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        messages = [Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT)]

        if history:
            for msg in history[-10:]:
                role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg["content"]))

        messages.append(Messages(role=MessagesRole.USER, content=user_query))

        resp = await self.model.achat(Chat(messages=messages))
        return resp.choices[0].message.content
