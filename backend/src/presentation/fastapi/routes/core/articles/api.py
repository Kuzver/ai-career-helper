from uuid import UUID
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.application.schemas.article import ArticleListItem, ArticleDetail, CategoryOut
from src.infra.postgres.tables import ArticleModel, ArticleCategoryModel

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.get("/categories", response_model=list[CategoryOut])
async def list_categories(session: FromDishka[AsyncSession], auth: FromDishka[AuthSchema]):
    result = await session.execute(
        select(ArticleCategoryModel).order_by(ArticleCategoryModel.order)
    )
    return [CategoryOut(id=c.id, name=c.name, slug=c.slug, order=c.order) for c in result.scalars().all()]


@ROUTER.get("", response_model=list[ArticleListItem])
async def list_articles(
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
    category: str | None = None,
    specialization: str | None = None,
):
    query = select(ArticleModel).order_by(ArticleModel.created_at.desc())
    if specialization:
        query = query.where(
            (ArticleModel.specialization == specialization) | (ArticleModel.specialization == None)
        )

    result = await session.execute(query)
    articles = result.scalars().all()

    cat_ids = list({a.category_id for a in articles if a.category_id})
    cats = {}
    if cat_ids:
        cr = await session.execute(select(ArticleCategoryModel).where(ArticleCategoryModel.id.in_(cat_ids)))
        cats = {c.id: CategoryOut(id=c.id, name=c.name, slug=c.slug, order=c.order) for c in cr.scalars().all()}

    items = []
    for a in articles:
        cat = cats.get(a.category_id) if a.category_id else None
        if category and (not cat or cat.slug != category):
            continue
        items.append(ArticleListItem(
            id=a.id, title=a.title, slug=a.slug,
            specialization=a.specialization, category=cat,
        ))
    return items


@ROUTER.get("/{slug}", response_model=ArticleDetail)
async def get_article(slug: str, session: FromDishka[AsyncSession], auth: FromDishka[AuthSchema]):
    result = await session.execute(
        select(ArticleModel).where(ArticleModel.slug == slug)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

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
