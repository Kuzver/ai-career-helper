# Фаза 1: Фундамент — План реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Стабилизировать проект — перенести профиль пользователя из localStorage в БД, исправить критические баги авторизации, добавить систему ролей, перенести формирование контекста бота на бэкенд.

**Architecture:** Расширяем существующую Clean Architecture: новая Alembic-миграция для полей `role` и `name` в `users`, новые API-эндпоинты профиля (`/api/profile`), обновлённый системный промпт GigaChat с контекстом пользователя из БД, фронтенд переходит с localStorage на API-вызовы.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (async), Alembic, Dishka DI, React 19, React Router 7, Axios, Tailwind CSS 4.1

---

## Структура файлов

### Backend — создать:
- `backend/src/infra/postgres/migration/versions/2026-03-23_add_role_and_profile_fields.py` — миграция: role в users, name в user_careers
- `backend/src/presentation/fastapi/routes/core/profile/api.py` — эндпоинты GET/PUT профиля
- `backend/src/usecase/profile/get.py` — usecase получения профиля
- `backend/src/usecase/profile/update.py` — usecase обновления профиля
- `backend/src/application/schemas/profile.py` — Pydantic-схемы профиля

### Backend — изменить:
- `backend/src/infra/postgres/tables.py` — добавить role в UserModel, name в UserCareersModel
- `backend/src/infra/auth/provider.py` — убрать anonymous fallback, кидать 401
- `backend/src/infra/gigachat/chat.py` — обновить системный промпт, принимать user_context
- `backend/src/infra/gigachat/agents/orchestrator.py` — прокидывать контекст
- `backend/src/usecase/message/create.py` — подгружать профиль, передавать контекст
- `backend/src/main/provider.py` — зарегистрировать новые usecase'ы
- `backend/src/presentation/fastapi/routes/core/setup.py` — подключить profile router
- `backend/src/presentation/fastapi/routes/auth/register.py` — устанавливать role='user' при регистрации

### Frontend — изменить:
- `frontend/app/modules/user/lib/use-user.tsx` — убрать localStorage профиля, загрузка с API
- `frontend/app/pages/profile.tsx` — сохранение через API
- `frontend/app/pages/chat.tsx` — убрать костыль с `[Контекст пользователя: ...]`
- `frontend/app/shared/api/axios-client.ts` — добавить interceptor на 401
- `frontend/app/shared/components/ui/app-layout.tsx` — убрать нерабочие search и notification

---

## Task 1: Alembic-миграция — role в users, расширение user_careers

**Files:**
- Create: `backend/src/infra/postgres/migration/versions/2026-03-23_add_role_and_profile_fields.py`
- Modify: `backend/src/infra/postgres/tables.py`

- [ ] **Step 1: Добавить поле role в UserModel**

В `backend/src/infra/postgres/tables.py`, после `is_active`:

```python
role: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    default='user',
    server_default='user',
)
```

- [ ] **Step 2: Добавить поле name в UserCareersModel**

В `backend/src/infra/postgres/tables.py`, в `UserCareersModel` после `user_id`:

```python
name: Mapped[str] = mapped_column(
    String(255),
    nullable=True,
)
```

- [ ] **Step 3: Создать Alembic-миграцию**

```python
"""add role to users, name to user_careers

Revision ID: c2a3b4d5e6f7
Revises: b1f2c3d4e5f6
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c2a3b4d5e6f7"
down_revision: Union[str, None] = "b1f2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        schema="db_schema",
    )
    op.add_column(
        "user_careers",
        sa.Column("name", sa.String(255), nullable=True),
        schema="db_schema",
    )


def downgrade() -> None:
    op.drop_column("user_careers", "name", schema="db_schema")
    op.drop_column("users", "role", schema="db_schema")
```

- [ ] **Step 4: Коммит**

```bash
git add backend/src/infra/postgres/tables.py backend/src/infra/postgres/migration/versions/2026-03-23_add_role_and_profile_fields.py
git commit -m "Миграция: role в users, name в user_careers"
```

---

## Task 2: Схемы и usecase'ы профиля

**Files:**
- Create: `backend/src/application/schemas/profile.py`
- Create: `backend/src/usecase/profile/__init__.py`
- Create: `backend/src/usecase/profile/get.py`
- Create: `backend/src/usecase/profile/update.py`

