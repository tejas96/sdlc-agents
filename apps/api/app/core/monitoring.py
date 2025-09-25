"""Comprehensive monitoring and observability system."""

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
from fastapi import Request, Response
from loguru import logger
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings


class PrometheusMetrics:
    """Prometheus metrics collector for the application."""

    def __init__(self):
        """Initialize Prometheus metrics."""
        self.registry = CollectorRegistry()

        # HTTP request metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry
        )

        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry
        )

        # Agent execution metrics
        self.agent_executions_total = Counter(
            "agent_executions_total",
            "Total agent executions",
            ["agent_type", "status"],
            registry=self.registry
        )

        self.agent_execution_duration = Histogram(
            "agent_execution_duration_seconds",
            "Agent execution duration in seconds",
            ["agent_type"],
            registry=self.registry
        )

        # Integration metrics
        self.integration_requests_total = Counter(
            "integration_requests_total",
            "Total integration API requests",
            ["integration_type", "status"],
            registry=self.registry
        )

        self.integration_request_duration = Histogram(
            "integration_request_duration_seconds",
            "Integration request duration in seconds",
            ["integration_type"],
            registry=self.registry
        )

        # System metrics
        self.active_users = Gauge(
            "active_users_total",
            "Number of active users",
            registry=self.registry
        )

        self.database_connections = Gauge(
            "database_connections_active",
            "Active database connections",
            registry=self.registry
        )

        self.cache_operations_total = Counter(
            "cache_operations_total",
            "Total cache operations",
            ["operation", "status"],
            registry=self.registry
        )

        # Error metrics
        self.errors_total = Counter(
            "errors_total",
            "Total errors",
            ["error_type", "severity"],
            registry=self.registry
        )

        # Authentication metrics
        self.auth_attempts_total = Counter(
            "auth_attempts_total",
            "Total authentication attempts",
            ["status"],
            registry=self.registry
        )

        # Task queue metrics
        self.background_tasks_total = Counter(
            "background_tasks_total",
            "Total background tasks",
            ["task_type", "status"],
            registry=self.registry
        )

        self.background_task_duration = Histogram(
            "background_task_duration_seconds",
            "Background task duration in seconds",
            ["task_type"],
            registry=self.registry
        )

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def record_agent_execution(self, agent_type: str, status: str, duration: float):
        """Record agent execution metrics."""
        self.agent_executions_total.labels(
            agent_type=agent_type,
            status=status
        ).inc()

        if duration > 0:
            self.agent_execution_duration.labels(
                agent_type=agent_type
            ).observe(duration)

    def record_integration_request(self, integration_type: str, status: str, duration: float):
        """Record integration request metrics."""
        self.integration_requests_total.labels(
            integration_type=integration_type,
            status=status
        ).inc()

        if duration > 0:
            self.integration_request_duration.labels(
                integration_type=integration_type
            ).observe(duration)

    def record_error(self, error_type: str, severity: str = "error"):
        """Record error metrics."""
        self.errors_total.labels(
            error_type=error_type,
            severity=severity
        ).inc()

    def record_auth_attempt(self, status: str):
        """Record authentication attempt."""
        self.auth_attempts_total.labels(status=status).inc()

    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation."""
        self.cache_operations_total.labels(
            operation=operation,
            status=status
        ).inc()

    def record_background_task(self, task_type: str, status: str, duration: float = 0):
        """Record background task metrics."""
        self.background_tasks_total.labels(
            task_type=task_type,
            status=status
        ).inc()

        if duration > 0:
            self.background_task_duration.labels(
                task_type=task_type
            ).observe(duration)

    def update_active_users(self, count: int):
        """Update active users gauge."""
        self.active_users.set(count)

    def update_database_connections(self, count: int):
        """Update database connections gauge."""
        self.database_connections.set(count)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    def __init__(self, app, metrics: PrometheusMetrics):
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()

        # Extract endpoint path (without query parameters)
        endpoint = request.url.path
        method = request.method

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            # Record error and re-raise
            self.metrics.record_error("http_request_error")
            logger.error(f"HTTP request error: {e}")
            status_code = 500
            raise

        finally:
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_http_request(method, endpoint, status_code, duration)

        return response


class SystemMonitor:
    """System resource monitoring."""

    def __init__(self):
        self.settings = get_settings()

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage('/')

            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                }
            except:
                network_stats = {}

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg_1m": load_avg[0],
                    "load_avg_5m": load_avg[1],
                    "load_avg_15m": load_avg[2],
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
                "network": network_stats,
            }

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}

    def get_process_metrics(self) -> dict[str, Any]:
        """Get current process metrics."""
        try:
            process = psutil.Process()

            # Memory info
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # CPU info
            cpu_percent = process.cpu_percent()
            cpu_times = process.cpu_times()

            # I/O info (if available)
            try:
                io_counters = process.io_counters()
                io_stats = {
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                }
            except:
                io_stats = {}

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "create_time": process.create_time(),
                "num_threads": process.num_threads(),
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": memory_percent,
                },
                "cpu": {
                    "percent": cpu_percent,
                    "user_time": cpu_times.user,
                    "system_time": cpu_times.system,
                },
                "io": io_stats,
            }

        except Exception as e:
            logger.error(f"Failed to get process metrics: {e}")
            return {"error": str(e)}


class HealthChecker:
    """Application health checking."""

    def __init__(self):
        self.checks = {}
        self.register_default_checks()

    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self.checks[name] = check_func

    def register_default_checks(self):
        """Register default health checks."""
        # Database check will be added when we have DB session
        # Cache check will be added when we have cache service
        # Task queue check will be added when we have task manager
        pass

    async def run_checks(self) -> dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_status = "healthy"

        for name, check_func in self.checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                results[name] = result

                if result.get("status") != "healthy":
                    overall_status = "unhealthy"

            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
                logger.error(f"Health check {name} failed: {e}")

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }

    async def get_readiness(self) -> dict[str, Any]:
        """Check if the application is ready to serve requests."""
        # Basic readiness checks
        checks = await self.run_checks()

        # Application is ready if all critical checks pass
        critical_checks = ["database", "cache"]  # Add more as needed

        ready = True
        for check_name in critical_checks:
            if check_name in checks["checks"]:
                if checks["checks"][check_name].get("status") != "healthy":
                    ready = False
                    break

        return {
            "ready": ready,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks["checks"]
        }

    async def get_liveness(self) -> dict[str, Any]:
        """Check if the application is alive."""
        # Simple liveness check - if we can respond, we're alive
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - getattr(self, '_start_time', time.time())
        }


class PerformanceTracker:
    """Track performance metrics and identify bottlenecks."""

    def __init__(self):
        self.operation_times = {}
        self.slow_operations = []
        self.error_counts = {}

    @asynccontextmanager
    async def track_operation(self, operation_name: str, threshold_seconds: float = 1.0):
        """Context manager to track operation performance."""
        start_time = time.time()
        try:
            yield
        except Exception as e:
            # Track errors
            error_type = type(e).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            raise
        finally:
            duration = time.time() - start_time

            # Track operation timing
            if operation_name not in self.operation_times:
                self.operation_times[operation_name] = []

            self.operation_times[operation_name].append(duration)

            # Track slow operations
            if duration > threshold_seconds:
                self.slow_operations.append({
                    "operation": operation_name,
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Keep only recent slow operations
                if len(self.slow_operations) > 100:
                    self.slow_operations = self.slow_operations[-50:]

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        stats = {}

        for operation, times in self.operation_times.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "avg_duration": sum(times) / len(times),
                    "min_duration": min(times),
                    "max_duration": max(times),
                    "recent_avg": sum(times[-10:]) / min(len(times), 10),
                }

        return {
            "operation_stats": stats,
            "slow_operations": self.slow_operations[-10:],  # Last 10 slow operations
            "error_counts": self.error_counts,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global monitoring instances
metrics = PrometheusMetrics()
system_monitor = SystemMonitor()
health_checker = HealthChecker()
performance_tracker = PerformanceTracker()


# Utility functions for monitoring

def monitor_function(operation_name: str, threshold_seconds: float = 1.0):
    """Decorator to monitor function performance."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async with performance_tracker.track_operation(operation_name, threshold_seconds):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper(*args, **kwargs)
            else:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    if duration > threshold_seconds:
                        performance_tracker.slow_operations.append({
                            "operation": operation_name,
                            "duration": duration,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                    return result
                except Exception as e:
                    error_type = type(e).__name__
                    performance_tracker.error_counts[error_type] = performance_tracker.error_counts.get(error_type, 0) + 1
                    raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
