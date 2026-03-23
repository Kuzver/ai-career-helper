from uuid import UUID, uuid4
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.application.schemas.survey import (
    SurveyCreate, SurveyUpdate, SurveyDetail, SurveyQuestionOut, SurveyOptionOut,
)
from src.infra.auth.admin import require_admin
from src.infra.postgres.tables import (
    SurveyModel, SurveyQuestionModel, SurveyOptionModel,
)

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.post("", status_code=status.HTTP_201_CREATED, response_model=SurveyDetail)
async def create_survey(
    body: SurveyCreate,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_admin(session, auth)

    survey_id = uuid4()
    session.add(SurveyModel(
        id=survey_id,
        title=body.title,
        description=body.description,
        is_mandatory=body.is_mandatory,
        is_active=True,
        created_by=auth.id,
    ))

    questions_out = []
    for q in body.questions:
        q_id = uuid4()
        session.add(SurveyQuestionModel(
            id=q_id,
            survey_id=survey_id,
            text=q.text,
            question_type=q.question_type,
            order=q.order,
        ))

        options_out = []
        for o in q.options:
            o_id = uuid4()
            session.add(SurveyOptionModel(
                id=o_id, question_id=q_id, text=o.text, order=o.order,
            ))
            options_out.append(SurveyOptionOut(id=o_id, text=o.text, order=o.order))

        questions_out.append(SurveyQuestionOut(
            id=q_id, text=q.text, question_type=q.question_type,
            order=q.order, options=options_out,
        ))

    await session.commit()

    return SurveyDetail(
        id=survey_id, title=body.title, description=body.description,
        is_mandatory=body.is_mandatory, questions=questions_out,
    )


@ROUTER.put("/{survey_id}", response_model=SurveyDetail)
async def update_survey(
    survey_id: UUID,
    body: SurveyUpdate,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_admin(session, auth)

    result = await session.execute(
        select(SurveyModel).where(SurveyModel.id == survey_id)
    )
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    if body.title is not None:
        survey.title = body.title
    if body.description is not None:
        survey.description = body.description
    if body.is_mandatory is not None:
        survey.is_mandatory = body.is_mandatory
    if body.is_active is not None:
        survey.is_active = body.is_active

    if body.questions is not None:
        # Удаляем старые вопросы (каскадно удалятся опции)
        await session.execute(
            delete(SurveyQuestionModel).where(SurveyQuestionModel.survey_id == survey_id)
        )
        await session.flush()

        questions_out = []
        for q in body.questions:
            q_id = uuid4()
            session.add(SurveyQuestionModel(
                id=q_id, survey_id=survey_id, text=q.text,
                question_type=q.question_type, order=q.order,
            ))

            options_out = []
            for o in q.options:
                o_id = uuid4()
                session.add(SurveyOptionModel(
                    id=o_id, question_id=q_id, text=o.text, order=o.order,
                ))
                options_out.append(SurveyOptionOut(id=o_id, text=o.text, order=o.order))

            questions_out.append(SurveyQuestionOut(
                id=q_id, text=q.text, question_type=q.question_type,
                order=q.order, options=options_out,
            ))
    else:
        questions_out = await _load_questions(session, survey_id)

    await session.commit()

    return SurveyDetail(
        id=survey.id, title=survey.title, description=survey.description,
        is_mandatory=survey.is_mandatory, questions=questions_out,
    )


@ROUTER.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: UUID,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_admin(session, auth)

    result = await session.execute(
        select(SurveyModel).where(SurveyModel.id == survey_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Опрос не найден")

    await session.execute(delete(SurveyModel).where(SurveyModel.id == survey_id))
    await session.commit()


async def _load_questions(session: AsyncSession, survey_id: UUID) -> list[SurveyQuestionOut]:
    q_result = await session.execute(
        select(SurveyQuestionModel).where(SurveyQuestionModel.survey_id == survey_id).order_by(SurveyQuestionModel.order)
    )
    questions = q_result.scalars().all()
    q_ids = [q.id for q in questions]

    o_result = await session.execute(
        select(SurveyOptionModel).where(SurveyOptionModel.question_id.in_(q_ids)).order_by(SurveyOptionModel.order)
    ) if q_ids else None
    options = o_result.scalars().all() if o_result else []

    opts_by_q: dict[UUID, list[SurveyOptionOut]] = {}
    for o in options:
        opts_by_q.setdefault(o.question_id, []).append(
            SurveyOptionOut(id=o.id, text=o.text, order=o.order)
        )

    return [
        SurveyQuestionOut(
            id=q.id, text=q.text, question_type=q.question_type,
            order=q.order, options=opts_by_q.get(q.id, []),
        )
        for q in questions
    ]
