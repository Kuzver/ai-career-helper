from pydantic import BaseModel, Field, field_validator
from uuid import UUID

class AuthSchema(BaseModel):
    id: UUID = Field(alias="sub")

    @field_validator('id', mode='before')
    def convert_string_to_uuid(cls, v):
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError(f"Invalid UUID string: {v}")
        return v