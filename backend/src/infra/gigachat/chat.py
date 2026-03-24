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

# Ключевые слова ON-topic — если есть хотя бы 1, вопрос может быть по теме
ON_TOPIC_KEYWORDS = {
    "резюме", "cv", "ваканси", "собеседован", "карьер", "работ", "зарплат",
    "обучен", "курс", "roadmap", "план обучен", "программир", "код", "разработ",
    "python", "java", "javascript", "typescript", "react", "vue", "angular",
    "frontend", "backend", "fullstack", "devops", "qa", "тестиров",
    "sql", "git", "docker", "kubernetes", "алгоритм", "структур данных",
    "junior", "middle", "senior", "lead", "стажир", "стажёр",
    "портфолио", "linkedin", "фриланс", "it", "айти",
    "технолог", "фреймворк", "библиотек", "архитектур",
    "навык", "компетенц", "проект", "команд", "agile", "scrum",
    "rest", "api", "http", "база данных", "бд", "orm",
    "машинное обучен", "data science", "ml", "нейросет",
    "ci/cd", "деплой", "сервер", "хостинг", "облак",
    "soft skill", "менторств", "код ревью", "code review",
    "open source", "open-source", "вклад",
    "диплом", "курсов", "сертифик",
    "повыш", "продвиж", "рост",
}

# Ключевые слова OFF-topic — если есть, вопрос точно не по теме
OFF_TOPIC_KEYWORDS = {
    "погод", "рецепт", "готов", "кулинар",
    "планет", "плутон", "космос", "астроном", "звезд", "галактик",
    "полити", "выбор", "президент", "депутат", "партия",
    "фильм", "сериал", "кино", "музык", "песн",
    "спорт", "футбол", "хоккей", "баскетбол",
    "здоров", "медицин", "лекарств", "болезн", "врач",
    "религ", "бог", "церков", "молитв",
    "животн", "кошк", "собак", "питомец",
    "путешеств", "отдых", "туризм", "отель",
    "истори", "война", "битв", "древн", "средневеков",
    "географ", "столиц", "населен", "океан", "гор",
    "физик", "химия", "биолог", "математ",
    "анекдот", "шутк", "мем", "смешн",
    "знак зодиак", "гороскоп", "астролог",
    "отношен", "любов", "свадьб", "развод",
    "автомобил", "машин", "двигател",
    "еда", "ресторан", "кафе",
    "одежд", "мода", "стиль",
    "недвижимост", "квартир", "ипотек",
    "крипт", "биткоин", "форекс",
    "игр", "playstation", "xbox", "steam",
    "почему небо", "почему вода", "почему трава",
    "сколько весит", "какой цвет", "кто изобрел",
    "расскажи сказк", "напиши стих", "придумай истори",
}


def _is_on_topic(query: str) -> bool:
    """
    Детерминистичная проверка: off-topic keywords имеют приоритет.
    Если найден off-topic keyword И нет on-topic — точно off-topic.
    Если найден on-topic keyword — on-topic.
    Если ничего не найдено — off-topic (по умолчанию блокируем).
    """
    q = query.lower()

    on_matches = sum(1 for kw in ON_TOPIC_KEYWORDS if kw in q)
    off_matches = sum(1 for kw in OFF_TOPIC_KEYWORDS if kw in q)

    # Если есть off-topic маркер и нет on-topic → блокируем
    if off_matches > 0 and on_matches == 0:
        return False

    # Если есть on-topic маркер → пропускаем
    if on_matches > 0:
        return True

    # Нет ни одного маркера — по умолчанию БЛОКИРУЕМ
    # Это ключевое изменение: раньше было True (пропускаем),
    # теперь False (блокируем неизвестные запросы)
    return False


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
        if not _is_on_topic(user_query):
            response = OFF_TOPIC_RESPONSE
            if user_context:
                response += "\n\nСудя по вашему профилю, вам может быть полезно обратиться к разделу дорожной карты или задать вопрос по вашей специализации."
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
