from dataclasses import dataclass

from src.infra.gigachat.chat import Gigachat
from src.usecase.message.schemas import RequestMessageSchema

ROADMAP_JSON_PROMPT = (
    "Ты — опытный ментор в IT. Создай персональный roadmap обучения.\n\n"
    "ВАЖНО: В конце ответа ОБЯЗАТЕЛЬНО добавь JSON-блок с данными roadmap в формате:\n"
    "```roadmap-json\n"
    '[{{"id":"1","title":"Название шага","description":"Описание","details":"Подробные инструкции 3-5 предложений",'
    '"resources":["Ресурс 1","Ресурс 2"],"skills":["Навык1","Навык2"],"duration":"1-2 месяца"}}]\n'
    "```\n"
    "Сначала дай текстовый ответ пользователю с описанием плана, "
    "а затем добавь JSON-блок. Создай 5-7 шагов с конкретными инструкциями."
)

ROADMAP_EDIT_PROMPT = (
    "Ты — опытный ментор. Пользователь хочет изменить свой roadmap.\n"
    "Текущий roadmap:\n{current}\n\n"
    "ВАЖНО: В конце ответа ОБЯЗАТЕЛЬНО добавь обновлённый JSON-блок:\n"
    "```roadmap-json\n[...шаги...]\n```\n"
    "Объясни что изменил, затем добавь полный обновлённый JSON."
)


@dataclass(slots=True, frozen=True, kw_only=True)
class LearningAgent:
    chat: Gigachat

    async def __call__(self, data: RequestMessageSchema, user_context: str | None = None) -> str:
        query = data.text.lower()

        if any(k in query for k in ("roadmap", "дорожн", "план обучен", "учебный план", "карт развит")):
            return await self._create_roadmap(data.text, user_context)

        if any(k in query for k in ("измени roadmap", "убери шаг", "добавь шаг", "обнови roadmap", "изменить карт")):
            return await self._edit_roadmap(data.text, user_context)

        if any(k in query for k in ("объясн", "концепц", "что такое", "как работает")):
            return await self._explain_concept(data.text, user_context)

        if any(k in query for k in ("книг", "курс", "материал", "туториал", "ресурс")):
            return await self._recommend_materials(data.text, user_context)

        return await self._general_learning_help(data.text, user_context)

    async def _create_roadmap(self, user_text: str, user_context: str | None = None) -> str:
        prompt = f"{ROADMAP_JSON_PROMPT}\n\nЗапрос пользователя: {user_text}"
        return await self.chat(prompt, user_context=user_context)

    async def _edit_roadmap(self, user_text: str, user_context: str | None = None) -> str:
        current = ""
        if user_context and "Roadmap:" in user_context:
            current = user_context.split("Roadmap:")[1][:2000]
        prompt = ROADMAP_EDIT_PROMPT.format(current=current or "Не найден") + f"\n\nЗапрос: {user_text}"
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
