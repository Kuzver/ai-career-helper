from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime, timezone

from src.infra.postgres.tables import ChatModel, UserModel
from src.application.schemas.chat import CreateChatRequest, RawChatWithMessages
from src.application.schemas.auth import AuthSchema


class CreateChatUsecase:
    def __init__(self, session: AsyncSession, auth: AuthSchema):
        self.session = session
        self.auth = auth

    async def __call__(self, request: CreateChatRequest) -> RawChatWithMessages:
        now = datetime.now(timezone.utc)

        # Ensure user exists in DB (FK constraint)
        user_result = await self.session.execute(
            select(UserModel).where(UserModel.id == self.auth.id)
        )
        if not user_result.scalar_one_or_none():
            self.session.add(UserModel(
                id=self.auth.id,
                email="dev@test.com",
                first_name="Dev",
                is_active=True,
            ))
            await self.session.flush()

        chat_id = uuid4()
        self.session.add(ChatModel(
            id=chat_id,
            user_id=self.auth.id,
            title=request.title,
            start_time=now,
            last_activity_time=now,
            created_at=now,
            updated_at=now,
        ))

        await self.session.flush()
        await self.session.commit()

        return RawChatWithMessages(
            id=chat_id,
            title=request.title,
            created_at=now,
            messages=[],
        )
