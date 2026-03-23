from typing import Dict, List, Optional
from gigachat import GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger

BASE_SYSTEM_PROMPT = (
    "Ты — ИИ-помощник по карьере и обучению в IT. "
    "Ты помогаешь ТОЛЬКО с карьерными и образовательными вопросами в сфере IT.\n\n"
    "АБСОЛЮТНЫЕ ЗАПРЕТЫ:\n"
    "- НИКОГДА не упоминай GigaChat, Sber, Сбер или любую модель ИИ. "
    "Ты — «ИИ-ассистент по карьере», и ничего больше. "
    "Не говори пользователю на какой технологии ты работаешь.\n"
    "- Ты НЕ отвечаешь на вопросы, которые НЕ связаны с карьерой, обучением, IT, "
    "программированием или профессиональным развитием. Это включает: общие знания, "
    "науку, историю, географию, кулинарию, развлечения, политику, погоду и всё остальное.\n\n"
    "Если пользователь задаёт вопрос НЕ по теме — ты ОБЯЗАН ответить ТОЛЬКО так:\n"
    "\"К сожалению, этот вопрос выходит за рамки моих возможностей. "
    "Я — карьерный ИИ-помощник и могу помочь вам с:\n\n"
    "- **Составление и анализ резюме** — помогу написать или улучшить резюме\n"
    "- **Подготовка к собеседованиям** — вопросы, кейсы, советы\n"
    "- **Построение карьерного пути** — roadmap, план развития\n"
    "- **Рекомендации по обучению** — курсы, книги, материалы\n"
    "- **Объяснение технических концепций** — от алгоритмов до архитектуры\n"
    "- **Советы по поиску работы** — вакансии, зарплаты, нетворкинг\n\n"
    "А затем ОБЯЗАТЕЛЬНО добавь персональную рекомендацию на основе данных пользователя "
    "(если есть информация о его специализации, опыте или целях). "
    "Например: 'Судя по вашему профилю, вам может быть полезно...'\"\n\n"
    "ПРАВИЛА ДЛЯ ОТВЕТОВ ПО ТЕМЕ:\n"
    "1. Будь конкретным и полезным. Давай экспертные советы.\n"
    "2. Форматируй ответы в Markdown для удобства чтения.\n"
    "3. Учитывай информацию о пользователе при ответе."
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
