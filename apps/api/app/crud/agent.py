"""Agent CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.agent import Agent, AgentCreate, AgentUpdate


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Agent | None:
        """Get agent by slug."""
        result = await db.execute(select(Agent).where(Agent.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        """Get agents by owner."""
        result = await db.execute(
            select(Agent).where(Agent.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_project(
        self, db: AsyncSession, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        """Get agents by project."""
        result = await db.execute(
            select(Agent).where(Agent.project_id == project_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, agent_type: str, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        """Get agents by type."""
        result = await db.execute(
            select(Agent).where(Agent.agent_type == agent_type).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        """Get active agents."""
        result = await db.execute(
            select(Agent).where(Agent.status == "active").offset(skip).limit(limit)
        )
        return result.scalars().all()


agent_crud = CRUDAgent(Agent)
