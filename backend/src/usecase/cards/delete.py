from sqlalchemy.ext.asyncio import AsyncSession
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import DeleteReturningGate
from src.application.schemas.cards import CardSchema
from src.infra.postgres.tables import CardsModel
from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteCardUsecase(Usecase[UUID, CardSchema]):
    session: AsyncSession
    delete_card: DeleteReturningGate[CardsModel, UUID, CardSchema]
    
    async def __call__(self, id: UUID) -> CardSchema:
        async with self.session.begin():
            return await self.delete_card(id)
