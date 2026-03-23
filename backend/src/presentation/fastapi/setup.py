from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi import FastAPI
from src.config import Config
from src.presentation.fastapi.routes.core.setup import setup_core_router
from src.presentation.fastapi.routes.auth.register import ROUTER as AUTH_ROUTER
from src.presentation.fastapi.routes.admin.surveys import ROUTER as ADMIN_SURVEY_ROUTER
from src.presentation.fastapi.routes.admin.articles import ROUTER as ADMIN_ARTICLE_ROUTER
from src.presentation.fastapi.routes.admin.users import ROUTER as ADMIN_USERS_ROUTER
from src.presentation.fastapi.exception_handlers import setup_exception_handlers

def setup_routes(app: FastAPI, config: Config) -> None:
    router = APIRouter(prefix='/api', route_class=DishkaRoute)
    router.include_router(router=setup_core_router())
    router.include_router(prefix='/auth', router=AUTH_ROUTER, tags=["Auth"])
    router.include_router(prefix='/admin/surveys', router=ADMIN_SURVEY_ROUTER, tags=["Admin Surveys"])
    router.include_router(prefix='/admin/articles', router=ADMIN_ARTICLE_ROUTER, tags=["Admin Articles"])
    router.include_router(prefix='/admin/users', router=ADMIN_USERS_ROUTER, tags=["Admin Users"])

    app.include_router(router)
    setup_exception_handlers(app=app)
    
