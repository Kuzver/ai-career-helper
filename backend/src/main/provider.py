from dishka import Provider
from dishka import Scope
from dishka import from_context
from dishka import provide
from dishka import provide_all
from fastapi import Request
from src.usecase.chats.get_all import GetAllChatUsecase
from src.usecase.chats.get_by_id import GetChatByIdUsecase

from src.config import Config
from src.config import ApiConfig
from src.config import DatabaseConfig
from src.config import RedisConfig
from src.config import GigachatConfig

from src.usecase.users.create import CreateUserUsecase
from src.usecase.cards.delete import DeleteCardUsecase
from src.usecase.cards.update import UpdateCardUsecase
from src.usecase.user_careers.create import CreateUserCareerUsecase
from src.usecase.cards.get_all import GetAllCardsUsecase
from src.usecase.cards.create import CreateCardsUsecase
from src.usecase.cards.generate import GenerateCardsUsecase
from src.usecase.message.create import MessengerUsecase
from src.usecase.chats.create import CreateChatUsecase
from src.usecase.chats.get import GetChatUsecase
from src.usecase.chats.get_all import GetAllChatUsecase
from src.usecase.systems.pagination import Pagination

class MainProvider(Provider):
    scope = Scope.REQUEST

    _provide_config = from_context(provides=Config, scope=Scope.APP) 

    @provide(scope=Scope.APP)
    async def _get_api_config(self, config: Config) -> ApiConfig:
        return config.api
    
    @provide(scope=Scope.APP)
    async def _get_database_config(self, config: Config) -> DatabaseConfig:
        return config.database
    
    @provide(scope=Scope.APP)
    async def _get_redis_config(self, config: Config) -> RedisConfig | None:
        return config.redis


    @provide(scope=Scope.APP)
    async def _get_gigachat_config(self, config: Config) -> GigachatConfig | None:
        return config.gigachat
    _request = from_context(provides=Request, scope=Scope.REQUEST)

    _get_usecases = provide_all(
        CreateUserUsecase,
        DeleteCardUsecase,
        UpdateCardUsecase,
        CreateUserCareerUsecase,
        GetAllCardsUsecase,
        CreateCardsUsecase,
        GenerateCardsUsecase,
        #MessengerUsecase,
        CreateChatUsecase,
        GetChatUsecase,
        Pagination,
        GetAllChatUsecase,
        CreateChatUsecase,
        GetChatByIdUsecase
    )

