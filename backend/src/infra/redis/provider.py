from collections.abc import AsyncIterator
from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from src.config import RedisConfig
from loguru import logger


class RedisProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def _get_redis_client(self, config: RedisConfig | None) -> AsyncIterator[Redis | None]:
        if config is None:
            logger.warning("Redis configuration is not provided, Redis client will not be available")
            yield None
            return
        
        client: Redis | None = None
        try:
            client = Redis(
                host=config.host,
                port=config.port,
                password=config.password if config.password else None,
                db=config.db,
                decode_responses=config.decode_responses,
            )
            # Проверяем подключение
            await client.ping()
            logger.info(f"Connected to Redis at {config.host}:{config.port}")
            yield client
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            raise
        finally:
            if client is not None:
                await client.aclose()

