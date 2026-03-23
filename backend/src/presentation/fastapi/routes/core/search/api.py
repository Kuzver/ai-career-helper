from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import ChatModel, ArticleModel

ROUTER = APIRouter(route_class=DishkaRoute)


class SearchResult(BaseModel):
    type: str
    id: str
    title: str
    url: str


@ROUTER.get("", response_model=list[SearchResult])
async def search(
    q: str,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    if not q or len(q) < 2:
        return []

    results: list[SearchResult] = []
    pattern = f"%{q}%"

    chat_result = await session.execute(
        select(ChatModel)
        .where(ChatModel.user_id == auth.id, ChatModel.title.ilike(pattern))
        .order_by(ChatModel.last_activity_time.desc())
        .limit(5)
    )
    for c in chat_result.scalars().all():
        results.append(SearchResult(
            type="chat", id=str(c.id), title=c.title,
            url=f"/chat?chatId={c.id}",
        ))

    article_result = await session.execute(
        select(ArticleModel)
        .where(ArticleModel.title.ilike(pattern))
        .limit(5)
    )
    for a in article_result.scalars().all():
        results.append(SearchResult(
            type="article", id=str(a.id), title=a.title,
            url=f"/knowledge-base/{a.slug}",
        ))

    return results
