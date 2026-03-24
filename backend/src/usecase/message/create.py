from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from loguru import logger
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import CreateReturningGate
from src.infra.postgres.tables import (
    MessageModel, UserCareersModel,
    SurveyResponseModel, SurveyAnswerModel,
    SurveyQuestionModel, SurveyOptionModel,
    UserRoadmapProgressModel, UserRoadmapModel,
)
from src.application.schemas.messages import MessageSchemas, CreateMessageSchema
from src.application.schemas.auth import AuthSchema
from src.usecase.message.schemas import RequestMessageSchema
from src.infra.gigachat.agents.orchestrator import OrchestratorAgent
from src.usecase.chats.auto_title import AutoTitleUsecase


def build_user_context(career, survey_context: str | None = None, roadmap_context: str | None = None) -> str | None:
    parts = []

    if career:
        if career.name:
            parts.append(f"Имя: {career.name}")
        if getattr(career, 'specialization', None):
            parts.append(f"Специализация: {career.specialization}")
        if career.experience_level:
            parts.append(f"Опыт: {career.experience_level}")
        if career.skills:
            parts.append(f"Навыки: {career.skills}")
        if career.career_goal:
            parts.append(f"Карьерная цель: {career.career_goal}")

    if survey_context:
        parts.append(f"\nРезультаты опросов:\n{survey_context}")

    if roadmap_context:
        parts.append(f"\nПрогресс по дорожной карте:\n{roadmap_context}")

    return "\n".join(parts) if parts else None


async def build_roadmap_context(session: AsyncSession, user_id: UUID) -> str | None:
    result = await session.execute(
        select(UserRoadmapProgressModel).where(UserRoadmapProgressModel.user_id == user_id)
    )
    items = result.scalars().all()
    if not items:
        return None

    by_roadmap: dict[str, list[str]] = {}
    for p in items:
        by_roadmap.setdefault(p.roadmap_key, []).append(p.step_id)

    lines = []
    for key, steps in by_roadmap.items():
        lines.append(f"- {key}: завершены шаги {', '.join(sorted(steps))}")

    return "\n".join(lines)


async def build_survey_context(session: AsyncSession, user_id: UUID) -> str | None:
    resp_result = await session.execute(
        select(SurveyResponseModel).where(SurveyResponseModel.user_id == user_id)
    )
    responses = resp_result.scalars().all()
    if not responses:
        return None

    response_ids = [r.id for r in responses]
    ans_result = await session.execute(
        select(SurveyAnswerModel).where(SurveyAnswerModel.response_id.in_(response_ids))
    )
    answers = ans_result.scalars().all()
    if not answers:
        return None

    q_ids = list({a.question_id for a in answers})
    q_result = await session.execute(
        select(SurveyQuestionModel).where(SurveyQuestionModel.id.in_(q_ids))
    )
    questions = {q.id: q.text for q in q_result.scalars().all()}

    o_ids = [a.option_id for a in answers if a.option_id]
    options = {}
    if o_ids:
        o_result = await session.execute(
            select(SurveyOptionModel).where(SurveyOptionModel.id.in_(o_ids))
        )
        options = {o.id: o.text for o in o_result.scalars().all()}

    lines = []
    for a in answers:
        q_text = questions.get(a.question_id, "")
        if a.option_id:
            a_text = options.get(a.option_id, a.free_text or "")
        else:
            a_text = a.free_text or ""
        if q_text and a_text:
            lines.append(f"- {q_text}: {a_text}")

    return "\n".join(lines) if lines else None


