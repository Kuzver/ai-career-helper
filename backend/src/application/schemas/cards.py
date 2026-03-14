from uuid import UUID
from datetime import datetime
from src.application.schemas.common import BaseModel

class CardSchema(BaseModel):
    id: UUID
    information_id: UUID
    title: str
    description: str
    updated_at: datetime
    created_at: datetime

class UpdateCardSchema(BaseModel):
    information_id: UUID
    title: str
    description: str
    updated_at: datetime

class CreateCardSchema(BaseModel):
    information_title: str
    title: str
    description: str

class CreateCardDBSchema(BaseModel):
    information_id: UUID
    title: str
    description: str
