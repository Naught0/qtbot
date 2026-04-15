import functools
import os
import pickle

from redis.asyncio import Redis

redis_client = Redis(host=os.getenv("REDIS_HOST"), decode_responses=True)


def cache(
    redis: Redis,
    namespace: str | None = None,
    ttl: int | None = 300,
):
    def deco(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{namespace}:{func.__name__}:{args}:{kwargs}"
            value = await redis.get(key)
            if value:
                print(f"Cache hit for {key}")
                return pickle.loads(value)

            print(f"Cache miss for {key}")
            resp = func(*args, **kwargs)
            await redis.set(key, pickle.dumps(resp), ex=ttl)
            return resp

        return wrapper

    return deco
