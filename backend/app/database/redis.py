"""
Redis Database Connection
=========================

Manages optional, high-performance Redis caching connections.
If Redis is disabled or unreachable, gracefully falls back without crashing.
"""

from typing import Optional
from app.config import get_settings
from app.utils.logger import logger

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


_redis_client: Optional[Any] = None


async def init_redis_pool() -> None:
    """Initialize Redis asynchronous connection pool if enabled."""
    global _redis_client
    settings = get_settings()

    if not settings.REDIS_ENABLED:
        logger.info("Redis caching is disabled in configuration (`REDIS_ENABLED=False`).")
        return

    if redis is None:
        logger.warning("`redis` Python library not installed. Caching layer will be skipped.")
        return

    try:
        _redis_client = redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
        )
        await _redis_client.ping()
        logger.info(f"Connected to Redis cache successfully at {settings.REDIS_URI}")
    except Exception as e:
        logger.warning(f"Could not connect to Redis ({e}). Continuing with cache bypassed.")
        _redis_client = None


async def close_redis_pool() -> None:
    """Close Redis connection pool on application shutdown."""
    global _redis_client
    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("Redis connection pool closed.")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        finally:
            _redis_client = None


def get_redis() -> Optional[Any]:
    """
    Get the active Redis client instance or None if disabled/unreachable.
    """
    return _redis_client
