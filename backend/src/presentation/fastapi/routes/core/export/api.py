from uuid import UUID
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import MessageModel, ChatModel, ArticleModel
from src.infra.files.exporter import export_markdown, export_docx, export_html

ROUTER = APIRouter(route_class=DishkaRoute)

FORMATS = {
    "md": ("text/markdown", ".md", export_markdown),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx", export_docx),
    "html": ("text/html", ".html", export_html),
}


class ExportRequest(BaseModel):
    message_id: UUID
    format: str


@ROUTER.post("")
async def export_message(
    body: ExportRequest,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    if body.format not in FORMATS:
        raise HTTPException(status_code=400, detail=f"Формат '{body.format}' не поддерживается. Допустимые: md, docx, html")

    result = await session.execute(
        select(MessageModel).where(MessageModel.id == body.message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    chat_result = await session.execute(
        select(ChatModel).where(
            ChatModel.id == message.chat_id,
            ChatModel.user_id == auth.id,
        )
    )
    if not chat_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Нет доступа")

    content_type, extension, exporter = FORMATS[body.format]
    file_bytes = exporter(message.text)

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="response{extension}"'},
    )


class ExportArticleRequest(BaseModel):
    slug: str
    format: str


@ROUTER.post("/article")
async def export_article(
    body: ExportArticleRequest,
    session: FromDishka[AsyncSession],
    auth: FromDishka[AuthSchema],
):
    if body.format not in FORMATS:
        raise HTTPException(status_code=400, detail="Формат не поддерживается")

    result = await session.execute(
        select(ArticleModel).where(ArticleModel.slug == body.slug)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    text = f"# {article.title}\n\n{article.content_md}"
    content_type, extension, exporter = FORMATS[body.format]
    file_bytes = exporter(text)

    safe_slug = article.slug.replace("/", "_")
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_slug}{extension}"'},
    )


class ExportRoadmapRequest(BaseModel):
    markdown: str
    format: str


@ROUTER.post("/roadmap")
async def export_roadmap(
    body: ExportRoadmapRequest,
    auth: FromDishka[AuthSchema],
):
    if body.format not in FORMATS:
        raise HTTPException(status_code=400, detail="Формат не поддерживается")

    content_type, extension, exporter = FORMATS[body.format]
    file_bytes = exporter(body.markdown)

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="roadmap{extension}"'},
    )
