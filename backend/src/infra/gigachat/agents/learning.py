from dataclasses import dataclass

from src.infra.gigachat.chat import Gigachat
from src.usecase.message.schemas import RequestMessageSchema


@dataclass(slots=True, frozen=True, kw_only=True)
class LearningAgent:
    chat: Gigachat

    async def __call__(self, data: RequestMessageSchema, user_context: str | None = None) -> str:
        query = data.text.lower()

        if any(k in query for k in ("roadmap", "дорожн", "план обучен", "учебный план")):
            return await self._create_roadmap(data.text, user_context)

        if any(k in query for k in ("объясн", "концепц", "что такое", "как работает")):
            return await self._explain_concept(data.text, user_context)

        if any(k in query for k in ("книг", "курс", "материал", "туториал", "ресурс")):
            return await self._recommend_materials(data.text, user_context)

        return await self._general_learning_help(data.text, user_context)

    async def _create_roadmap(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Ты — опытный ментор. Создай образовательный roadmap "
            "на основе запроса пользователя. Укажи этапы, сроки, "
            "навыки, проекты для практики и чекпоинты.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _explain_concept(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Объясни концепцию простым языком. Используй аналогии, "
            "примеры и практические применения.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _recommend_materials(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Подбери обучающие материалы: книги, курсы, статьи, видео. "
            "Укажи примерное время на освоение.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _general_learning_help(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Ты — ИИ-помощник по обучению и развитию. "
            "Дай полезный и конкретный ответ.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)
