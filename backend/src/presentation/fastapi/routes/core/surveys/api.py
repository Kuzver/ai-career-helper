from uuid import UUID, uuid4
from datetime import datetime, timezone
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.schemas.auth import AuthSchema
from src.application.schemas.survey import (
    SurveyListItem, SurveyDetail, SurveyQuestionOut, SurveyOptionOut,
    SurveySubmitRequest, SurveySubmitResponse,
)
from src.infra.postgres.tables import (
    SurveyModel, SurveyQuestionModel, SurveyOptionModel,
    SurveyResponseModel, SurveyAnswerModel,
)
from src.infra.gigachat.chat import Gigachat

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.get("", response_model=list[SurveyListItem])
async def list_surveys(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    result = await session.execute(
        select(SurveyModel).where(SurveyModel.is_active == True).order_by(SurveyModel.created_at)
    )
    surveys = result.scalars().all()

    resp_result = await session.execute(
        select(SurveyResponseModel.survey_id).where(SurveyResponseModel.user_id == auth.id)
    )
    completed_ids = {r for r in resp_result.scalars().all()}

    return [
        SurveyListItem(
            id=s.id, title=s.title, description=s.description,
            is_mandatory=s.is_mandatory,
            is_completed=s.id in completed_ids,
        )
        for s in surveys
    ]


@ROUTER.get("/mandatory/pending", response_model=list[SurveyListItem])
async def pending_mandatory(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    resp_result = await session.execute(
        select(SurveyResponseModel.survey_id).where(SurveyResponseModel.user_id == auth.id)
    )
    completed_ids = {r for r in resp_result.scalars().all()}

    result = await session.execute(
        select(SurveyModel).where(
            SurveyModel.is_active == True,
            SurveyModel.is_mandatory == True,
        )
    )
    surveys = result.scalars().all()

    return [
        SurveyListItem(
            id=s.id, title=s.title, description=s.description,
            is_mandatory=True, is_completed=False,
        )
        for s in surveys if s.id not in completed_ids
    ]


@ROUTER.get("/{survey_id}", response_model=SurveyDetail)
async def get_survey(
    survey_id: UUID,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    result = await session.execute(
        select(SurveyModel).where(SurveyModel.id == survey_id, SurveyModel.is_active == True)
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    q_result = await session.execute(
        select(SurveyQuestionModel)
        .where(SurveyQuestionModel.survey_id == survey_id)
        .order_by(SurveyQuestionModel.order)
    )
    questions = q_result.scalars().all()

    question_ids = [q.id for q in questions]
    o_result = await session.execute(
        select(SurveyOptionModel)
        .where(SurveyOptionModel.question_id.in_(question_ids))
        .order_by(SurveyOptionModel.order)
    ) if question_ids else None
    options = o_result.scalars().all() if o_result else []

    options_by_q: dict[UUID, list[SurveyOptionOut]] = {}
    for o in options:
        options_by_q.setdefault(o.question_id, []).append(
            SurveyOptionOut(id=o.id, text=o.text, order=o.order)
        )

    return SurveyDetail(
        id=survey.id, title=survey.title, description=survey.description,
        is_mandatory=survey.is_mandatory,
        questions=[
            SurveyQuestionOut(
                id=q.id, text=q.text, question_type=q.question_type,
                order=q.order, options=options_by_q.get(q.id, []),
            )
            for q in questions
        ],
    )


@ROUTER.post("/{survey_id}/submit", response_model=SurveySubmitResponse)
async def submit_survey(
    survey_id: UUID,
    body: SurveySubmitRequest,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
    gigachat: FromDishka[Gigachat],
):
    result = await session.execute(
        select(SurveyModel).where(SurveyModel.id == survey_id, SurveyModel.is_active == True)
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    existing = await session.execute(
        select(SurveyResponseModel).where(
            SurveyResponseModel.user_id == auth.id,
            SurveyResponseModel.survey_id == survey_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Вы уже прошли этот опрос")

    response_id = uuid4()
    response = SurveyResponseModel(
        id=response_id,
        user_id=auth.id,
        survey_id=survey_id,
        is_validated=False,
    )
    session.add(response)

    for answer in body.answers:
        session.add(SurveyAnswerModel(
            id=uuid4(),
            response_id=response_id,
            question_id=answer.question_id,
            option_id=answer.option_id,
            free_text=answer.free_text,
        ))

    await session.flush()

    # Валидация через GigaChat
    validation_result = await _validate_answers(session, survey_id, body, gigachat)
    response.is_validated = True
    response.validation_result = validation_result

    await session.commit()

    return SurveySubmitResponse(
        response_id=response_id,
        is_validated=True,
        validation_result=validation_result,
    )


async def _validate_answers(
    session: AsyncSession,
    survey_id: UUID,
    body: SurveySubmitRequest,
    gigachat: Gigachat,
) -> str:
    q_result = await session.execute(
        select(SurveyQuestionModel).where(SurveyQuestionModel.survey_id == survey_id).order_by(SurveyQuestionModel.order)
    )
    questions = {q.id: q.text for q in q_result.scalars().all()}

    o_result = await session.execute(
        select(SurveyOptionModel).where(SurveyOptionModel.question_id.in_(questions.keys()))
    )
    options = {o.id: o.text for o in o_result.scalars().all()}

    lines = []
    for a in body.answers:
        q_text = questions.get(a.question_id, "?")
        if a.option_id:
            a_text = options.get(a.option_id, a.free_text or "?")
        else:
            a_text = a.free_text or "?"
        lines.append(f"Вопрос: {q_text}\nОтвет: {a_text}")

    prompt = (
        "Проверь ответы пользователя на опрос. Оцени:\n"
        "1. Адекватность — ответы осмысленные, а не случайные?\n"
        "2. Связность — ответы соответствуют вопросам?\n"
        "3. Полнота — на все вопросы даны ответы?\n\n"
        "Дай краткий вердикт (1-2 предложения).\n\n"
        + "\n\n".join(lines)
    )

    try:
        return await gigachat(prompt)
    except Exception as e:
        logger.error(f"Survey validation error: {e}")
        return "Валидация недоступна"
