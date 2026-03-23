from uuid import UUID, uuid4
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.application.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleDetail, CategoryOut, CategoryCreate,
)
from src.infra.auth.admin import require_editor
from src.infra.postgres.tables import ArticleModel, ArticleCategoryModel

ROUTER = APIRouter(route_class=DishkaRoute)


# Categories

@ROUTER.post("/categories", status_code=status.HTTP_201_CREATED, response_model=CategoryOut)
async def create_category(
    body: CategoryCreate,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_editor(session, auth)
    cat_id = uuid4()
    session.add(ArticleCategoryModel(id=cat_id, name=body.name, slug=body.slug, order=body.order))
    await session.commit()
    return CategoryOut(id=cat_id, name=body.name, slug=body.slug, order=body.order)


@ROUTER.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(cat_id: UUID, session: FromDishka[AsyncSession], auth: FromDishka[AuthSchema]):
    await require_editor(session, auth)
    await session.execute(delete(ArticleCategoryModel).where(ArticleCategoryModel.id == cat_id))
    await session.commit()


# Articles

@ROUTER.post("", status_code=status.HTTP_201_CREATED, response_model=ArticleDetail)
async def create_article(
    body: ArticleCreate,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_editor(session, auth)
    article_id = uuid4()
    session.add(ArticleModel(
        id=article_id, title=body.title, slug=body.slug,
        content_md=body.content_md, category_id=body.category_id,
        specialization=body.specialization,
    ))
    await session.commit()

    cat = None
    if body.category_id:
        cr = await session.execute(
            select(ArticleCategoryModel).where(ArticleCategoryModel.id == body.category_id)
        )
        c = cr.scalar_one_or_none()
        if c:
            cat = CategoryOut(id=c.id, name=c.name, slug=c.slug, order=c.order)

    return ArticleDetail(
        id=article_id, title=body.title, slug=body.slug,
        content_md=body.content_md, specialization=body.specialization, category=cat,
    )


@ROUTER.put("/{article_id}", response_model=ArticleDetail)
async def update_article(
    article_id: UUID,
    body: ArticleUpdate,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    await require_editor(session, auth)
    result = await session.execute(select(ArticleModel).where(ArticleModel.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    if body.title is not None: article.title = body.title
    if body.slug is not None: article.slug = body.slug
    if body.content_md is not None: article.content_md = body.content_md
    if body.category_id is not None: article.category_id = body.category_id
    if body.specialization is not None: article.specialization = body.specialization
    await session.commit()

    cat = None
    if article.category_id:
        cr = await session.execute(
            select(ArticleCategoryModel).where(ArticleCategoryModel.id == article.category_id)
        )
        c = cr.scalar_one_or_none()
        if c:
            cat = CategoryOut(id=c.id, name=c.name, slug=c.slug, order=c.order)

    return ArticleDetail(
        id=article.id, title=article.title, slug=article.slug,
        content_md=article.content_md, specialization=article.specialization, category=cat,
    )


@ROUTER.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: UUID, session: FromDishka[AsyncSession], auth: FromDishka[AuthSchema]):
    await require_editor(session, auth)
    await session.execute(delete(ArticleModel).where(ArticleModel.id == article_id))
    await session.commit()
