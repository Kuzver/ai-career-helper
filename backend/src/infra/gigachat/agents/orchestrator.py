from src.usecase.message.schemas import RequestMessageSchema
from src.infra.gigachat.agents.career import CareerAgent
from src.infra.gigachat.agents.learning import LearningAgent
from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class OrchestratorAgent():
    career_agent: CareerAgent
    learning_agent: LearningAgent


    async def __call__(self, data: RequestMessageSchema) -> str:
        q = data.text.lower()
        """Определяет, какой агент должен обработать запрос"""

        career_keywords = ['резюме', 'ваканси', 'собеседован', 'карьер', 'работ', 'cv']
        learning_keywords = ['обучен', 'изуч', 'курс', 'материал', 'roadmap', 'концепц', 'учиться', 'обучаться']

        tech_keywords = [
            'программир', 'python', 'java', 'c++', 'c#', 'sql',
            'алгоритм', 'структур данных', 'машинное обучен', 'ml',
            'data', 'аналитик', 'backend', 'frontend', 'devops',
            'langgraph', 'лангграф', 'llm', 'агент', 'multi-agent'
        ]

        base_match = any(k in q for k in career_keywords + learning_keywords)

        is_explain_tech = ("объясн" in q) and any(k in q for k in tech_keywords)

        is_career_or_learning = base_match or is_explain_tech

        if not is_career_or_learning:
            # нужно брать из базы ответов
            response = ("Я специализированный ассистент по вопросам карьеры и обучения.\n\n"
                        "Моё основное предназначение:\n"
                        "• анализировать резюме и вакансии,\n"
                        "• помогать с подготовкой к собеседованиям,\n"
                        "• строить образовательные roadmap’ы и планы развития,\n"
                        "• подбирать материалы для обучения и объяснять сложные концепции.\n\n"
                        "Если у тебя есть вопрос про карьеру, обучение или резюме — сформулируй его, "
                        "и я помогу максимально детально. По другим темам я, к сожалению, не отвечаю.")
            return response

        career_score = sum(1 for keyword in career_keywords if keyword in q)
        learning_score = sum(1 for keyword in learning_keywords if keyword in q)

        if career_score > learning_score:
            # тут таску надо регистирировать в редис
            response = await  self.career_agent(data)
            return response
        else:
            # тут таску надо регистирировать в редис
            # если примерно одинаково — по умолчанию считаем, что это про обучение
            response = await self.learning_agent(data)
            return response
