"""

Non-handler functions decorators

"""
import base64
import json

import aioredis

from kubectl.config import env

redis = aioredis.from_url(
    f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}",
    password=env.REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True,
    db=0,
)


def cache(ttl: int = 3600):
    """

    Stores the results of a given function within a ttl frame on redis

    """

    def decorator(func):
        async def wrapper(*args, **kwargs) -> str:
            key = base64.b64encode(
                f"{func.__name__}{args}{kwargs}".encode("utf-8")
            ).decode("utf-8")
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis.set(key, json.dumps(result), ex=ttl)
            return result

        return wrapper

    return decorator
