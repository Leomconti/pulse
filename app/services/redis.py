from redis.asyncio import ConnectionPool, Redis

from app.config import cache_config


def create_async_connection_pool() -> ConnectionPool:
    return ConnectionPool.from_url(
        url=cache_config.REDIS_URL,
        decode_responses=True,
    )


async_pool = create_async_connection_pool()


def get_redis() -> Redis:
    return Redis(connection_pool=async_pool)


redis = get_redis()


async def ping_redis():
    redis = get_redis()
    await redis.ping()
