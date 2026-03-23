from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.presentation.fastapi.routes.core.users.api import ROUTER as USER_ROUTER
from src.presentation.fastapi.routes.core.cards.api import ROUTER as CARD_ROUTER
from src.presentation.fastapi.routes.core.user_careers.api import ROUTER as USER_CAREER_ROUTER
from src.presentation.fastapi.routes.core.messages.api import ROUTER as MESSAGE_ROUTER
from src.presentation.fastapi.routes.core.chats.api import ROUTER as CHAT_ROUTER
from src.presentation.fastapi.routes.core.profile.api import ROUTER as PROFILE_ROUTER
from src.presentation.fastapi.routes.core.export.api import ROUTER as EXPORT_ROUTER

def setup_core_router() -> APIRouter:
    router = APIRouter(route_class=DishkaRoute)

    router.include_router(prefix='/user', router=USER_ROUTER, tags=["Users"])
    router.include_router(prefix='/cards', router=CARD_ROUTER, tags=["Cards"])
    router.include_router(prefix='/user_careers', router=USER_CAREER_ROUTER, tags=["User Careers"])
    router.include_router(prefix='/messages', router=MESSAGE_ROUTER, tags=["Messages"])
    router.include_router(prefix='/chats', router=CHAT_ROUTER, tags=["Chats"])
    router.include_router(prefix='/profile', router=PROFILE_ROUTER, tags=["Profile"])
    router.include_router(prefix='/export', router=EXPORT_ROUTER, tags=["Export"])
    return router
