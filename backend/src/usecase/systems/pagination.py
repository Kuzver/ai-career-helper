from dataclasses import dataclass
from pydantic import BaseModel
from src.application.schemas.common import ResponsePaginationSchema
from typing import TypeVar, Generic, Type


T = TypeVar('T', bound=BaseModel)

@dataclass(slots=True, frozen=True, kw_only=True)
class Pagination(Generic[T]):
    def __call__(self, items: list[T], limit: int, offset: int, schema_class: Type[T]) -> ResponsePaginationSchema:
        items = sorted(
            items,
            key=lambda x: x.created_at,
            reverse=True
        )
        if offset - limit > 0:
            left_limit = limit
            left_offset = offset-limit
        else:
            left_limit = None
            left_offset = None

        if offset + limit <= len(items) or 0 < len(items) - limit - offset < limit:
            right_limit = limit
            right_offset = offset+limit
        else:
            right_limit = None
            right_offset = None
        if limit+offset > len(items):
            limit = len(items) - offset

        items = items[offset:offset+limit]

        return ResponsePaginationSchema(
            items=[schema_class.model_validate(item) for item in items],
            len_items=len(items),
            left_offset=left_offset,
            left_limit=left_limit,
            right_limit=right_limit,
            right_offset=right_offset
        )

