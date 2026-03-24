from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.usecase.base import Usecase

from src.application.schemas.cards import CardSchema, CreateCardSchema, CreateCardDBSchema
from src.application.schemas.informations import CreateInformationSchema, InformationSchema
from src.infra.postgres.tables import CardsModel, InformationsModel
from src.infra.postgres.gateways.base import CreateReturningGate, GetAllGate

@dataclass(slots=True, frozen=True, kw_only=True)
class CreateCardsUsecase(Usecase[List[CreateCardSchema], List[CardSchema]]):
    session: AsyncSession
    create_card: CreateReturningGate[CardsModel, CreateCardDBSchema, CardSchema]
    get_informations: GetAllGate[InformationsModel, InformationSchema]
    create_information: CreateReturningGate[InformationsModel, CreateInformationSchema, InformationSchema]

    async def __call__(self, cards: List[CreateCardSchema]) -> List[CardSchema]:
        results: List[CardSchema] = []

        informations = await self.get_informations()
        information_titles = [info.title for info in informations]

        for card in cards:

            if card.information_title not in information_titles:
                info = await self.create_information(
                    CreateInformationSchema(title=card.information_title)
                )
                informations.append(info)
                information_titles.append(info.title)
                info_id = info.id
            else:
                index = information_titles.index(card.information_title)
                info_id = informations[index].id

            created = await self.create_card(
                CreateCardDBSchema(
                    title=card.title,
                    description=card.description,
                    information_id=info_id
                )
            )

            results.append(created)

        await self.session.commit()
        return results
