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
    # Диагностика: выводим переменные окружения, начинающиеся с LIZA
    logger.info("=== Environment variables with LIZA prefix ===")
    for key, value in os.environ.items():
        if 'LIZA' in key:
            logger.info(f"{key}={value}")
    logger.info("==============================================")

    dynaconf = Dynaconf(
        settings_files=[
            '././deploy/configs/config.toml'
        ],
        envvar_prefix='LIZA_API',
        load_dotenv=True,
    )

    # Выводим то, что загрузил dynaconf
    logger.info("Dynaconf settings: %s", dynaconf.to_dict())

    # ----- Собираем API config -----
    if 'API' in dynaconf:
        api_data = dynaconf.API
    else:
        # Если API нет, берём верхнеуровневые ключи (как от Render)
        api_data = {
            'host': dynaconf.get('HOST', '0.0.0.0'),
            'port': dynaconf.get('PORT', 8000),
            'project_name': dynaconf.get('PROJECT_NAME', 'base'),
            'cors': dynaconf.get('CORS', ["*"]),
        }
    api = ApiConfig(**api_data)

    # ----- База данных -----
    if 'DATABASE' not in dynaconf:
        logger.error("DATABASE section not found in dynaconf! Available keys: %s", list(dynaconf.keys()))
        raise RuntimeError("Missing DATABASE configuration")
    db_data = dynaconf.DATABASE
    database = DatabaseConfig(**db_data)

    # ----- Redis (опционально) -----
    redis = None
    if 'REDIS' in dynaconf:
        redis = RedisConfig(**dynaconf.REDIS)

    # ----- GigaChat -----
    if 'GIGACHAT' not in dynaconf:
        logger.error("GIGACHAT section not found in dynaconf! Available keys: %s", list(dynaconf.keys()))
        raise RuntimeError("Missing GIGACHAT configuration")
    gc_data = dynaconf.GIGACHAT
    gigachat = GigachatConfig(**gc_data)

    # ----- JWT -----
    if 'JWT' in dynaconf:
        jwt = JwtConfig(**dynaconf.JWT)
    else:
        jwt = JwtConfig()

    cfg = Config(
        api=api,
        database=database,
        redis=redis,
        gigachat=gigachat,
        jwt=jwt,
    )

    if cfg.jwt.secret == _DEFAULT_JWT_SECRET:
        logger.warning(
            "JWT secret не настроен! Используется дефолтное значение. "
            "Задайте jwt.secret в config.toml или переменной окружения LIZA_JWT__SECRET"
        )

    return cfg