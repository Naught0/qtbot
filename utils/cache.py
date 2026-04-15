import os

from redis.asyncio import Redis


def ensure_redis():
    if not (host := os.getenv("REDIS_HOST")):
        raise Exception("REDIS_HOST is not set")

    return Redis(host=host, decode_responses=True)


redis_client = ensure_redis()
