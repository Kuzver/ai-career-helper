from uuid import UUID
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.application.schemas.chat import CreateChatRequest, RawChatWithMessages, RawPagination
from src.usecase.chats.create import CreateChatUsecase
from src.usecase.chats.get_all import GetAllChatUsecase
from src.usecase.chats.get_by_id import GetChatByIdUsecase
from src.usecase.chats.rename import RenameChatUsecase
from src.usecase.chats.delete import DeleteChatUsecase

ROUTER = APIRouter(route_class=DishkaRoute)


class RenameChatRequest(BaseModel):
    title: str


@ROUTER.get("/all", response_model=RawPagination)
async def get_chats(
    limit: int = 50,
    offset: int = 0,
    usecase: FromDishka[GetAllChatUsecase] = None
):
    return await usecase(limit=limit, offset=offset)


@ROUTER.post("", response_model=RawChatWithMessages)
async def create_chat(
    request: CreateChatRequest,
    usecase: FromDishka[CreateChatUsecase] = None
):
    return await usecase(request)


@ROUTER.get("/{chat_id}", response_model=RawPagination)
async def get_chat_by_id(
    chat_id: str,
    limit: int = 50,
    offset: int = 0,
    usecase: FromDishka[GetChatByIdUsecase] = None
):
    try:
        return await usecase(chat_id=chat_id, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ROUTER.patch("/{chat_id}")
async def rename_chat(
    chat_id: UUID,
    body: RenameChatRequest,
    usecase: FromDishka[RenameChatUsecase] = None,
):
    try:
        return await usecase(chat_id=chat_id, title=body.title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ROUTER.delete("/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: UUID,
    usecase: FromDishka[DeleteChatUsecase] = None,
):
    try:
        await usecase(chat_id=chat_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
