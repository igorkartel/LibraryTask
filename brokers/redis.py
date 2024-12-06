import redis.asyncio as aioredis
from fastapi import HTTPException, status

from configs.logger import logger
from configs.settings import settings


async def get_redis_client():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True
    )
    return redis


async def add_refresh_token_to_blacklist(redis: aioredis.Redis, token: str, expiration: int):
    try:
        return await redis.set(name=token, value="blacklisted", ex=expiration)
    except Exception as e:
        logger.error(f"Failed to blacklist a token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An unexpected error occurred. Please try again later",
        )


async def is_refresh_token_blacklisted(redis: aioredis.Redis, token: str):
    return await redis.exists(token)