- [ ] **Step 1: Создать Pydantic-схемы профиля**

`backend/src/application/schemas/profile.py`:

```python
from pydantic import BaseModel


class ProfileResponse(BaseModel):
    name: str | None = None
    specialization: str | None = None
    experience_level: str | None = None
    skills: str | None = None
    career_goal: str | None = None


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    specialization: str | None = None
    experience_level: str | None = None
    skills: str | None = None
    career_goal: str | None = None
```

- [ ] **Step 2: Создать usecase получения профиля**

`backend/src/usecase/profile/get.py`:

```python
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
            specialization=str(career.specialization_id) if career.specialization_id else None,
            experience_level=career.experience_level,
            skills=career.skills,
            career_goal=career.career_goal,
        )
```

- [ ] **Step 3: Создать usecase обновления профиля**

`backend/src/usecase/profile/update.py`:

Логика: если запись `user_careers` существует — обновить, иначе — создать.
Поле `specialization_id` хранит UUID, но фронт отправляет строку (slug). Для простоты сохраняем slug как строку в поле `name` для specialization, а `specialization_id` ставим фиктивный UUID. TODO: привести в порядок в фазе 4.

```python
from dataclasses import dataclass
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.profile import ProfileUpdateRequest, ProfileResponse
from src.infra.postgres.tables import UserCareersModel


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileUsecase:
    session: AsyncSession

    async def __call__(self, user_id: UUID, data: ProfileUpdateRequest) -> ProfileResponse:
        async with self.session.begin():
            result = await self.session.execute(
                select(UserCareersModel).where(UserCareersModel.user_id == user_id)
            )
            career = result.scalar_one_or_none()

            if career:
                if data.name is not None:
                    career.name = data.name
                if data.experience_level is not None:
                    career.experience_level = data.experience_level
                if data.skills is not None:
                    career.skills = data.skills
                if data.career_goal is not None:
                    career.career_goal = data.career_goal
                if data.specialization is not None:
                    career.specialization_id = uuid4()
                    career.name = data.name
            else:
                career = UserCareersModel(
                    id=uuid4(),
                    user_id=user_id,
                    name=data.name,
                    specialization_id=uuid4(),
                    experience_level=data.experience_level or "",
                    skills=data.skills,
                    career_goal=data.career_goal,
                )
                self.session.add(career)

        return ProfileResponse(
            name=career.name,
            specialization=data.specialization,
            experience_level=career.experience_level,
            skills=career.skills,
            career_goal=career.career_goal,
        )
```

- [ ] **Step 4: Создать `__init__.py`**

```bash
touch backend/src/usecase/profile/__init__.py
```

- [ ] **Step 5: Коммит**

```bash
git add backend/src/application/schemas/profile.py backend/src/usecase/profile/
git commit -m "Usecase'ы и схемы профиля пользователя"
```

---

## Task 3: API-эндпоинты профиля + DI-регистрация

**Files:**
- Create: `backend/src/presentation/fastapi/routes/core/profile/__init__.py`
- Create: `backend/src/presentation/fastapi/routes/core/profile/api.py`
- Modify: `backend/src/main/provider.py`
- Modify: `backend/src/presentation/fastapi/routes/core/setup.py`

- [ ] **Step 1: Создать API-роутер профиля**

`backend/src/presentation/fastapi/routes/core/profile/api.py`:

```python
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.application.schemas.auth import AuthSchema
from src.application.schemas.profile import ProfileResponse, ProfileUpdateRequest
from src.usecase.profile.get import GetProfileUsecase
from src.usecase.profile.update import UpdateProfileUsecase

ROUTER = APIRouter(route_class=DishkaRoute)


@ROUTER.get("", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def get_profile(
    auth: FromDishka[AuthSchema],
    usecase: FromDishka[GetProfileUsecase],
) -> ProfileResponse:
    return await usecase(user_id=auth.id)


@ROUTER.put("", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def update_profile(
    auth: FromDishka[AuthSchema],
    usecase: FromDishka[UpdateProfileUsecase],
    body: ProfileUpdateRequest,
) -> ProfileResponse:
    return await usecase(user_id=auth.id, data=body)
```

- [ ] **Step 2: Зарегистрировать usecase'ы в MainProvider**

