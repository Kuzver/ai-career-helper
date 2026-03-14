import pdfplumber
from src.infra.gigachat.chat import Gigachat
from io import BytesIO
from dataclasses import dataclass
from loguru import logger
from src.usecase.message.schemas import RequestMessageSchema


@dataclass(slots=True, frozen=True, kw_only=True)
class CareerAgent():
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

    async def analyze_resume_tool(self, pdf: bytes | None) -> str:
        """Анализирует резюме из PDF файла"""
        if pdf is None:
            return "📂 Пришли свое резюме!!!"
        text = self.extract_pdf_text_tool(pdf)
        with pdfplumber.open(BytesIO(pdf)) as pdf:

            for page_num, page in enumerate(pdf.pages, 1):
                # Извлекаем текст со страницы
                text = page.extract_text()
        logger.info(text)
        prompt = f"""
        Проанализируй это резюме и дай рекомендации по улучшению:

        {text}

        Критерии анализа:
        1. Структура и читаемость
        2. Наличие конкретных достижений и метрик
        3. Соответствие современным требованиям
        4. Оптимизация под ATS системы
        5. Профессиональное впечатление

        Верни структурированный анализ.
        """

        response = await self.chat(prompt)
        return response

    async def analyze_vacancy_tool(self, pdf_path: bytes) -> str:
        """Анализирует вакансию из PDF файла"""
        text = self.extract_pdf_text_tool(pdf_path)
        # доставать из файла
        prompt = f"""
        Проанализируй вакансию и определи "красные флаги":

        {text}

        Ищи:
        1. Размытые обязанности
        2. Непрозрачные условия оплаты
        3. Завышенные требования
        4. Признаки токсичной рабочей среды
        5. Противоречивые условия

        Верни анализ с выделением позитивных и негативных аспектов.
        """

        response = await self.chat(prompt)
        return response

    async def generate_interview_questions_tool(self, position: str, level: str = "middle") -> str:
        """Генерирует вопросы для собеседования"""

        # доставать из файла
        prompt = f"""
        Сгенерируй список из 10-15 вопросов для собеседования на позицию {position} уровня {level}.
        Включи:
        - Технические вопросы
        - Поведенческие вопросы
        - Вопросы о мотивации
        - Кейсовые задания

        Для каждого вопроса укажи, на что обращать внимание в ответе.
        """

        response = await self.chat(prompt)
        return response


    async def __call__(self, data: RequestMessageSchema):
        q = data.text.lower()
        if "собеседован" in q and "вопрос" in q:
            logger.info(1)
            resp_text = await self.generate_interview_questions_tool(position=data.tex)
        elif "резюм" in q:
            resp_text = await self.analyze_resume_tool(pdf=data.file)

        elif "ваканси" in q and ".pdf" not in q:
            logger.info(2)
            prompt = (
                f"Проанализируй эту вакансию и укажи красные и зелёные флаги.\n\n"
                f"Текст запроса пользователя:\n{data.tex}"
            )
            resp_text = await self.chat(prompt)

        else:
            logger.info(3)
            # Всё остальное по карьере — просто отдаём LLM с историей
            resp_text = await self.chat(data.tex)
        return resp_text
