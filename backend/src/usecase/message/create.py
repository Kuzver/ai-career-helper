from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import CreateReturningGate
from src.infra.postgres.tables import MessageModel, UserCareersModel
from src.application.schemas.messages import MessageSchemas, CreateMessageSchema
from src.application.schemas.auth import AuthSchema
from src.usecase.message.schemas import RequestMessageSchema
from src.infra.gigachat.agents.orchestrator import OrchestratorAgent


def build_user_context(career) -> str | None:
    if not career:
        return None

    parts = []
    if career.name:
        parts.append(f"Имя: {career.name}")
    if career.experience_level:
        parts.append(f"Опыт: {career.experience_level}")
    if career.skills:
        parts.append(f"Навыки: {career.skills}")
    if career.career_goal:
        parts.append(f"Карьерная цель: {career.career_goal}")

    return ". ".join(parts) if parts else None


@dataclass(slots=True, frozen=True, kw_only=True)
class MessengerUsecase(Usecase[RequestMessageSchema, MessageSchemas]):
    session: AsyncSession
    auth: AuthSchema
    create_message: CreateReturningGate[MessageModel, CreateMessageSchema, MessageSchemas]
    orchestrator: OrchestratorAgent

    async def __call__(self, data: RequestMessageSchema) -> MessageSchemas:
        result = await self.session.execute(
            select(UserCareersModel).where(UserCareersModel.user_id == self.auth.id)
        )
        career = result.scalar_one_or_none()
        user_context = build_user_context(career)

        async with self.session.begin():
            await self.create_message(CreateMessageSchema(
                chat_id=data.chat_id,
                text=data.text,
                sender_type_id="user"
            ))
            answer = await self.orchestrator(data=data, user_context=user_context)

            return await self.create_message(CreateMessageSchema(
                chat_id=data.chat_id,
                text=answer,
                sender_type_id="chat"
            ))