В `backend/src/main/provider.py` добавить импорты и usecase'ы в `provide_all`:

```python
from src.usecase.profile.get import GetProfileUsecase
from src.usecase.profile.update import UpdateProfileUsecase
```

Добавить `GetProfileUsecase` и `UpdateProfileUsecase` в `_get_usecases = provide_all(...)`.

- [ ] **Step 3: Подключить profile router в setup**

В `backend/src/presentation/fastapi/routes/core/setup.py`:

```python
from src.presentation.fastapi.routes.core.profile.api import ROUTER as PROFILE_ROUTER
```

И в `setup_core_router()`:

```python
router.include_router(prefix='/profile', router=PROFILE_ROUTER, tags=["Profile"])
```

- [ ] **Step 4: Создать `__init__.py`**

```bash
touch backend/src/presentation/fastapi/routes/core/profile/__init__.py
```

- [ ] **Step 5: Коммит**

```bash
git add backend/src/presentation/fastapi/routes/core/profile/ backend/src/main/provider.py backend/src/presentation/fastapi/routes/core/setup.py
git commit -m "API профиля: GET/PUT /api/profile"
```

---

## Task 4: Исправить AuthProvider — убрать anonymous fallback

**Files:**
- Modify: `backend/src/infra/auth/provider.py`
- Modify: `backend/src/presentation/fastapi/routes/auth/register.py`

- [ ] **Step 1: AuthProvider возвращает 401 вместо anonymous**

Заменить содержимое `backend/src/infra/auth/provider.py`:

```python
from dishka import Provider, provide, Scope
from fastapi import Request, HTTPException, status
from loguru import logger

from src.application.schemas.auth import AuthSchema
from src.config import JwtConfig
from src.infra.auth.jwt import verify_token


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_auth(self, request: Request, jwt_config: JwtConfig) -> AuthSchema:
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется авторизация",
            )

        token = auth_header[7:]
        try:
            data = verify_token(token, jwt_config.secret)
            return AuthSchema(id=data["sub"], email=data.get("email", ""))
        except ValueError as e:
            logger.warning(f"Invalid JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен",
            )
```

- [ ] **Step 2: register.py — установить role='user' при регистрации**

В `backend/src/presentation/fastapi/routes/auth/register.py`, в `register_user`, при создании `UserModel`:

```python
user = UserModel(
    id=user_id,
    email=body.email,
    password_hash=hash_password(body.password),
    first_name=body.first_name,
    is_active=True,
    role="user",
)
```

- [ ] **Step 3: Коммит**

```bash
git add backend/src/infra/auth/provider.py backend/src/presentation/fastapi/routes/auth/register.py
git commit -m "Исправлен AuthProvider: 401 вместо anonymous fallback"
```

---

## Task 5: Контекст бота на бэкенде

**Files:**
- Modify: `backend/src/infra/gigachat/chat.py`
- Modify: `backend/src/infra/gigachat/agents/orchestrator.py`
- Modify: `backend/src/usecase/message/create.py`

- [ ] **Step 1: Обновить Gigachat — принимать user_context**

Заменить содержимое `backend/src/infra/gigachat/chat.py`:

```python
from typing import Dict, List, Optional
from gigachat import GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger

BASE_SYSTEM_PROMPT = (
    "Ты — ИИ-помощник по карьере и обучению в IT. "
    "Ты помогаешь пользователям с карьерными вопросами: составление резюме, "
    "подготовка к собеседованиям, построение карьерного пути, выбор технологий, "
    "план обучения, roadmap развития, поиск работы и вакансий.\n\n"
    "СТРОГИЕ ПРАВИЛА:\n"
    "1. Отвечай ТОЛЬКО на вопросы, связанные с карьерой, обучением, IT, "
    "программированием, профессиональным развитием.\n"
    "2. Если вопрос НЕ относится к этим темам — вежливо откажи и перечисли, "
    "чем ты можешь помочь:\n"
    "   - Составление и анализ резюме\n"
    "   - Подготовка к собеседованиям\n"
    "   - Построение карьерного пути и roadmap\n"
    "   - Рекомендации по обучению и курсам\n"
    "   - Объяснение технических концепций\n"
    "   - Советы по поиску работы\n"
    "3. Будь конкретным и полезным. Давай экспертные советы.\n"
    "4. Форматируй ответы в Markdown для удобства чтения."
)


class Gigachat:
    def __init__(self) -> None:
        self.model = GigaChatAsyncClient(
            credentials=config.gigachat.authorization_key,
            verify_ssl_certs=False,
        )

    async def __call__(
        self,
        user_query: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[str] = None,
    ) -> str:
        system_prompt = BASE_SYSTEM_PROMPT
        if user_context:
            system_prompt += f"\n\nИнформация о пользователе:\n{user_context}"

        messages = [Messages(role=MessagesRole.SYSTEM, content=system_prompt)]

        if history:
            for msg in history[-10:]:
                role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg["content"]))

        messages.append(Messages(role=MessagesRole.USER, content=user_query))

        resp = await self.model.achat(Chat(messages=messages))
        return resp.choices[0].message.content
```

