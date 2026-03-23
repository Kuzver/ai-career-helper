from pydantic import BaseModel
from uuid import UUID


class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    order: int


class ArticleListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    specialization: str | None
    category: CategoryOut | None = None


class ArticleDetail(BaseModel):
    id: UUID
    title: str
    slug: str
    content_md: str
    specialization: str | None
    category: CategoryOut | None = None


class ArticleCreate(BaseModel):
    title: str
    slug: str
    content_md: str
    category_id: UUID | None = None
    specialization: str | None = None


class ArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content_md: str | None = None
    category_id: UUID | None = None
    specialization: str | None = None


class CategoryCreate(BaseModel):
    name: str
    slug: str
    order: int = 0
