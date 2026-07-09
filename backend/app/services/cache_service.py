"""
Cache Service
=============

Unified wrapper around Redis for caching high-frequency read endpoints.
If Redis is disabled or unreachable, operations bypass cleanly without raising exceptions.
"""

import json
from typing import Any, Optional
from app.database.redis import get_redis
from app.utils.logger import logger


class CacheService:
    """Provides get, set, and invalidation helpers over optional Redis instance."""

    @staticmethod
    async def get_cache(key: str) -> Optional[Any]:
        """
        Retrieve and deserialize JSON data from cache.
        Returns None if cache is disabled, key is missing, or Redis is unreachable.
        """
        redis_client = get_redis()
        if not redis_client:
            return None

        try:
            cached_val = await redis_client.get(key)
            if cached_val:
                return json.loads(cached_val)
        except Exception as e:
            logger.debug(f"Cache get error for key '{key}': {e}")

        return None

    @staticmethod
    async def set_cache(key: str, value: Any, ttl_seconds: int = 60) -> bool:
        """
        Serialize data to JSON and store in cache with Time-To-Live.
        Returns True on success, False if skipped or error occurs.
        """
        redis_client = get_redis()
        if not redis_client:
            return False

        try:
            serialized_val = json.dumps(value, default=str)
            await redis_client.setex(key, ttl_seconds, serialized_val)
            return True
        except Exception as e:
            logger.debug(f"Cache set error for key '{key}': {e}")
            return False

    @staticmethod
    async def invalidate_cache(pattern: str) -> int:
        """
        Delete cached items matching a specific key pattern (e.g., 'dashboard:*').
        Returns the number of keys removed.
        """
        redis_client = get_redis()
        if not redis_client:
            return 0

        try:
            keys = []
            async for key in redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await redis_client.delete(*keys)
        except Exception as e:
            logger.debug(f"Cache invalidation error for pattern '{pattern}': {e}")

        return 0
