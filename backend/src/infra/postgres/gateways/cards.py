from src.infra.postgres.gateways.base import PostgresGateway
from src.infra.postgres.tables import CardsModel, InformationsModel
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy import func
from  src.usecase.cards.schemas import CardsSchema, ResponseCardsSchema
from loguru import logger

@dataclass(slots=True, kw_only=True)
class GetCardsGate(PostgresGateway):
    async  def __call__(self, limit: int, offset: int) -> ResponseCardsSchema:
        numbered_cards = (
            select(
                CardsModel.id,
                CardsModel.title,
                CardsModel.description,
                CardsModel.created_at,
                CardsModel.information_id,
                InformationsModel.created_at.label('info_created_at'),
                func.row_number().over(
                    order_by=(
                        InformationsModel.created_at.desc(),
                        CardsModel.created_at
                    )
                ).label('global_card_num')
            )
            .join(InformationsModel, InformationsModel.id == CardsModel.information_id)
            .subquery()
        )

        limited_cards = (
            select(
                numbered_cards.c.id,
                numbered_cards.c.title,
                numbered_cards.c.description,
                numbered_cards.c.created_at,
                numbered_cards.c.information_id,
                numbered_cards.c.info_created_at
            )
            .where(numbered_cards.c.global_card_num <= limit + offset)
            .where(numbered_cards.c.global_card_num > offset * limit)
            .subquery()
        )

        cards_agg = (
            select(
                limited_cards.c.information_id,
                func.json_agg(
                    func.json_build_object(
                        'id', limited_cards.c.id,
                        'title', limited_cards.c.title,
                        'description', limited_cards.c.description,
                        'created_at', limited_cards.c.created_at
                    )
                ).label('cards')
            )
            .group_by(limited_cards.c.information_id)
            .subquery()
        )

        stmt = (
            select(
                InformationsModel.id,
                InformationsModel.title,
                InformationsModel.created_at,
                cards_agg.c.cards
            )
            .join(cards_agg, InformationsModel.id == cards_agg.c.information_id)
            .order_by(InformationsModel.created_at.desc())  # информация по убыванию
        )
        total_count_stmt = select(func.count(CardsModel.id))
        total_count = (await self.session.execute(total_count_stmt)).scalar()
        next = None
        prev = None
        if offset + limit <= total_count or total_count-offset > 0:
            next = f"/cards?offset={offset + limit}&limit={limit}"
        if offset - limit >= 0:
            prev = f"/cards?offset={offset - limit}&limit={limit}"

        results = (await self.session.execute(stmt)).mappings().fetchall()
        if results == []:
            return ResponseCardsSchema(items=[], total=0)
        return ResponseCardsSchema(
            items=[CardsSchema.model_validate(result) for result in results],
            next=next,
            prev=prev,
            total=total_count
        )