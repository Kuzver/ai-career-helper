from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter
from fastapi import status, HTTPException
from src.application.schemas.cards import CardSchema
from src.usecase.cards.delete import DeleteCardUsecase
from src.usecase.cards.schemas import GetUpdateCardsSchema
from src.usecase.cards.update import UpdateCardUsecase
from src.usecase.cards.generate import GenerateCardsUsecase

import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.application.schemas.auth import AuthSchema
from src.infra.postgres.tables import UserCareersModel
from src.application.schemas.cards import GeneratedCardsResponse
from src.infra.gigachat.chat import Gigachat

from src.usecase.cards.get_all import GetAllCardsUsecase
from src.usecase.cards.schemas import PaginationSchema, ResponseCardsSchema
from src.usecase.cards.create import CreateCardsUsecase
from src.usecase.cards.schemas import CreateManyCardsSchema
from uuid import UUID

ROUTER = APIRouter(route_class=DishkaRoute, )

@ROUTER.delete('', status_code=status.HTTP_200_OK)
async def delete_cards(
    usecase: FromDishka[DeleteCardUsecase],
    id: UUID) -> CardSchema:
    return await usecase(id)

@ROUTER.get('', status_code=status.HTTP_200_OK)
async def get_cards(
    usecase: FromDishka[GetAllCardsUsecase],
    limit: int,
    offset:int) -> ResponseCardsSchema:
    return await usecase(PaginationSchema(limit=limit, offset=offset))

@ROUTER.put('', status_code=status.HTTP_200_OK)
async def update_card(
    usecase: FromDishka[UpdateCardUsecase],
    card: GetUpdateCardsSchema) -> CardSchema:
    return await usecase(card)

@ROUTER.post('', status_code=status.HTTP_200_OK)
async def create_cards(
    usecase: FromDishka[CreateCardsUsecase],
    cards: CreateManyCardsSchema
) -> list[CardSchema]:
    return await usecase(cards.cards)

@ROUTER.post('/generate', status_code=status.HTTP_200_OK)
async def generate_cards(
    usecase: FromDishka[GenerateCardsUsecase],
) -> list[CardSchema]:
    return await usecase()

@ROUTER.get('/recommendations', response_model=GeneratedCardsResponse)
async def get_ai_recommendations(
    auth: FromDishka[AuthSchema],
    db: FromDishka[AsyncSession],
    gigachat: FromDishka[Gigachat]
):
    query = select(UserCareersModel).where(UserCareersModel.user_id == auth.id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден. Сначала заполните данные о карьере, чтобы я мог подобрать карточки под ваши предпочтения.")

    user_query = (
        "Ты — генератор коротких кнопок-подсказок для IT-карьерного чата. "
        "Сгенерируй 6 карточек на основе профиля пользователя. "
        "ПРАВИЛА:\n"
        "1. title: Только ПРЯМАЯ ПРОСЬБА пользователя к ИИ (например: 'Составь мне roadmap', 'Проверь моё резюме').\n"
        "2. description: Очень коротко (2-4 слова), поясняющее суть (например: 'План обучения', 'Анализ навыков').\n"
        "3. tag: Одно слово (например: 'обучение', 'карьера', 'резюме').\n\n"
        "ПРИМЕР ВЫХОДА:\n"
        "{"
        "  \"cards\": [\n"
        "    {\"title\": \"Составь мне план обучения по Machine Learning\", \"description\": \"Персонализированный учебный план\", \"tag\": \"обучение\"}\n"
        "  ]\n"
        "}\n"
        "Верни ответ СТРОГО в формате JSON без лишних слов."
    )

    user_context = (
        f"Специализация: {profile.specialization or 'Не указана'}\n"
        f"Уровень: {profile.experience_level or 'Не указан'}\n"
        f"Навыки: {profile.skills or 'Не указаны'}\n"
        f"Цель: {profile.career_goal or 'Не указана'}"
    )

    response_text = await gigachat(user_query=user_query, user_context=user_context)

    try:
        cleaned_text = response_text.strip("` \n")
        if cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
            
        parsed_data = json.loads(cleaned_text)
        return GeneratedCardsResponse(**parsed_data)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка генерации карточек. Попробуйте еще раз.")