from typing import Dict, List, Optional
from gigachat import GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger

BASE_SYSTEM_PROMPT = (
    "Ты — ИИ-ассистент по карьере и обучению в IT. "
    "Отвечай только на вопросы по карьере, IT, программированию, обучению, резюме, собеседованиям. "
    "Никогда не упоминай GigaChat, Sber, Сбер или модели ИИ. Ты — «ИИ-ассистент». "
    "Форматируй ответы в Markdown. Учитывай профиль пользователя."
)

OFF_TOPIC_RESPONSE = (
    "К сожалению, этот вопрос выходит за рамки моих возможностей. "
    "Я — карьерный ИИ-помощник и могу помочь вам с:\n\n"
    "- **Составление и анализ резюме** — помогу написать или улучшить резюме\n"
    "- **Подготовка к собеседованиям** — вопросы, кейсы, советы\n"
    "- **Построение карьерного пути** — roadmap, план развития\n"
    "- **Рекомендации по обучению** — курсы, книги, материалы\n"
    "- **Объяснение технических концепций** — от алгоритмов до архитектуры\n"
    "- **Советы по поиску работы** — вакансии, зарплаты, нетворкинг"
)

TOPIC_CHECK_PROMPT = (
    "Определи, относится ли вопрос пользователя к одной из этих тем: "
    "карьера, IT, программирование, резюме, собеседования, обучение технологиям, "
    "поиск работы, профессиональное развитие. "
    "Ответь ОДНИМ словом: ДА или НЕТ. Ничего больше."
)

ON_TOPIC_KEYWORDS = {
    "резюме", "cv", "ваканси", "собеседован", "карьер", "работ", "зарплат",
    "обучен", "курс", "roadmap", "план", "программир", "код", "разработ",
    "python", "java", "javascript", "react", "frontend", "backend", "devops",
    "sql", "git", "docker", "алгоритм", "junior", "middle", "senior",
    "стажир", "портфолио", "linkedin", "фриланс", "it", "айти",
    "технолог", "фреймворк", "библиотек", "архитектур", "тестиров",
    "навык", "компетенц", "проект", "команд", "agile", "scrum",
    "rest",
}


def _quick_topic_check(query: str) -> bool | None:
    q = query.lower()
    matches = sum(1 for kw in ON_TOPIC_KEYWORDS if kw in q)
    if matches >= 2:
        return True
    if len(q) < 15 and matches == 0:
        return False
    return None


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
        quick = _quick_topic_check(user_query)

        if quick is None:
            try:
                check_messages = [
                    Messages(role=MessagesRole.SYSTEM, content=TOPIC_CHECK_PROMPT),
                    Messages(role=MessagesRole.USER, content=user_query),
                ]
                check_resp = await self.model.achat(Chat(messages=check_messages))
                answer = check_resp.choices[0].message.content.strip().lower()
                if answer.startswith("нет") or answer == "no":
                    quick = False
                else:
                    quick = True
            except Exception as e:
                logger.error(f"Topic check error: {e}")
                quick = True

        if quick is False:
            response = OFF_TOPIC_RESPONSE
            if user_context:
                response += f"\n\nСудя по вашему профилю, вам может быть полезно обратиться к разделу дорожной карты или задать вопрос по вашей специализации."
            return response

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
        content = resp.choices[0].message.content
        if not content:
            return "Не удалось получить ответ. Попробуйте переформулировать вопрос."
        return content
