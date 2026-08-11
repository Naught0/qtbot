import os

from redis.asyncio import Redis


def redis_from_env(decode_responses=True, **kwargs):
    if not (host := os.getenv("REDIS_HOST")):
        raise Exception("REDIS_HOST is not set")

    return Redis(host=host, decode_responses=decode_responses, **kwargs)


redis_client = redis_from_env()
