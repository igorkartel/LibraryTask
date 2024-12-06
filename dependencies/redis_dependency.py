from brokers.redis import get_redis_client


async def get_redis_connection():
    redis = await get_redis_client()
    try:
        yield redis
    finally:
        await redis.close()
