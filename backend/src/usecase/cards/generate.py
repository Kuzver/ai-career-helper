from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import os
from src.usecase.base import Usecase

from src.application.schemas.cards import CardSchema, CreateCardSchema, CreateCardDBSchema
from src.application.schemas.informations import CreateInformationSchema, InformationSchema
from src.infra.postgres.tables import CardsModel, InformationsModel
from src.infra.postgres.gateways.base import CreateReturningGate, GetAllGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GenerateCardsUsecase(Usecase[None, List[CardSchema]]):
    session: AsyncSession

    create_card: CreateReturningGate[CardsModel, CreateCardDBSchema, CardSchema]
    get_informations: GetAllGate[InformationsModel, InformationSchema]
    create_information: CreateReturningGate[InformationsModel, CreateInformationSchema, InformationSchema]

    async def __call__(self, cards: None = None) -> List[CardSchema]:
        results: List[CardSchema] = []

        async with self.session.begin():
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, 'cards.json')

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for info_item in data:
                information = await self.create_information(CreateInformationSchema(title=info_item['information_title']))
                for card_data in info_item['cards']:
                    card_result = await self.create_card(CreateCardDBSchema(
                        information_id=information.id,
                        title=card_data['title'],
                        description=card_data['description']
                    ))
                    results.append(card_result)
        return results