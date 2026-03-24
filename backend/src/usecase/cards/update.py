from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import UpdateReturningGate
from src.application.schemas.cards import CardSchema, UpdateCardSchema
from src.usecase.cards.schemas import GetUpdateCardsSchema
from src.infra.postgres.tables import CardsModel
from dataclasses import dataclass

@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCardUsecase(Usecase[GetUpdateCardsSchema, CardSchema]):
    session: AsyncSession
    update_card: UpdateReturningGate[CardsModel, UpdateCardSchema, UUID, CardSchema]

    async def __call__(self, data: GetUpdateCardsSchema) -> CardSchema:
        result = await self.update_card(entity_id=data.id, entity=data.card)
        await self.session.commit()
        return result
