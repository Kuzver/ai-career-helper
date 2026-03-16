import pdfplumber
from io import BytesIO
from dataclasses import dataclass
from loguru import logger

from src.infra.gigachat.chat import Gigachat
from src.usecase.message.schemas import RequestMessageSchema


@dataclass(slots=True, frozen=True, kw_only=True)
class CareerAgent:
    chat: Gigachat

    async def __call__(self, data: RequestMessageSchema) -> str:
        query = data.text.lower()

        if "собеседован" in query and "вопрос" in query:
            return await self._generate_interview_questions(data.text)

        if "резюм" in query:
            if data.file:
                return await self._analyze_resume(data.file)
            return await self._help_compose_resume(data.text)

        if "ваканси" in query:
            if data.file:
                return await self._analyze_vacancy(data.file)
            return await self._discuss_vacancy(data.text)

        return await self._general_career_advice(data.text)

    async def _help_compose_resume(self, user_text: str) -> str:
        prompt = (
            "Ты — профессиональный карьерный консультант. "
            "Помоги пользователю составить резюме. "
            "Задай уточняющие вопросы, если информации недостаточно. "
            "Если пользователь дал достаточно данных — составь структурированное резюме.\n\n"
            f"Запрос пользователя: {user_text}"
        )
        return await self.chat(prompt)

    async def _analyze_resume(self, pdf_bytes: bytes) -> str:
        text = self._extract_pdf_text(pdf_bytes)
        prompt = (
            "Проанализируй это резюме и дай рекомендации по улучшению:\n\n"
            f"{text}\n\n"
            "Критерии: структура, конкретные достижения, "
            "соответствие требованиям, оптимизация под ATS."
        )
        return await self.chat(prompt)

    async def _analyze_vacancy(self, pdf_bytes: bytes) -> str:
        text = self._extract_pdf_text(pdf_bytes)
        prompt = (
            "Проанализируй вакансию, выдели плюсы и красные флаги:\n\n"
            f"{text}"
        )
        return await self.chat(prompt)

    async def _discuss_vacancy(self, user_text: str) -> str:
        prompt = (
            "Ты — карьерный консультант. Помоги пользователю разобраться с вакансией. "
            "Проанализируй и дай советы.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt)

    async def _generate_interview_questions(self, user_text: str) -> str:
        prompt = (
            "Сгенерируй 10-15 вопросов для подготовки к собеседованию "
            "на основе запроса пользователя. Включи технические, "
            "поведенческие вопросы и кейсы.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt)

    async def _general_career_advice(self, user_text: str) -> str:
        prompt = (
            "Ты — опытный карьерный консультант. "
            "Дай полезный и конкретный совет по запросу пользователя.\n\n"
            f"Запрос: {user_text}"
        )
        return await self.chat(prompt)

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
