from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.presentation.fastapi.routes.core.users.api import ROUTER as USER_ROUTER
from src.presentation.fastapi.routes.core.cards.api import ROUTER as CARD_ROUTER
from src.presentation.fastapi.routes.core.user_careers.api import ROUTER as USER_CAREER_ROUTER
from src.presentation.fastapi.routes.core.messages.api import ROUTER as MESSAGE_ROUTER
from src.presentation.fastapi.routes.core.chats.api import ROUTER as CHAT_ROUTER
from src.presentation.fastapi.routes.core.profile.api import ROUTER as PROFILE_ROUTER
from src.presentation.fastapi.routes.core.export.api import ROUTER as EXPORT_ROUTER
from src.presentation.fastapi.routes.core.surveys.api import ROUTER as SURVEY_ROUTER
from src.presentation.fastapi.routes.core.articles.api import ROUTER as ARTICLE_ROUTER
from src.presentation.fastapi.routes.core.roadmap.api import ROUTER as ROADMAP_ROUTER
from src.presentation.fastapi.routes.core.search.api import ROUTER as SEARCH_ROUTER
from src.presentation.fastapi.routes.core.legal.api import ROUTER as LEGAL_ROUTER

def setup_core_router() -> APIRouter:
    router = APIRouter(route_class=DishkaRoute)

    router.include_router(prefix='/user', router=USER_ROUTER, tags=["Users"])
    router.include_router(prefix='/cards', router=CARD_ROUTER, tags=["Cards"])
    router.include_router(prefix='/user_careers', router=USER_CAREER_ROUTER, tags=["User Careers"])
    router.include_router(prefix='/messages', router=MESSAGE_ROUTER, tags=["Messages"])
    router.include_router(prefix='/chats', router=CHAT_ROUTER, tags=["Chats"])
    router.include_router(prefix='/profile', router=PROFILE_ROUTER, tags=["Profile"])
    router.include_router(prefix='/export', router=EXPORT_ROUTER, tags=["Export"])
    router.include_router(prefix='/surveys', router=SURVEY_ROUTER, tags=["Surveys"])
    router.include_router(prefix='/articles', router=ARTICLE_ROUTER, tags=["Articles"])
    router.include_router(prefix='/roadmap', router=ROADMAP_ROUTER, tags=["Roadmap"])
    router.include_router(prefix='/search', router=SEARCH_ROUTER, tags=["Search"])
    router.include_router(prefix='/legal', router=LEGAL_ROUTER, tags=["Legal"])
    return router
