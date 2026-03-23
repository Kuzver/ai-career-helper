import pdfplumber
from io import BytesIO
from dataclasses import dataclass
from loguru import logger

from src.infra.gigachat.chat import Gigachat
from src.usecase.message.schemas import RequestMessageSchema


@dataclass(slots=True, frozen=True, kw_only=True)
class CareerAgent:
    chat: Gigachat

    async def __call__(self, data: RequestMessageSchema, user_context: str | None = None) -> str:
        query = data.text.lower()

        if "собеседован" in query and "вопрос" in query:
            return await self._generate_interview_questions(data.text, user_context)

        if "резюм" in query:
            if data.file:
                return await self._analyze_resume(data.file, user_context)
            return await self._help_compose_resume(data.text, user_context)

        if "ваканси" in query:
            if data.file:
                return await self._analyze_vacancy(data.file, user_context)
            return await self._discuss_vacancy(data.text, user_context)

        return await self._general_career_advice(data.text, user_context)

    async def _help_compose_resume(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Ты — профессиональный HR-консультант. Помоги составить резюме. "
            "Спроси пошагово: 1) Желаемая позиция 2) Опыт работы (компания, должность, достижения с цифрами) "
            "3) Технические навыки 4) Образование. "
            "Сформируй структурированное резюме в Markdown, оптимизированное для ATS.\n\n"
            f"Запрос пользователя: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _analyze_resume(self, pdf_bytes: bytes, user_context: str | None = None) -> str:
        text = self._extract_pdf_text(pdf_bytes)
        prompt = (
            "Проанализируй резюме по критериям: 1) Структура 2) Конкретность (цифры, достижения) "
            "3) ATS-совместимость 4) Грамматика. "
            "Дай оценку 1-10 и конкретные рекомендации по улучшению.\n\n"
            f"{text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _analyze_vacancy(self, pdf_bytes: bytes, user_context: str | None = None) -> str:
        text = self._extract_pdf_text(pdf_bytes)
        prompt = (
            "Проанализируй вакансию, выдели плюсы и красные флаги:\n\n"
            f"{text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _discuss_vacancy(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Ты — карьерный консультант. Помоги пользователю разобраться с вакансией. "
            "Проанализируй и дай советы.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _generate_interview_questions(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Сгенерируй вопросы для собеседования. Раздели на: "
            "Технические (по стеку из запроса), Поведенческие (STAR-метод), Кейсовые. "
            "После каждого вопроса дай краткий эталонный ответ. Учитывай уровень пользователя.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    async def _general_career_advice(self, user_text: str, user_context: str | None = None) -> str:
        prompt = (
            "Ты — опытный карьерный консультант. "
            "Дай полезный и конкретный совет по запросу пользователя.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt, user_context=user_context)

    @staticmethod
    def _extract_pdf_text(pdf_bytes: bytes, max_chars: int = 2000) -> str:
        try:
            text = ""
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text[:max_chars] if text else "Не удалось извлечь текст из PDF"
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return f"Ошибка при чтении PDF: {e}"
