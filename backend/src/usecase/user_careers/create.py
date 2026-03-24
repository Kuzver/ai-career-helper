from sqlalchemy.ext.asyncio import AsyncSession
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import CreateReturningGate
from src.application.schemas.user_careers import CreateUserCareersSchema, UserCareersSchema
from src.infra.postgres.tables import UserCareersModel
from dataclasses import dataclass

@dataclass(slots=True, frozen=True, kw_only=True)
class CreateUserCareerUsecase(Usecase[CreateUserCareersSchema, UserCareersSchema]):
    session: AsyncSession
    create_user_career: CreateReturningGate[UserCareersModel, CreateUserCareersSchema, UserCareersSchema]

    async def __call__(self, data: CreateUserCareersSchema) -> UserCareersSchema:
        result = await self.create_user_career(data)
        await self.session.commit()
        return result
