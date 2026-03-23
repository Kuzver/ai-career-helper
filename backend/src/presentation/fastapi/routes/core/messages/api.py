from dishka.integrations.fastapi import DishkaRoute
from uuid import UUID
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from fastapi import status
from src.application.schemas.messages import MessageSchemas
from src.usecase.message.schemas import RequestMessageSchema
from src.usecase.message.create import MessengerUsecase
from src.infra.files.parser import validate_file, extract_text

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.post('', status_code=status.HTTP_200_OK, response_model=MessageSchemas)
async def create_message(
    usecase: FromDishka[MessengerUsecase],
    chat_id: UUID = Form(),
    text: str = Form(),
    file: UploadFile | None = File(None),
) -> MessageSchemas:
    file_bytes = None
    file_text = None

    if file and file.filename:
        file_bytes = await file.read()

        error = validate_file(file.filename, len(file_bytes))
        if error:
            raise HTTPException(status_code=400, detail=error)

        file_text = extract_text(file.filename, file_bytes)

    message_text = text
    if file_text:
        message_text = f"{text}\n\n[Содержимое файла {file.filename}]:\n{file_text}"

    return await usecase(RequestMessageSchema(
        chat_id=chat_id,
        text=message_text,
        file=file_bytes,
    ))
