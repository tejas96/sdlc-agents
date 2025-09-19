"""Redis caching service for performance optimization."""

import json
import pickle
import time
from datetime import timedelta
from typing import Any, Optional, Union

from loguru import logger

from app.core.config import get_settings

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class CacheService:
    """Redis-based caching service for performance optimization."""

    def __init__(self):
        """Initialize Redis connection."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not redis:
            logger.warning("Redis not available, caching disabled")
            return

        try:
            redis_url = self.settings.REDIS_URL or "redis://localhost:6379/0"
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if not self.redis_client:
            return default

        try:
            value = await self.redis_client.get(key)
            if value is None:
                return default

            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value)
                except (pickle.PickleError, TypeError):
                    # Return as string if can't deserialize
                    return value.decode('utf-8') if isinstance(value, bytes) else value

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis_client:
            return False

        try:
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            elif isinstance(value, (str, int, float, bool)):
                serialized_value = json.dumps(value)
            else:
                # Use pickle for complex objects
                serialized_value = pickle.dumps(value)

            # Set with TTL
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)

            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False

        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False

        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration time for a key."""
        if not self.redis_client:
            return False

        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            result = await self.redis_client.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        if not self.redis_client:
            return -1

        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        if not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache."""
        if not self.redis_client:
            return None

        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement a numeric value in cache."""
        if not self.redis_client:
            return None

        try:
            return await self.redis_client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Cache decrement error for key {key}: {e}")
            return None

    # High-level caching methods for common use cases

    async def cache_user_session(self, user_id: int, session_data: dict, ttl: timedelta = timedelta(hours=24)) -> bool:
        """Cache user session data."""
        key = f"user_session:{user_id}"
        return await self.set(key, session_data, ttl)

    async def get_user_session(self, user_id: int) -> Optional[dict]:
        """Get cached user session data."""
        key = f"user_session:{user_id}"
        return await self.get(key)

    async def invalidate_user_session(self, user_id: int) -> bool:
        """Invalidate user session cache."""
        key = f"user_session:{user_id}"
        return await self.delete(key)

    async def cache_api_response(self, endpoint: str, params: dict, response_data: Any, ttl: timedelta = timedelta(minutes=15)) -> bool:
        """Cache API response data."""
        # Create cache key from endpoint and parameters
        params_str = json.dumps(params, sort_keys=True)
        key = f"api_response:{endpoint}:{hash(params_str)}"
        return await self.set(key, response_data, ttl)

    async def get_cached_api_response(self, endpoint: str, params: dict) -> Any:
        """Get cached API response data."""
        params_str = json.dumps(params, sort_keys=True)
        key = f"api_response:{endpoint}:{hash(params_str)}"
        return await self.get(key)

    async def cache_agent_execution_result(self, execution_id: str, result_data: dict, ttl: timedelta = timedelta(hours=1)) -> bool:
        """Cache agent execution results."""
        key = f"agent_execution:{execution_id}"
        return await self.set(key, result_data, ttl)

    async def get_cached_agent_execution_result(self, execution_id: str) -> Optional[dict]:
        """Get cached agent execution results."""
        key = f"agent_execution:{execution_id}"
        return await self.get(key)

    async def cache_integration_data(self, integration_type: str, integration_id: int, data: dict, ttl: timedelta = timedelta(minutes=30)) -> bool:
        """Cache integration data (repos, projects, etc.)."""
        key = f"integration:{integration_type}:{integration_id}"
        return await self.set(key, data, ttl)

    async def get_cached_integration_data(self, integration_type: str, integration_id: int) -> Optional[dict]:
        """Get cached integration data."""
        key = f"integration:{integration_type}:{integration_id}"
        return await self.get(key)

    async def invalidate_integration_cache(self, integration_type: str, integration_id: int) -> bool:
        """Invalidate integration cache."""
        pattern = f"integration:{integration_type}:{integration_id}*"
        count = await self.clear_pattern(pattern)
        return count > 0

    # Rate limiting support

    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """
        Check rate limit for a key.
        Returns: (is_allowed, current_count, time_until_reset)
        """
        if not self.redis_client:
            return True, 0, 0

        try:
            # Use sliding window rate limiting
            current_time = int(time.time())
            window_start = current_time - window_seconds

            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_count = await self.redis_client.zcard(key)

            if current_count >= limit:
                # Rate limit exceeded
                oldest_entry = await self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_entry:
                    time_until_reset = int(oldest_entry[0][1]) + window_seconds - current_time
                else:
                    time_until_reset = window_seconds
                return False, current_count, max(0, time_until_reset)

            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, window_seconds)

            return True, current_count + 1, 0

        except Exception as e:
            logger.error(f"Rate limit check error for key {key}: {e}")
            # Allow request on error
            return True, 0, 0

    # Health check

    async def health_check(self) -> dict:
        """Perform Redis health check."""
        if not self.redis_client:
            return {"status": "unhealthy", "message": "Redis client not initialized"}

        try:
            # Test basic operations
            test_key = "health_check_test"
            await self.redis_client.set(test_key, "test_value", ex=10)
            value = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)

            if value == b"test_value":
                # Get Redis info
                info = await self.redis_client.info()
                return {
                    "status": "healthy",
                    "redis_version": info.get("redis_version"),
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "uptime_in_seconds": info.get("uptime_in_seconds")
                }
            else:
                return {"status": "unhealthy", "message": "Redis read/write test failed"}

        except Exception as e:
            return {"status": "unhealthy", "message": f"Redis health check failed: {e!s}"}


# Global cache service instance
cache_service = CacheService()


# Decorator for caching function results
def cached(ttl: Union[int, timedelta] = timedelta(minutes=15), key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib
            key_data = f"{key_prefix}:{func.__name__}:{args!s}:{sorted(kwargs.items())!s}"
            cache_key = f"func_cache:{hashlib.md5(key_data.encode()).hexdigest()}"

            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
