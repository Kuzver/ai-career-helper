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
    def dsn(self, db=True) -> str:
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
    # Диагностика: выводим переменные окружения с LIZA
    logger.info("=== Environment variables with LIZA prefix ===")
    for key, value in os.environ.items():
        if 'LIZA' in key:
            logger.info(f"{key}={value}")
    logger.info("==============================================")

    dynaconf = Dynaconf(
        settings_files=['././deploy/configs/config.toml'],
        envvar_prefix='LIZA_API',
        load_dotenv=True,
        environments=True,
    )

    logger.info("Dynaconf settings: %s", dynaconf.to_dict())

    # --- helper для секций с _ ---
    def get_section(name: str):
        return dynaconf.get(f"_{name}") or dynaconf.get(name)

    # ----- API -----
    api_data = dynaconf.get("API") or {
        'host': dynaconf.get('HOST', '0.0.0.0'),
        'port': dynaconf.get('PORT', 8000),
        'project_name': dynaconf.get('PROJECT_NAME', 'base'),
        'cors': dynaconf.get('CORS', ["*"]),
    }
    api = ApiConfig(**api_data)

    # ----- DATABASE -----
    db_section = get_section("DATABASE")
    if not db_section:
        raise RuntimeError(f"Missing DATABASE section: {dynaconf.as_dict()}")

    db_data = {
        "host": db_section.get("HOST"),
        "port": db_section.get("PORT"),
        "username": db_section.get("USERNAME"),
        "password": db_section.get("PASSWORD"),
        "database": db_section.get("DATABASE"),
    }
    if not all(db_data.values()):
        raise RuntimeError(f"Missing DATABASE configuration: {db_data}")
    database = DatabaseConfig(**db_data)

    # ----- REDIS (опционально) -----
    redis_section = get_section("REDIS")
    redis = RedisConfig(**redis_section) if redis_section else None

    # ----- GIGACHAT -----
    gc_section = dynaconf.get("GIGACHAT", {})

    if not gc_section:
        logger.error(
            "GIGACHAT section not found in dynaconf! Available keys: %s",
            list(dynaconf.keys())
        )
        raise RuntimeError("Missing GIGACHAT configuration")

    gigachat = GigachatConfig(**gc_section)

    # ----- JWT -----
    jwt_section = get_section("JWT")
    jwt = JwtConfig(**jwt_section) if jwt_section else JwtConfig()

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