@dataclass(slots=True, frozen=True, kw_only=True)
class MessengerUsecase(Usecase[RequestMessageSchema, MessageSchemas]):
    session: AsyncSession
    auth: AuthSchema
    create_message: CreateReturningGate[MessageModel, CreateMessageSchema, MessageSchemas]
    orchestrator: OrchestratorAgent
    auto_title: AutoTitleUsecase

    async def __call__(self, data: RequestMessageSchema) -> MessageSchemas:
        result = await self.session.execute(
            select(UserCareersModel).where(UserCareersModel.user_id == self.auth.id)
        )
        career = result.scalar_one_or_none()
        survey_context = await build_survey_context(self.session, self.auth.id)
        roadmap_context = await build_roadmap_context(self.session, self.auth.id)
        user_context = build_user_context(career, survey_context, roadmap_context)

        await self.create_message(CreateMessageSchema(
            chat_id=data.chat_id,
            text=data.text,
            sender_type_id="user"
        ))
        answer = await self.orchestrator(data=data, user_context=user_context)

        bot_message = await self.create_message(CreateMessageSchema(
            chat_id=data.chat_id,
            text=answer,
            sender_type_id="chat"
        ))
        await self.session.flush()

        response = MessageSchemas(
            id=bot_message.id,
            chat_id=bot_message.chat_id,
            text=bot_message.text,
            sender_type_id=bot_message.sender_type_id,
            created_at=bot_message.created_at,
            updated_at=bot_message.updated_at,
        )

        # Автосохранение roadmap если бот вернул JSON
        await _try_save_roadmap(self.session, self.auth.id, answer)

        await self.session.commit()
        await self.auto_title(chat_id=data.chat_id)

        return response


async def _try_save_roadmap(session: AsyncSession, user_id: UUID, answer: str) -> None:
    """Парсит roadmap из ответа бота (JSON-блок или markdown-шаги) и сохраняет в БД."""
    import json as _json
    import re

    steps = []

    # Способ 1: JSON-блок ```roadmap-json [...]```
    match = _json_match = re.search(r"```(?:roadmap-json|json)\s*\n(.+?)\n```", answer, re.DOTALL)
    if match:
        try:
            parsed = _json.loads(match.group(1))
            if isinstance(parsed, list) and len(parsed) > 0:
                steps = parsed
        except Exception:
            pass

    # Способ 2: Парсинг markdown-шагов (#### **Шаг N: ...**  или ## N. ... или **Шаг N:**)
    if not steps:
        step_patterns = [
            r"#{2,4}\s*\*{0,2}(?:Шаг|Step)\s*(\d+)[.:]\s*(.+?)(?:\*{0,2})\s*$",
            r"#{2,4}\s*(\d+)\.\s*(.+?)$",
            r"\*{2}(?:Шаг|Этап)\s*(\d+)[.:]\s*(.+?)\*{2}",
        ]
        raw_steps = []
        for pattern in step_patterns:
            found = re.findall(pattern, answer, re.MULTILINE)
            if len(found) >= 3:
                raw_steps = found
                break

        if raw_steps:
            for i, (num, title) in enumerate(raw_steps):
                title = title.strip().strip("*").strip()
                # Попробуем найти описание после заголовка
                desc_pattern = re.escape(title) + r"[*]*\s*\n+([\s\S]*?)(?=\n#{2,4}|\n\*{2}(?:Шаг|Этап)|\Z)"
                desc_match = re.search(desc_pattern, answer)
                description = ""
                if desc_match:
                    desc_text = desc_match.group(1).strip()
                    lines = [l.strip() for l in desc_text.split("\n") if l.strip() and not l.strip().startswith("#")]
                    description = " ".join(lines[:3])[:300]

                steps.append({
                    "id": str(i + 1),
                    "title": title[:200],
                    "description": description,
                    "details": "",
                    "resources": [],
                    "skills": [],
                    "duration": "",
                })

    if not steps:
        return

    try:
        data_json = _json.dumps(steps, ensure_ascii=False)

        result = await session.execute(
            select(UserRoadmapModel).where(UserRoadmapModel.user_id == user_id)
        )
        rm = result.scalar_one_or_none()

        title = steps[0].get("title", "Мой roadmap") if steps else "Мой roadmap"
        full_title = f"Персональный roadmap"

        if rm:
            rm.title = full_title
            rm.data_json = data_json
        else:
            from uuid import uuid4 as _uuid4
            session.add(UserRoadmapModel(
                id=_uuid4(),
                user_id=user_id,
                title=full_title,
                description="Создан ИИ-ассистентом на основе вашего профиля",
                data_json=data_json,
            ))
        logger.info(f"Roadmap auto-saved: {len(steps)} steps for user {user_id}")
    except Exception as e:
        logger.error(f"Roadmap auto-save error: {e}")
