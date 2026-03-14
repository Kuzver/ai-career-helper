from src.infra.postgres.gateways.base import PostgresGateway
from src.infra.postgres.tables import ChatModel, MessageModel
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select
from sqlalchemy import func
from  src.usecase.chats.schemas import GetChatMessaesSchema
from loguru import logger

@dataclass(slots=True, kw_only=True)
class GetChatGate(PostgresGateway):
    async  def __call__(self, chat_id: UUID) -> GetChatMessaesSchema:
        stmt = (
            select(
                ChatModel.id,
                ChatModel.title,
                ChatModel.created_at,
                func.jsonb_agg(
                    func.jsonb_build_object(
                        'id', MessageModel.id,
                        'chat_id', MessageModel.chat_id,
                        'text', MessageModel.text,
                        'created_at', MessageModel.created_at,
                        'updated_at', MessageModel.updated_at,
                        'sender_type_id', MessageModel.sender_type_id
                    )
                ).label('messages')
            ).join(ChatModel, ChatModel.id == MessageModel.chat_id
            )
            .where(ChatModel.id == chat_id)
            .group_by(
                ChatModel.id,
                ChatModel.title,
                ChatModel.created_at
            )
        )

        result = (await self.session.execute(stmt)).mappings().fetchone()
        return GetChatMessaesSchema.model_validate(result)

