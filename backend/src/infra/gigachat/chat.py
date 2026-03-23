from typing import Dict, List, Optional
from gigachat import GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger

BASE_SYSTEM_PROMPT = (
    "Ты — ИИ-помощник по карьере и обучению в IT. "
    "Ты помогаешь пользователям с карьерными вопросами: составление резюме, "
    "подготовка к собеседованиям, построение карьерного пути, выбор технологий, "
    "план обучения, roadmap развития, поиск работы и вакансий.\n\n"
    "СТРОГИЕ ПРАВИЛА:\n"
    "1. Отвечай ТОЛЬКО на вопросы, связанные с карьерой, обучением, IT, "
    "программированием, профессиональным развитием.\n"
    "2. Если вопрос НЕ относится к этим темам — вежливо откажи и перечисли, "
    "чем ты можешь помочь:\n"
    "   - Составление и анализ резюме\n"
    "   - Подготовка к собеседованиям\n"
    "   - Построение карьерного пути и roadmap\n"
    "   - Рекомендации по обучению и курсам\n"
    "   - Объяснение технических концепций\n"
    "   - Советы по поиску работы\n"
    "3. Будь конкретным и полезным. Давай экспертные советы.\n"
    "4. Форматируй ответы в Markdown для удобства чтения."
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
        user_context: Optional[str] = None,
    ) -> str:
        system_prompt = BASE_SYSTEM_PROMPT
        if user_context:
            system_prompt += f"\n\nИнформация о пользователе:\n{user_context}"

        messages = [Messages(role=MessagesRole.SYSTEM, content=system_prompt)]

        if history:
            for msg in history[-10:]:
                role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg["content"]))

        messages.append(Messages(role=MessagesRole.USER, content=user_query))

        resp = await self.model.achat(Chat(messages=messages))
        return resp.choices[0].message.content
