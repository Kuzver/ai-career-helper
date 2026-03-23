import uuid
from datetime import datetime, timezone
from sqlalchemy import UUID
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from typing import Annotated
from src.infra.postgres.base import BaseDBModel

uuid_pk = Annotated[uuid.UUID, mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
    )]

created_at = Annotated[datetime, mapped_column(
    DateTime(timezone=True),
    default=func.now(), 
    nullable=False,

)]
updated_at = Annotated[datetime, mapped_column(
    DateTime(timezone=True),
    default=func.now(), 
    nullable=False,

)]

class BaseDBModel(DeclarativeBase):
    __tablename__: str
    __table_args__: dict[str, str] | tuple = {'schema': 'db_schema'}

    @classmethod
    def group_by_fields(cls, exclude: list[str] | None = None) -> list:
        payload = []
        if not exclude:
            exclude = []

        for column in cls.__table__.columns:
            if column.key in exclude:
                continue

            payload.append(column)

        return payload

class UserModel(BaseDBModel):
    __tablename__ = 'users'
    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    corporate_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='user',
        server_default='user',
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class UserCareersModel(BaseDBModel):
    __tablename__ = 'user_careers'
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    specialization_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=True
    )
    specialization: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )
    experience_level: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    skills: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    career_goal: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class UserResumeModel(BaseDBModel):
    __tablename__ = 'user_resume'
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    work_experience: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    skills: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    recomendations: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class SpecializationsModel(BaseDBModel):
    __tablename__ = 'specializations'
    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    '''timestamp'''

class RoadmapsModel(BaseDBModel):
    __tablename__ = 'roadmaps'
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    '''timestamp
    start_date: Mapped[start_date]
    estmated_end_date: Mapped[estmated_end_date]
    DATE'''

class RoadmapStatusModel(BaseDBModel):
    __tablename__ = 'roadmap_status'
    id: Mapped[uuid_pk]
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    '''timestamp'''

class RoadMapStepsModel(BaseDBModel):
    __tablename__ = 'roadmapsteps'
    id: Mapped[uuid_pk]
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    materials: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    deadline: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    '''timestamp'''



class InformationsModel(BaseDBModel):
    __tablename__ = 'informations'
    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class CardsModel(BaseDBModel):
    __tablename__ = 'cards'
    id: Mapped[uuid_pk]
    information_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('db_schema.informations.id'),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class FavoritesModel(BaseDBModel):
    __tablename__ = 'favorites'
    id: Mapped[uuid_pk] = mapped_column(
        UUID,
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('db_schema.users.id'),
        nullable=False
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('db_schema.cards.id'),
        nullable=False
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ChatModel(BaseDBModel):
    __tablename__ = 'chats'
    __table_args__ = {'extend_existing': True, 'schema': 'db_schema'}
    id: Mapped[uuid_pk] 
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('db_schema.users.id'),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime,  
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    last_activity_time: Mapped[datetime] = mapped_column(  
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class MessageModel(BaseDBModel):
    __tablename__ = 'messages'
    id: Mapped[uuid_pk]  
    chat_id: Mapped[uuid.UUID] = mapped_column(  
        ForeignKey('db_schema.chats.id'),
        nullable=False
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    sender_type_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey('db_schema.sender_types.name'),
        nullable=False
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class SenderTypesModel(BaseDBModel):
    __tablename__ = 'sender_types'
    name: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False
    )


class SurveyModel(BaseDBModel):
    __tablename__ = 'surveys'
    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.users.id'), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class SurveyQuestionModel(BaseDBModel):
    __tablename__ = 'survey_questions'
    id: Mapped[uuid_pk]
    survey_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.surveys.id', ondelete='CASCADE'), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False, default='single')
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class SurveyOptionModel(BaseDBModel):
    __tablename__ = 'survey_options'
    id: Mapped[uuid_pk]
    question_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.survey_questions.id', ondelete='CASCADE'), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class SurveyResponseModel(BaseDBModel):
    __tablename__ = 'survey_responses'
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.users.id'), nullable=False)
    survey_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.surveys.id', ondelete='CASCADE'), nullable=False)
    is_validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validation_result: Mapped[str] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class SurveyAnswerModel(BaseDBModel):
    __tablename__ = 'survey_answers'
    id: Mapped[uuid_pk]
    response_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.survey_responses.id', ondelete='CASCADE'), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.survey_questions.id', ondelete='CASCADE'), nullable=False)
    option_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.survey_options.id', ondelete='SET NULL'), nullable=True)
    free_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ArticleCategoryModel(BaseDBModel):
    __tablename__ = 'article_categories'
    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ArticleModel(BaseDBModel):
    __tablename__ = 'articles'
    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.article_categories.id', ondelete='SET NULL'), nullable=True)
    specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class UserRoadmapProgressModel(BaseDBModel):
    __tablename__ = 'user_roadmap_progress'
    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('db_schema.users.id'), nullable=False)
    roadmap_key: Mapped[str] = mapped_column(String(100), nullable=False)
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

