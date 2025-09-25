"""Database utility functions."""

import asyncio

from sqlalchemy import text

from app.core.database import get_async_session
from app.utils import get_logger

logger = get_logger(__name__)


async def wait_for_database(max_retries: int = 10, delay_seconds: float = 1.0) -> None:
    """Wait for database to be available."""
    for attempt in range(max_retries):
        try:
            async with get_async_session() as session:
                await session.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay_seconds)
            else:
                raise


async def acquire_advisory_lock(lock_id: int) -> bool:
    """Acquire PostgreSQL advisory lock."""
    try:
        async with get_async_session() as session:
            result = await session.execute(
                text("SELECT pg_try_advisory_lock(:lock_id)"),
                {"lock_id": lock_id}
            )
            acquired = result.scalar()
            if acquired:
                logger.info(f"Acquired advisory lock {lock_id}")
            else:
                logger.warning(f"Failed to acquire advisory lock {lock_id}")
            return bool(acquired)
    except Exception as e:
        logger.error(f"Error acquiring advisory lock {lock_id}: {e}")
        return False


async def release_advisory_lock(lock_id: int) -> bool:
    """Release PostgreSQL advisory lock."""
    try:
        async with get_async_session() as session:
            result = await session.execute(
                text("SELECT pg_advisory_unlock(:lock_id)"),
                {"lock_id": lock_id}
            )
            released = result.scalar()
            if released:
                logger.info(f"Released advisory lock {lock_id}")
            else:
                logger.warning(f"Failed to release advisory lock {lock_id}")
            return bool(released)
    except Exception as e:
        logger.error(f"Error releasing advisory lock {lock_id}: {e}")
        return False
