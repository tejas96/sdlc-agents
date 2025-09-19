"""Background task processing with Celery and Redis."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from celery import Celery
from loguru import logger

from app.core.config import get_settings


# Initialize Celery app
def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    settings = get_settings()

    celery_app = Celery(
        "sdlc_agents",
        broker=settings.CELERY_BROKER_URL or settings.REDIS_URL or "redis://localhost:6379/1",
        backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL or "redis://localhost:6379/1",
        include=[
            "app.tasks.agent_tasks",
            "app.tasks.integration_tasks",
            "app.tasks.notification_tasks",
            "app.tasks.maintenance_tasks"
        ]
    )

    # Configure Celery
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        task_routes={
            "app.tasks.agent_tasks.*": {"queue": "agent_queue"},
            "app.tasks.integration_tasks.*": {"queue": "integration_queue"},
            "app.tasks.notification_tasks.*": {"queue": "notification_queue"},
            "app.tasks.maintenance_tasks.*": {"queue": "maintenance_queue"},
        },
        task_default_queue="default",
        task_default_exchange="default",
        task_default_exchange_type="direct",
        task_default_routing_key="default",
        # Retry configuration
        task_annotations={
            "*": {
                "rate_limit": "100/m",
                "retry_policy": {
                    "max_retries": 3,
                    "interval_start": 0,
                    "interval_step": 0.2,
                    "interval_max": 0.2,
                }
            }
        },
        # Beat schedule for periodic tasks
        beat_schedule={
            "cleanup_expired_sessions": {
                "task": "app.tasks.maintenance_tasks.cleanup_expired_sessions",
                "schedule": timedelta(hours=1),
            },
            "cleanup_old_audit_logs": {
                "task": "app.tasks.maintenance_tasks.cleanup_old_audit_logs",
                "schedule": timedelta(days=1),
            },
            "refresh_integration_tokens": {
                "task": "app.tasks.integration_tasks.refresh_oauth_tokens",
                "schedule": timedelta(hours=6),
            },
            "health_check_integrations": {
                "task": "app.tasks.integration_tasks.health_check_all_integrations",
                "schedule": timedelta(minutes=30),
            },
            "generate_daily_reports": {
                "task": "app.tasks.maintenance_tasks.generate_daily_reports",
                "schedule": timedelta(days=1),
            },
        },
    )

    return celery_app


# Create global Celery instance
celery_app = create_celery_app()


class TaskManager:
    """Manager for background tasks and job queuing."""

    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    async def schedule_agent_execution(
        self,
        agent_id: int,
        user_id: int,
        execution_data: Dict[str, Any],
        priority: str = "normal",
        delay_seconds: int = 0
    ) -> str:
        """Schedule agent execution as background task."""
        try:
            task_kwargs = {
                "agent_id": agent_id,
                "user_id": user_id,
                "execution_data": execution_data,
                "scheduled_at": datetime.utcnow().isoformat()
            }

            queue_name = "agent_queue_high" if priority == "high" else "agent_queue"

            if delay_seconds > 0:
                eta = datetime.utcnow() + timedelta(seconds=delay_seconds)
                result = self.celery_app.send_task(
                    "app.tasks.agent_tasks.execute_agent_background",
                    kwargs=task_kwargs,
                    queue=queue_name,
                    eta=eta
                )
            else:
                result = self.celery_app.send_task(
                    "app.tasks.agent_tasks.execute_agent_background",
                    kwargs=task_kwargs,
                    queue=queue_name
                )

            logger.info(f"Scheduled agent execution task: {result.id}")
            return result.id

        except Exception as e:
            logger.error(f"Failed to schedule agent execution: {e}")
            raise

    async def schedule_integration_sync(
        self,
        integration_id: int,
        sync_type: str = "full",
        priority: str = "normal"
    ) -> str:
        """Schedule integration data synchronization."""
        try:
            task_kwargs = {
                "integration_id": integration_id,
                "sync_type": sync_type,
                "scheduled_at": datetime.utcnow().isoformat()
            }

            queue_name = "integration_queue_high" if priority == "high" else "integration_queue"

            result = self.celery_app.send_task(
                "app.tasks.integration_tasks.sync_integration_data",
                kwargs=task_kwargs,
                queue=queue_name
            )

            logger.info(f"Scheduled integration sync task: {result.id}")
            return result.id

        except Exception as e:
            logger.error(f"Failed to schedule integration sync: {e}")
            raise

    async def schedule_notification(
        self,
        user_ids: List[int],
        notification_type: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 0
    ) -> str:
        """Schedule notification delivery."""
        try:
            task_kwargs = {
                "user_ids": user_ids,
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "metadata": metadata or {},
                "scheduled_at": datetime.utcnow().isoformat()
            }

            if delay_seconds > 0:
                eta = datetime.utcnow() + timedelta(seconds=delay_seconds)
                result = self.celery_app.send_task(
                    "app.tasks.notification_tasks.send_notification",
                    kwargs=task_kwargs,
                    queue="notification_queue",
                    eta=eta
                )
            else:
                result = self.celery_app.send_task(
                    "app.tasks.notification_tasks.send_notification",
                    kwargs=task_kwargs,
                    queue="notification_queue"
                )

            logger.info(f"Scheduled notification task: {result.id}")
            return result.id

        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            raise

    async def schedule_file_processing(
        self,
        file_path: str,
        user_id: int,
        processing_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule file processing task."""
        try:
            task_kwargs = {
                "file_path": file_path,
                "user_id": user_id,
                "processing_type": processing_type,
                "metadata": metadata or {},
                "scheduled_at": datetime.utcnow().isoformat()
            }

            result = self.celery_app.send_task(
                "app.tasks.agent_tasks.process_uploaded_file",
                kwargs=task_kwargs,
                queue="agent_queue"
            )

            logger.info(f"Scheduled file processing task: {result.id}")
            return result.id

        except Exception as e:
            logger.error(f"Failed to schedule file processing: {e}")
            raise

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a background task."""
        try:
            result = self.celery_app.AsyncResult(task_id)

            status_info = {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "traceback": result.traceback,
                "successful": result.successful(),
                "failed": result.failed(),
                "date_done": result.date_done.isoformat() if result.date_done else None,
            }

            # Add progress info if available
            if hasattr(result, "info") and isinstance(result.info, dict):
                status_info.update(result.info)

            return status_info

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {
                "task_id": task_id,
                "status": "UNKNOWN",
                "error": str(e)
            }

    async def cancel_task(self, task_id: str, terminate: bool = False) -> bool:
        """Cancel a background task."""
        try:
            self.celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Cancelled task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about task queues."""
        try:
            inspect = self.celery_app.control.inspect()

            # Get active tasks
            active_tasks = inspect.active()

            # Get scheduled tasks
            scheduled_tasks = inspect.scheduled()

            # Get reserved tasks
            reserved_tasks = inspect.reserved()

            # Get queue lengths (requires additional setup)
            queue_stats = {}

            stats = {
                "active_tasks": active_tasks,
                "scheduled_tasks": scheduled_tasks,
                "reserved_tasks": reserved_tasks,
                "queue_lengths": queue_stats,
                "timestamp": datetime.utcnow().isoformat()
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {"error": str(e)}

    async def purge_queue(self, queue_name: str) -> int:
        """Purge all tasks from a queue."""
        try:
            result = self.celery_app.control.purge()
            logger.info(f"Purged queue: {queue_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to purge queue {queue_name}: {e}")
            return 0

    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics about Celery workers."""
        try:
            inspect = self.celery_app.control.inspect()

            # Get worker stats
            stats = inspect.stats()

            # Get worker status
            ping = inspect.ping()

            # Get registered tasks
            registered = inspect.registered()

            return {
                "stats": stats,
                "ping": ping,
                "registered_tasks": registered,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            return {"error": str(e)}


# Global task manager instance
task_manager = TaskManager(celery_app)


# Utility functions for common task patterns

async def schedule_delayed_task(
    task_name: str,
    delay_minutes: int,
    **task_kwargs
) -> str:
    """Schedule a task to run after a delay."""
    eta = datetime.utcnow() + timedelta(minutes=delay_minutes)
    result = celery_app.send_task(
        task_name,
        kwargs=task_kwargs,
        eta=eta
    )
    return result.id


async def schedule_recurring_task(
    task_name: str,
    interval_minutes: int,
    **task_kwargs
) -> str:
    """Schedule a recurring task (note: for demo, actual recurring tasks use beat schedule)."""
    # This would typically be handled by Celery Beat
    # For now, just schedule the next execution
    result = celery_app.send_task(
        task_name,
        kwargs=task_kwargs
    )
    return result.id


def task_retry_with_backoff(func):
    """Decorator to add exponential backoff retry to tasks."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            # Exponential backoff: 2^retry_count seconds
            countdown = 2 ** func.request.retries
            logger.warning(f"Task {func.name} failed, retrying in {countdown}s: {exc}")
            raise func.retry(exc=exc, countdown=countdown, max_retries=5)
    return wrapper


# Health check for background tasks
async def health_check_tasks() -> Dict[str, Any]:
    """Perform health check for the task system."""
    try:
        # Check if workers are alive
        inspect = celery_app.control.inspect()
        ping_result = inspect.ping()

        if not ping_result:
            return {
                "status": "unhealthy",
                "message": "No Celery workers responding"
            }

        # Check queue stats
        active_tasks = inspect.active()
        total_active = sum(len(tasks) for tasks in active_tasks.values())

        return {
            "status": "healthy",
            "workers": list(ping_result.keys()),
            "active_tasks": total_active,
            "worker_count": len(ping_result)
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Task system health check failed: {str(e)}"
        }
