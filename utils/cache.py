import os

from redis.asyncio import Redis

redis_client = Redis(host=os.getenv("REDIS_HOST"), decode_responses=True)
