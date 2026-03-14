import pdfplumber
from src.infra.gigachat.chat import Gigachat
from io import BytesIO
from dataclasses import dataclass
from src.usecase.message.schemas import RequestMessageSchema

@dataclass(slots=True, frozen=True, kw_only=True)
class LearningAgent():
    chat: Gigachat

    def extract_pdf_text_tool(self, pdf_bytes: bytes) -> str:
        """Извлекает текст из PDF файла, переданного в виде байтов"""
        try:
            text = ""
            # Используем BytesIO для работы с байтами
            with BytesIO(pdf_bytes) as byte_stream:
                with pdfplumber.open(byte_stream) as pdf:
                    for page in pdf.pages:
                        extracted_text = page.extract_text()
                        if extracted_text:
                            text += extracted_text + "\n"

            # Возвращаем первые 2000 символов или весь текст, если он короче
            return text[:2000] if text else "Не удалось извлечь текст из PDF"

        except Exception as e:
            return f"Ошибка при чтении PDF: {str(e)}"

    async def create_roadmap_tool(self, profession: str,) -> str:
        """Создает образовательный roadmap"""
        prompt = f"""
        Изучи запрос пользователя и определи из его запроса на какой срок будет создаваться учебный план.
        Создай детальный образовательный roadmap для профессии {profession} на период, который ты определил из запроса ранее

        Структура:
        1. Цели обучения
        2. Поэтапный план (с временными метками)
        3. Ключевые навыки для освоения
        4. Рекомендуемые проекты для практики
        5. Метрики успеха
        6. Чекпоинты для самопроверки

        Сделай roadmap практичным и достижимым.
        """

        response = await self.chat(prompt)
        return response

    async def recommend_materials_tool(self, topic: str, level: str = "beginner") -> str:
        """Рекомендует обучающие материалы"""
        prompt = f"""
        Подбери рекомендации обучающих материалов по теме {topic} для уровня {level}.

        Включи:
        - Книги (с обоснованием выбора)
        - Онлайн курсы
        - Статьи и блоги
        - Видео материалы
        - Практические задания
        - Сообщества для обучения

        Укажи примерное время на освоение каждого ресурса.
        """

        response = await self.chat(prompt)
        return response

    async def explain_concept_tool(self, concept: str, explanation_level: str = "новичок") -> str:
        """Объясняет сложные концепции простым языком"""
        prompt = f"""
        Объясни концепцию {concept} для уровня {explanation_level}.

        Используй:
        - Простые аналогии
        - Конкретные примеры
        - Визуальные метафоры
        - Практические применения

        Избегай сложной терминологии, объясняй как для новичка.
        """

        response =await self.chat(prompt)
        return response


    async def __call__(self, data: RequestMessageSchema):
        q = data.text.lower()
        if "roadmap" in q or "дорожн" in q or "план" in q:
            resp_text = await self.create_roadmap_tool(profession=data.text)

        elif "объясн" in q or "концепц" in q:
            resp_text = await self.explain_concept_tool(concept=data.text)

        else:
            resp_text = await self.chat(data.text)
        return resp_text