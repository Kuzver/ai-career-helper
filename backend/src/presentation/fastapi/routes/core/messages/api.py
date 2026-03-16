from dishka.integrations.fastapi import DishkaRoute
from uuid import UUID
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter, UploadFile, Form, File
from fastapi import status
from src.application.schemas.messages import MessageSchemas
from src.usecase.message.schemas import RequestMessageSchema
from src.usecase.message.create import MessengerUsecase

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.post('', status_code=status.HTTP_200_OK, response_model=MessageSchemas)
async def create_message(
    usecase: FromDishka[MessengerUsecase],
    chat_id: UUID = Form(),
    text: str = Form(),
    file: UploadFile | None = File(None),
) -> MessageSchemas:
    file_bytes = None
    if file:
        file_bytes = await file.read()
    return await usecase(RequestMessageSchema(
        chat_id=chat_id,
        text=text,
        file=file_bytes,
    ))