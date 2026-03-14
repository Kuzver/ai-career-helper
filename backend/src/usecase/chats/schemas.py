from pydantic import BaseModel
from uuid import UUID
from src.application.schemas.messages import MessageSchemas
from datetime import datetime
class GetChatMessaesSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    messages: list[MessageSchemas]
