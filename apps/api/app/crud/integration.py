"""Integration CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.integration import Integration, IntegrationCreate, IntegrationUpdate


class CRUDIntegration(CRUDBase[Integration, IntegrationCreate, IntegrationUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Integration | None:
        """Get integration by slug."""
        result = await db.execute(select(Integration).where(Integration.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Integration]:
        """Get integrations by owner."""
        result = await db.execute(
            select(Integration).where(Integration.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, integration_type: str, skip: int = 0, limit: int = 100
    ) -> list[Integration]:
        """Get integrations by type."""
        result = await db.execute(
            select(Integration)
            .where(Integration.integration_type == integration_type)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Integration]:
        """Get active integrations."""
        result = await db.execute(
            select(Integration).where(Integration.status == "active").offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_webhook_url(self, db: AsyncSession, *, webhook_url: str) -> Integration | None:
        """Get integration by webhook URL."""
        result = await db.execute(select(Integration).where(Integration.webhook_url == webhook_url))
        return result.scalar_one_or_none()


integration_crud = CRUDIntegration(Integration)
