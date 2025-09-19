import time
from typing import Any

from app.api.v1.api import api_router
from app.core.cache import cache_service
from app.core.config import get_settings
from app.core.database import close_db_connection, init_db
from app.core.monitoring import MetricsMiddleware, health_checker, metrics, system_monitor
from app.services.rbac_service import rbac_service
from app.utils import configure_logging, get_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

logger = get_logger(__name__)


def get_application() -> FastAPI:
    """Get the FastAPI application"""
    # Initialize logging first
    configure_logging()

    settings = get_settings()
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
## SDLC Agents - Software Development Lifecycle Management API

A comprehensive FastAPI system for managing software development lifecycle processes:

- **Project Management**: Create, track, and manage software projects
- **Agent Orchestration**: Deploy and manage AI agents for development tasks
- **Workflow Automation**: Automate SDLC processes and integrations
- **User Management**: Handle team members, roles, and permissions
- **Integration Hub**: Connect with various development tools and services
- **Monitoring & Analytics**: Track project metrics and agent performance
- **RESTful API**: Modern API design with comprehensive documentation

Built with FastAPI, SQLModel, and async Python for high performance and scalability.
        """,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_DOCS else None,
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    )

    # CORS middleware configuration
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins() or ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add monitoring middleware
    if settings.PROMETHEUS_ENABLED:
        _app.add_middleware(MetricsMiddleware, metrics=metrics)

    # Include API router
    _app.include_router(api_router, prefix=settings.API_V1_STR)

    @_app.on_event("startup")
    async def startup_event() -> None:
        """Application startup event handler"""
        logger.info("Starting up SDLC Agents application...")

        try:
            # Initialize database
            await init_db()
            logger.info("Database initialized successfully")

            # Initialize Redis cache
            await cache_service.connect()
            logger.info("Cache service connected successfully")

            # Initialize RBAC system
            from app.core.database import get_async_session

            async with get_async_session() as session:
                await rbac_service.initialize_default_roles_and_permissions(session)
            logger.info("RBAC system initialized successfully")

            # Record startup metric
            health_checker._start_time = time.time()
            metrics.record_auth_attempt("startup")

        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise

    @_app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Application shutdown event handler"""
        logger.info("Shutting down application...")
        try:
            # Close cache connections
            await cache_service.disconnect()
            logger.info("Cache service disconnected successfully")

            # Close database connections
            await close_db_connection()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Failed to close connections: {e}")

    @_app.get("/")
    async def root() -> dict[str, Any]:
        """Welcome endpoint with API information"""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "description": "SDLC Agents API for software development lifecycle management",
            "version": settings.VERSION,
            "docs": "/docs" if settings.ENABLE_DOCS else None,
            "redoc": "/redoc" if settings.ENABLE_REDOC else None,
            "health": "/health",
            "environment": settings.ENVIRONMENT,
        }

    @_app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Global health check endpoint"""
        health_results = await health_checker.run_checks()
        system_metrics = system_monitor.get_system_metrics()

        return {
            "status": health_results.get("status", "healthy"),
            "version": settings.VERSION,
            "service": "SDLC Agents API",
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "checks": health_results.get("checks", {}),
            "system": {
                "cpu_percent": system_metrics.get("cpu", {}).get("percent", 0),
                "memory_percent": system_metrics.get("memory", {}).get("percent", 0),
                "disk_percent": system_metrics.get("disk", {}).get("percent", 0),
            },
        }

    @_app.get("/metrics", response_class=PlainTextResponse)
    async def get_metrics() -> str:
        """Prometheus metrics endpoint"""
        if not settings.PROMETHEUS_ENABLED:
            return "Metrics disabled"
        return metrics.get_metrics()

    @_app.get("/ready")
    async def readiness_check() -> dict[str, Any]:
        """Readiness check endpoint for Kubernetes"""
        return await health_checker.get_readiness()

    @_app.get("/live")
    async def liveness_check() -> dict[str, Any]:
        """Liveness check endpoint for Kubernetes"""
        return await health_checker.get_liveness()

    return _app


app = get_application()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
