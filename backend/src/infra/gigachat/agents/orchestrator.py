from dataclasses import dataclass
from loguru import logger

from src.usecase.message.schemas import RequestMessageSchema
from src.infra.gigachat.agents.career import CareerAgent
from src.infra.gigachat.agents.learning import LearningAgent

CAREER_KEYWORDS = [
    "резюме", "ваканси", "собеседован", "карьер", "работ", "cv",
    "зарплат", "оффер", "увольн", "начальник", "коллег", "hr",
    "трудоустр", "найм", "наём", "стажир", "стажёр",
]

LEARNING_KEYWORDS = [
    "обучен", "изуч", "курс", "материал", "roadmap", "концепц",
    "учиться", "обучаться", "книг", "туториал", "практик",
    "объясн", "что такое", "как работает", "план обучен",
]

TECH_KEYWORDS = [
    "программир", "python", "java", "javascript", "typescript",
    "c++", "c#", "sql", "алгоритм", "структур данных",
    "машинное обучен", "ml", "data", "аналитик",
    "backend", "frontend", "devops", "react", "vue", "angular",
    "django", "fastapi", "docker", "git", "linux", "api",
]


@dataclass(slots=True, frozen=True, kw_only=True)
class OrchestratorAgent:
    career_agent: CareerAgent
    learning_agent: LearningAgent

    async def __call__(self, data: RequestMessageSchema) -> str:
        query = data.text.lower()

        career_score = sum(1 for k in CAREER_KEYWORDS if k in query)
        learning_score = sum(1 for k in LEARNING_KEYWORDS if k in query)
        tech_score = sum(1 for k in TECH_KEYWORDS if k in query)

        # Tech keywords boost learning score
        if tech_score > 0 and career_score == 0:
            learning_score += tech_score

        logger.info(
            f"Orchestrator scores — career: {career_score}, "
            f"learning: {learning_score}, tech: {tech_score}"
        )

        if career_score > learning_score:
            return await self.career_agent(data)

        if learning_score > 0:
            return await self.learning_agent(data)

        # No keywords matched — route to learning agent as general helper
        return await self.learning_agent(data)
