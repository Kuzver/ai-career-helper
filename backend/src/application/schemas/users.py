from uuid import UUID
from datetime import datetime
from src.application.schemas.common import BaseModel

class UserSchemas(BaseModel):
    id: UUID
    first_name: str | None
    email: str
    corporate_account_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CreateUserSchema(BaseModel):
    id: UUID
    email: str = "example@email.com"
    first_name: str | None = None
    is_active: bool = True
    policy_accepted: bool
