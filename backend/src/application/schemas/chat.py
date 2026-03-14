from uuid import UUID
from datetime import datetime
from src.application.schemas.common import BaseModel
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Union

class ChatSchemas(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    start_time: datetime
    last_activity_time: datetime
    created_at: datetime
    updated_at: datetime

class CreateChatSchema(BaseModel):
    user_id: UUID
    title: str

class ChatRequest(BaseModel):
    message: str
    session_id: UUID | None = None

class ChatResponse(BaseModel):
    message: str
    session_id: UUID
    timestamp: datetime

class RawMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    chat_id: UUID
    text: str
    sender_type_id: str
    created_at: datetime
    updated_at: datetime

class RawChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    title: str
    start_time: datetime
    last_activity_time: datetime
    created_at: datetime
    updated_at: datetime

class RawChatWithMessages(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    created_at: datetime
    messages: List[RawMessage]

class RawPagination(BaseModel):
    items: Union[List[RawChat], List[RawChatWithMessages]]
    lenItems: int
    leftLimit: Optional[int] = None
    leftOffset: Optional[int] = None
    rightLimit: Optional[int] = None
    rightOffset: Optional[int] = None

class CreateChatRequest(BaseModel):
    user_id: UUID
    title: str
