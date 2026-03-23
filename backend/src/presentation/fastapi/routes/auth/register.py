from uuid import uuid4, UUID
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from src.infra.auth.jwt import hash_password, verify_password, create_token
from src.infra.postgres.tables import UserModel, ChatModel, MessageModel
from src.config import JwtConfig


WELCOME_CHATS = [
    {
        "title": "Построение карьерного roadmap",
        "messages": [
            ("user", "Помоги мне составить план развития в IT"),
            ("chat", "Отличный первый шаг! Чтобы составить персональный roadmap, мне нужно узнать о вас больше.\n\n"
             "Ответьте на несколько вопросов:\n\n"
             "1. **Какое направление** вас интересует? (frontend, backend, fullstack, data science, devops)\n"
             "2. **Какой у вас текущий уровень?** (новичок, junior, middle)\n"
             "3. **Сколько времени** вы готовы уделять обучению в неделю?\n"
             "4. **Какие технологии** вы уже знаете?\n\n"
             "На основе ваших ответов я составлю подробный план с этапами, сроками и ресурсами."),
        ],
    },
    {
        "title": "Помощь с резюме",
        "messages": [
            ("user", "Хочу составить или улучшить резюме"),
            ("chat", "Буду рад помочь с резюме! Вот что я могу:\n\n"
             "- **Составить резюме с нуля** — расскажите о вашем опыте, навыках и целях\n"
             "- **Проанализировать готовое** — загрузите PDF или DOCX файл через кнопку 📎\n"
             "- **Адаптировать под вакансию** — пришлите описание вакансии\n\n"
             "С чего начнём? Если хотите составить с нуля, расскажите:\n"
             "- На какую позицию претендуете?\n"
             "- Какой у вас опыт работы?\n"
             "- Какие ключевые навыки?"),
        ],
    },
    {
        "title": "Подготовка к собеседованию",
        "messages": [
            ("user", "Как подготовиться к техническому собеседованию?"),
            ("chat", "Подготовка к собеседованию — это системный процесс. Вот мой план:\n\n"
             "### За 2-4 недели:\n"
             "- Решайте алгоритмические задачи (LeetCode Easy → Medium)\n"
             "- Повторите основы вашего стека\n\n"
             "### За 1 неделю:\n"
             "- Изучите компанию и продукт\n"
             "- Подготовьте рассказ о себе (2 минуты)\n"
             "- Подготовьте 3-5 вопросов к интервьюеру\n\n"
             "### В день собеседования:\n"
             "- Уточняйте задачу перед решением\n"
             "- Думайте вслух — интервьюер оценивает процесс мышления\n\n"
             "Хотите потренироваться? Скажите на какую позицию и стек — я сгенерирую вопросы!"),
        ],
    },
]


async def create_welcome_chats(session: AsyncSession, user_id: UUID) -> None:
    try:
        now = datetime.now(timezone.utc)
        for chat_data in WELCOME_CHATS:
            chat_id = uuid4()
            session.add(ChatModel(
                id=chat_id, user_id=user_id, title=chat_data["title"],
                start_time=now, last_activity_time=now,
            ))
            await session.flush()

            for sender, text in chat_data["messages"]:
                session.add(MessageModel(
                    id=uuid4(), chat_id=chat_id, text=text, sender_type_id=sender,
                ))
            await session.flush()
    except Exception as e:
        logger.error(f"Welcome chats error: {e}")

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register_user(
    body: RegisterRequest,
    session: FromDishka[AsyncSession],
    jwt_config: FromDishka[JwtConfig],
):
    result = await session.execute(
        select(UserModel).where(UserModel.email == body.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        is_active=True,
        role="user",
    )
    session.add(user)
    await session.flush()

    await create_welcome_chats(session, user_id)
    await session.commit()

    token = create_token(user_id, body.email, jwt_config.secret, jwt_config.expire_days)
    return TokenResponse(token=token, user_id=str(user_id), email=body.email)


@ROUTER.post("/login", response_model=TokenResponse)
async def login_user(
    body: LoginRequest,
    session: FromDishka[AsyncSession],
    jwt_config: FromDishka[JwtConfig],
):
    result = await session.execute(
        select(UserModel).where(UserModel.email == body.email)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    token = create_token(user.id, user.email, jwt_config.secret, jwt_config.expire_days)
    return TokenResponse(token=token, user_id=str(user.id), email=user.email)
