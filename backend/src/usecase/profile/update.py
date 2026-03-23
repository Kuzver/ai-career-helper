from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.profile import ProfileUpdateRequest, ProfileResponse
from src.infra.postgres.tables import UserCareersModel


class UpdateProfileUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, user_id: UUID, data: ProfileUpdateRequest) -> ProfileResponse:
        async with self.session.begin():
            result = await self.session.execute(
                select(UserCareersModel).where(UserCareersModel.user_id == user_id)
            )
            career = result.scalar_one_or_none()

            if career:
                if data.name is not None:
                    career.name = data.name
                if data.specialization is not None:
                    career.specialization = data.specialization
                if data.experience_level is not None:
                    career.experience_level = data.experience_level
                if data.skills is not None:
                    career.skills = data.skills
                if data.career_goal is not None:
                    career.career_goal = data.career_goal
            else:
                career = UserCareersModel(
                    id=uuid4(),
                    user_id=user_id,
                    name=data.name,
                    specialization=data.specialization,
                    experience_level=data.experience_level or "",
                    skills=data.skills,
                    career_goal=data.career_goal,
                )
                self.session.add(career)

            response = ProfileResponse(
                name=career.name,
                specialization=data.specialization,
                experience_level=career.experience_level,
                skills=career.skills,
                career_goal=career.career_goal,
            )

        return response
