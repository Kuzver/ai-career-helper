from uuid import uuid4
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import UserRoadmapProgressModel, UserRoadmapModel

ROUTER = APIRouter(route_class=DishkaRoute)


class RoadmapStepData(BaseModel):
    id: str
    title: str
    description: str
    details: str = ""
    resources: list[str] = []
    skills: list[str] = []
    duration: str = ""


class PersonalRoadmapResponse(BaseModel):
    title: str
    description: str | None
    steps: list[RoadmapStepData]


class PersonalRoadmapSave(BaseModel):
    title: str
    description: str | None = None
    steps: list[RoadmapStepData]


@ROUTER.get("/personal", response_model=PersonalRoadmapResponse | None)
async def get_personal_roadmap(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    result = await session.execute(
        select(UserRoadmapModel).where(UserRoadmapModel.user_id == auth.id)
    )
    rm = result.scalar_one_or_none()
    if not rm:
        return None

    import json
    steps = json.loads(rm.data_json)
    return PersonalRoadmapResponse(title=rm.title, description=rm.description, steps=steps)


@ROUTER.put("/personal", response_model=PersonalRoadmapResponse)
async def save_personal_roadmap(
    body: PersonalRoadmapSave,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    import json
    data_json = json.dumps([s.model_dump() for s in body.steps], ensure_ascii=False)

    result = await session.execute(
        select(UserRoadmapModel).where(UserRoadmapModel.user_id == auth.id)
    )
    rm = result.scalar_one_or_none()

    if rm:
        rm.title = body.title
        rm.description = body.description
        rm.data_json = data_json
    else:
        rm = UserRoadmapModel(
            id=uuid4(),
            user_id=auth.id,
            title=body.title,
            description=body.description,
            data_json=data_json,
        )
        session.add(rm)

    await session.commit()
    return PersonalRoadmapResponse(title=body.title, description=body.description, steps=[s.model_dump() for s in body.steps])


@ROUTER.delete("/personal", status_code=204)
async def delete_personal_roadmap(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await session.execute(
        delete(UserRoadmapModel).where(UserRoadmapModel.user_id == auth.id)
    )
    await session.commit()


class ProgressToggleRequest(BaseModel):
    roadmap_key: str
    step_id: str


class ProgressItem(BaseModel):
    roadmap_key: str
    step_id: str


@ROUTER.get("/progress", response_model=list[ProgressItem])
async def get_progress(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
    roadmap_key: str | None = None,
):
    query = select(UserRoadmapProgressModel).where(UserRoadmapProgressModel.user_id == auth.id)
    if roadmap_key:
        query = query.where(UserRoadmapProgressModel.roadmap_key == roadmap_key)

    result = await session.execute(query)
    items = result.scalars().all()
    return [ProgressItem(roadmap_key=p.roadmap_key, step_id=p.step_id) for p in items]


@ROUTER.post("/progress", status_code=201)
async def toggle_progress(
    body: ProgressToggleRequest,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    existing = await session.execute(
        select(UserRoadmapProgressModel).where(
            UserRoadmapProgressModel.user_id == auth.id,
            UserRoadmapProgressModel.roadmap_key == body.roadmap_key,
            UserRoadmapProgressModel.step_id == body.step_id,
        )
    )
    item = existing.scalar_one_or_none()

    if item:
        await session.execute(
            delete(UserRoadmapProgressModel).where(UserRoadmapProgressModel.id == item.id)
        )
        await session.commit()
        return {"action": "removed", "step_id": body.step_id}
    else:
        session.add(UserRoadmapProgressModel(
            id=uuid4(),
            user_id=auth.id,
            roadmap_key=body.roadmap_key,
            step_id=body.step_id,
        ))
        await session.commit()
        return {"action": "added", "step_id": body.step_id}