- [ ] **Step 2: Обновить OrchestratorAgent — прокидывать user_context**

В `backend/src/infra/gigachat/agents/orchestrator.py`:

Добавить параметр `user_context: str | None = None` в `__call__`, прокинуть его в агенты.

Изменить сигнатуру:
```python
async def __call__(self, data: RequestMessageSchema, user_context: str | None = None) -> str:
```

Прокинуть `user_context` в вызовы `career_agent` и `learning_agent`.

**Примечание:** CareerAgent и LearningAgent тоже потребуют аналогичного изменения — добавить `user_context` параметр, прокинуть в `Gigachat.__call__`. Это задача для отдельного step.

- [ ] **Step 3: Обновить агенты career и learning — принимать user_context**

В `backend/src/infra/gigachat/agents/career.py` и `backend/src/infra/gigachat/agents/learning.py`:
- Добавить `user_context: str | None = None` в `__call__`
- Прокидывать `user_context=user_context` во все вызовы `self.gigachat()`

- [ ] **Step 4: Обновить MessengerUsecase — подгружать профиль**

В `backend/src/usecase/message/create.py`:

```python
from multiprocessing.connection import answer_challenge
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
        # Подгружаем профиль пользователя для контекста бота
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
```

- [ ] **Step 5: Коммит**

```bash
git add backend/src/infra/gigachat/ backend/src/usecase/message/create.py
git commit -m "Контекст бота формируется на бэкенде из профиля в БД"
```

---

## Task 6: Фронтенд — профиль через API вместо localStorage

**Files:**
- Modify: `frontend/app/modules/user/lib/use-user.tsx`
- Modify: `frontend/app/pages/profile.tsx`

- [ ] **Step 1: Добавить API-функции профиля**

Создать `frontend/app/modules/user/api/profile.ts`:

```typescript
import { baseClient } from "~/shared/api/axios-client"

export type ProfileData = {
  name: string | null
  specialization: string | null
  experienceLevel: string | null
  skills: string | null
  careerGoal: string | null
}

export async function getProfile(): Promise<ProfileData> {
  const { data } = await baseClient.get<ProfileData>("/api/profile")
  return data
}

export async function updateProfile(profile: {
  name?: string | null
  specialization?: string | null
  experience_level?: string | null
  skills?: string | null
  career_goal?: string | null
}): Promise<ProfileData> {
  const { data } = await baseClient.put<ProfileData>("/api/profile", profile)
  return data
}
```

- [ ] **Step 2: Обновить useUser — убрать localStorage для профиля**

В `frontend/app/modules/user/lib/use-user.tsx`:
- Убрать `PROFILE_KEY`, `getProfile` из localStorage, `saveProfile` в localStorage
- Убрать `getProfileContext` (контекст теперь формируется на бэке)
- Оставить только auth-функции: `user`, `setUser`, `logout`, `getToken`

```typescript
import { useCallback, useContext } from "react"
import { UserContext } from "../ui/user-context"

export const useUser = () => {
  const { user, setUser } = useContext(UserContext)

  const logout = useCallback(() => {
    setUser({ isAuthorized: false })
  }, [setUser])

  const getToken = useCallback((): string | null => {
    return user.token ?? null
  }, [user.token])

  return { user, setUser, logout, getToken }
}
```

- [ ] **Step 3: Обновить profile.tsx — загрузка/сохранение через API**

