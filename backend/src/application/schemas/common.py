from pydantic import AliasGenerator
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import alias_generators
from uuid import UUID
from typing import TypeVar, Generic


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=alias_generators.to_camel),
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class RequestPaginationSchema(BaseSchema):
    limit: int
    offset: int

class RequestPaginationByIDSchema(RequestPaginationSchema):
    id: UUID



T = TypeVar('T', bound=BaseModel)

class ResponsePaginationSchema(BaseSchema, Generic[T]):
    items: list[T] | T
    len_items: int
    left_limit: int | None
    left_offset: int | None
    right_limit: int | None
    right_offset: int | None
