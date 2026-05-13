# utils/cache_manager.py
"""Redis cache manager with async support."""
import json
import hashlib
from typing import Any, Optional
from functools import wraps
import redis.asyncio as aioredis
from backend.core.config import settings
from backend.core.logger import logger

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        redis = await get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache GET error: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> bool:
    """Set value in cache with TTL."""
    try:
        redis = await get_redis()
        await redis.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning(f"Cache SET error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete cache key."""
    try:
        redis = await get_redis()
        await redis.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache DELETE error: {e}")
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern."""
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            return await redis.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache DELETE PATTERN error: {e}")
        return 0


def make_cache_key(*args) -> str:
    """Create deterministic cache key from arguments."""
    raw = ":".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