Переписать `frontend/app/pages/profile.tsx`:
- `useEffect` → вызов `getProfile()` при монтировании
- `handleSave` → вызов `updateProfile()`
- Маппинг camelCase ↔ snake_case для API
- Состояние загрузки и ошибок

- [ ] **Step 4: Коммит**

```bash
git add frontend/app/modules/user/ frontend/app/pages/profile.tsx
git commit -m "Профиль: загрузка и сохранение через API вместо localStorage"
```

---

## Task 7: Фронтенд — убрать костыль контекста из чата

**Files:**
- Modify: `frontend/app/pages/chat.tsx`

- [ ] **Step 1: Убрать вклеивание контекста в текст сообщения**

В `frontend/app/pages/chat.tsx`:
- Убрать `import { useUser }` (если не нужен для auth-проверки) или оставить только `user`
- Убрать `getProfileContext` из деструктуризации
- Убрать переменную `profileCtx` и `enrichedText`
- Отправлять просто `text` вместо `enrichedText` в `sendMessage`
- Функция `cleanUserText` больше не нужна — убрать
- В `MessageBubble` отображать `msg.text` напрямую, без `cleanUserText`

- [ ] **Step 2: Коммит**

```bash
git add frontend/app/pages/chat.tsx
git commit -m "Убран костыль вклеивания контекста в текст сообщения"
```

---

## Task 8: Фронтенд — interceptor на 401, fix нерабочих элементов

**Files:**
- Modify: `frontend/app/shared/api/axios-client.ts`
- Modify: `frontend/app/shared/components/ui/app-layout.tsx`

- [ ] **Step 1: Добавить response interceptor на 401**

В `frontend/app/shared/api/axios-client.ts`, после request interceptor:

```typescript
baseClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth")
      window.location.href = "/sign-in"
    }
    return Promise.reject(error)
  }
)
```

- [ ] **Step 2: Убрать нерабочие search и notification из app-layout**

В `frontend/app/shared/components/ui/app-layout.tsx`:
- Убрать search input из header
- Убрать notification button
- Оставить header с аватаром профиля

Header становится:
```tsx
<header className="flex items-center justify-end gap-4 border-b border-gray-100 px-6 py-3">
  <Link to="/profile" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200">
    <img src="/icons/icon profile.svg" alt="" className="h-5 w-5 opacity-50" />
  </Link>
</header>
```

- [ ] **Step 3: Коммит**

```bash
git add frontend/app/shared/api/axios-client.ts frontend/app/shared/components/ui/app-layout.tsx
git commit -m "Interceptor на 401, убраны нерабочие search и notification"
```

---

## Task 9: Миграция данных из localStorage (одноразовая)

**Files:**
- Modify: `frontend/app/pages/profile.tsx`

- [ ] **Step 1: Добавить одноразовую миграцию в profile.tsx**

При монтировании компонента профиля:
1. Проверить `localStorage.getItem("user_profile")`
2. Если есть данные и API вернул пустой профиль → отправить PUT с данными из localStorage
3. После успешной миграции → `localStorage.removeItem("user_profile")`

```typescript
// В useEffect после загрузки профиля
if (!profile.name && !profile.specialization) {
  const raw = localStorage.getItem("user_profile")
  if (raw) {
    try {
      const local = JSON.parse(raw)
      await updateProfile({
        name: local.name || null,
        specialization: local.specialization || null,
        experience_level: local.experience || null,
        skills: local.skills || null,
        career_goal: local.careerGoal || null,
      })
      localStorage.removeItem("user_profile")
      // перезагрузить профиль
    } catch {}
  }
}
```

- [ ] **Step 2: Коммит**

```bash
git add frontend/app/pages/profile.tsx
git commit -m "Одноразовая миграция профиля из localStorage в БД"
```

---

## Порядок выполнения

```
Task 1 (миграция БД)
  ↓
Task 2 (схемы + usecase'ы)
  ↓
Task 3 (API эндпоинты + DI)
  ↓
Task 4 (AuthProvider fix)
  ↓
Task 5 (контекст бота)
  ↓
Task 6 (фронт: профиль через API) — зависит от Task 3
  ↓
Task 7 (фронт: убрать костыль) — зависит от Task 5
  ↓
Task 8 (фронт: 401 interceptor) — зависит от Task 4
  ↓
Task 9 (миграция localStorage) — зависит от Task 6
```
