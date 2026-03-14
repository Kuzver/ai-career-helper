from uuid import UUID
from datetime import datetime
from src.application.schemas.common import BaseModel

class InformationSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class CreateInformationSchema(BaseModel):
    title: str

