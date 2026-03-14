from pydantic import BaseModel
from uuid import UUID

from fastapi import File

class RequestMessageSchema(BaseModel):
    chat_id: UUID
    text: str
    file: None | bytes = File()
