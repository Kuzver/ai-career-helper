import os
from pydantic import ConfigDict
from dynaconf import Dynaconf
from loguru import logger

from src.application.schemas.common import BaseSchema


class ApiConfig(BaseSchema):
    host: str = 'localhost'
    port: int = 8000
    project_name: str = 'base'
    cors: list[str] = ["*"]

class DatabaseConfig(BaseSchema):
    host: str
    port: int
    username: str
    password: str
    database: str
    driver: str = 'postgresql+psycopg_async'

    @property
    def dsn(self, db = True) -> str:
        return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'

class RedisConfig(BaseSchema):
    host: str = 'localhost'
    port: int = 6379
    password: str | None = None
    db: int = 0
    decode_responses: bool = True

class GigachatConfig(BaseSchema):
    client_id: str
    scope: str
    authorization_key: str

_DEFAULT_JWT_SECRET = "ai-career-helper-jwt-secret-key-change-in-production"


class JwtConfig(BaseSchema):
    secret: str = _DEFAULT_JWT_SECRET
    expire_days: int = 7

class Config(BaseSchema):
    model_config = ConfigDict(extra='allow', from_attributes=True)
    api: ApiConfig
    database: DatabaseConfig
    redis: RedisConfig | None = None
    gigachat: GigachatConfig
    jwt: JwtConfig = JwtConfig()


def get_config() -> Config:
    dynaconf = Dynaconf(
        settings_files=[
            '././deploy/configs/config.toml'
        ],
        envvar_prefix='Liza',
        load_dotenv=True,
    )
    logger.info(dynaconf.api)
    cfg = Config.model_validate(dynaconf)

    if cfg.jwt.secret == _DEFAULT_JWT_SECRET:
        logger.warning(
            "JWT secret не настроен! Используется дефолтное значение. "
            "Задайте jwt.secret в config.toml или переменной окружения LIZA_JWT__SECRET"
        )

    return cfg