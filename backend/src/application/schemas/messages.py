from uuid import UUID
from datetime import datetime, timezone
from src.application.schemas.common import BaseModel

class MessageSchemas(BaseModel):
    id: UUID
    chat_id: UUID
    text: str
    sender_type_id: str
    created_at: datetime
    updated_at: datetime

class CreateMessageSchema(BaseModel):
    chat_id: UUID
    text: str
    sender_type_id: str
    created_at: datetime = datetime.now(timezone.utc)
