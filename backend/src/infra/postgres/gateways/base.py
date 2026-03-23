from uuid import UUID
from dataclasses import dataclass
from sqlalchemy import insert, delete, update

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.infra.postgres.tables import BaseDBModel
from sqlalchemy import Select
from sqlalchemy.sql.dml import ReturningInsert, ReturningUpdate
from typing import TypeVar, Generic, Type
from src.application.errors import (
    DatabaseCreateError,
    DatabaseUpdateError,
    DatabaseDeleteError,
    NotFoundError,
)
from loguru import logger

TAppliable = Select | ReturningInsert | ReturningUpdate

TTable = TypeVar('TTable', bound=BaseDBModel)
TEntity = TypeVar('TEntity', bound=BaseModel)
TCreate = TypeVar('TCreate', bound=BaseModel)
TUpdate = TypeVar('TUpdate', bound=BaseModel)
TEntityId = TypeVar('TEntityId', bound=UUID)

@dataclass(slots=True, kw_only=True)
class PostgresGateway:
    session: AsyncSession

@dataclass(slots=True, kw_only=True)
class GetAllGate(Generic[TTable, TEntity], PostgresGateway):
    table: Type[TTable]
    schema_type: Type[TEntity]

    async def __call__(self) -> list[TEntity] | list[None]:
        stmt = Select(*self.table.group_by_fields())
        results = (await self.session.execute(stmt)).mappings().fetchall()
        if results == []:
            return  results
        return [self.schema_type.model_validate(result) for result in results]

@dataclass(slots=True, kw_only=True)
class GetAllByIdUserGate(Generic[TTable, TEntity, TEntityId], PostgresGateway):
    table: Type[TTable]
    schema_type: Type[TEntity]
    entity_id: Type[TEntityId]

    async def __call__(self, user_id: TEntityId) -> list[TEntity] | list[None]:
        stmt = Select(*self.table.group_by_fields()).where(self.table.user_id == user_id)
        results = (await self.session.execute(stmt)).mappings().fetchall()
        if results == []:
            return  results
        return [self.schema_type.model_validate(result) for result in results]

@dataclass(slots=True, kw_only=True)
class GetByIdGate(Generic[TTable, TEntityId, TEntity], PostgresGateway):
    table: Type[TTable]
    schema_type: Type[TEntity]
    entity_id: Type[TEntityId]

    async def __call__(self, id: TEntityId) -> TEntity:
        stmt = Select(*self.table.group_by_fields()).where(self.table.id == id)
        result = (await self.session.execute(stmt)).mappings().fetchone()
        logger.info(result)
        if result is None:
            raise  NotFoundError(self.table)
        logger.info(result)
        return self.schema_type.model_validate(result)


@dataclass(slots=True, kw_only=True)
class GetByEmailGate(Generic[TTable, TEntity], PostgresGateway):
    table: Type[TTable]
    schema_type: Type[TEntity]

    async def __call__(self, email: str) -> TEntity | None:
        stmt = Select(*self.table.group_by_fields()).where(self.table.email == email)
        result = (await self.session.execute(stmt)).mappings().fetchone()
        if result is None:
            return None
        return self.schema_type.model_validate(result)

@dataclass(slots=True, kw_only=True)
class CreateGate(Generic[TTable, TCreate], PostgresGateway):
    table: Type[TTable]
    create_schema_type: Type[TCreate]

    async def __call__(self, entity: TCreate) -> None:
        stmt = insert(self.table).values(**entity.model_dump())
        try:
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"CreateGate error [{self.table.__tablename__}]: {e}")
            raise DatabaseCreateError(self.table)

@dataclass(slots=True, kw_only=True)
class CreateReturningGate(Generic[TTable, TCreate, TEntity], PostgresGateway):
    table: Type[TTable]
    create_schema_type: Type[TCreate]
    schema_type: Type[TEntity]

    async def __call__(self, entity: TCreate) -> TEntity:
        stmt = insert(self.table).values(**entity.model_dump()).returning(self.table)
        try:
            result = (await self.session.execute(stmt)).scalar_one().__dict__
            return self.schema_type.model_validate(result)
        except Exception:
            raise DatabaseCreateError(self.table)


@dataclass(slots=True, kw_only=True)
class UpdateGate(Generic[TTable, TUpdate, TEntityId], PostgresGateway):
    table: Type[TTable]
    update_schema_type: Type[TUpdate]
    entity_id: Type[TEntityId]

    async def __call__(self, entity: TCreate, entity_id: TEntityId) -> None:
        stmt = update(self.table).where(self.table.id==entity_id).values(**entity.model_dump())
        try:
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"UpdateGate error [{self.table.__tablename__}]: {e}")
            raise DatabaseUpdateError(self.table)

@dataclass(slots=True, kw_only=True)
class UpdateReturningGate(Generic[TTable, TUpdate, TEntityId, TEntity], PostgresGateway):
    table: Type[TTable]
    update_schema_type: Type[TUpdate]
    entity_id: Type[TEntityId]
    schema_type: Type[TEntity]

    async def __call__(self, entity_id: TEntityId, entity: TUpdate) -> TEntity:
        stmt = update(self.table).where(self.table.id==entity_id).values(**entity.model_dump(exclude_none=True)).returning(self.table)
        try:
            result = (await self.session.execute(stmt)).scalar_one().__dict__
            return self.schema_type.model_validate(result)
        except Exception as e:
            logger.error(f"UpdateReturningGate error [{self.table.__tablename__}]: {e}")
            raise DatabaseUpdateError(self.table)


@dataclass(slots=True, kw_only=True)
class DeleteGate(Generic[TTable, TEntityId], PostgresGateway):
    table: Type[TTable]
    entity_id: Type[TEntityId]

    async def __call__(self, entity_id: TEntityId) -> None:
        stmt = delete(self.table).where(self.table.id==entity_id)
        try:
            await self.session.execute(stmt)
        except Exception as e:
            logger.error(f"DeleteGate error [{self.table.__tablename__}]: {e}")
            raise DatabaseDeleteError(self.table)

@dataclass(slots=True, kw_only=True)
class DeleteReturningGate(Generic[TTable, TEntityId, TEntity], PostgresGateway):
    table: Type[TTable]
    entity_id: Type[TEntityId]
    schema_type: Type[TEntity]

    async def __call__(self, entity_id: TEntityId) -> TEntity:
        stmt = delete(self.table).where(self.table.id==entity_id).returning(self.table)
        try:
            result = (await self.session.execute(stmt)).scalar_one().__dict__
            return self.schema_type.model_validate(result)
        except Exception as e:
            logger.error(f"DeleteReturningGate error [{self.table.__tablename__}]: {e}")
            raise DatabaseDeleteError(self.table)
