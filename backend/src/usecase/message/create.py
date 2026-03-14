from multiprocessing.connection import answer_challenge
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from src.usecase.base import Usecase
from src.infra.postgres.gateways.base import CreateReturningGate
from src.infra.postgres.tables import MessageModel
from src.application.schemas.messages import MessageSchemas, CreateMessageSchema
from src.application.schemas.auth import AuthSchema
from src.usecase.message.schemas import RequestMessageSchema

from src.infra.gigachat.agents.orchestrator import OrchestratorAgent

@dataclass(slots=True, frozen=True, kw_only=True)
class MessengerUsecase(Usecase[RequestMessageSchema, MessageSchemas]):
    session: AsyncSession
    auth: AuthSchema
    create_message: CreateReturningGate[MessageModel, CreateMessageSchema, MessageSchemas]
    orchestrator: OrchestratorAgent

    async def __call__(self, data: RequestMessageSchema) -> MessageSchemas:
        async with self.session.begin():
            await self.create_message(CreateMessageSchema(
                chat_id=data.chat_id,
                text=data.text,
                sender_type_id="user"
            ))
            answer = await self.orchestrator(data=data)

            return await self.create_message(CreateMessageSchema(
                chat_id=data.chat_id,
                text=answer,
                sender_type_id="chat"
            ))
