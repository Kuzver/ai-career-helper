from pydantic import BaseModel
from uuid import UUID


class RequestMessageSchema(BaseModel):
    chat_id: UUID
    text: str
    file: bytes | None = None
