from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.profile import ProfileResponse
from src.infra.postgres.tables import UserCareersModel


@dataclass(slots=True, frozen=True, kw_only=True)
class GetProfileUsecase:
    session: AsyncSession

    async def __call__(self, user_id: UUID) -> ProfileResponse:
        result = await self.session.execute(
            select(UserCareersModel).where(UserCareersModel.user_id == user_id)
        )
        career = result.scalar_one_or_none()

        if not career:
            return ProfileResponse()

        return ProfileResponse(
            name=career.name,
            specialization=career.experience_level,
            experience_level=career.experience_level,
            skills=career.skills,
            career_goal=career.career_goal,
        )
