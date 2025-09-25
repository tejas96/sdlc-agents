"""Workflow CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.workflow import Workflow, WorkflowCreate, WorkflowUpdate


class CRUDWorkflow(CRUDBase[Workflow, WorkflowCreate, WorkflowUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Workflow | None:
        """Get workflow by slug."""
        result = await db.execute(select(Workflow).where(Workflow.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100) -> list[Workflow]:
        """Get workflows by owner."""
        result = await db.execute(select(Workflow).where(Workflow.owner_id == owner_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_project(
        self, db: AsyncSession, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> list[Workflow]:
        """Get workflows by project."""
        result = await db.execute(select(Workflow).where(Workflow.project_id == project_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_trigger_type(
        self, db: AsyncSession, *, trigger_type: str, skip: int = 0, limit: int = 100
    ) -> list[Workflow]:
        """Get workflows by trigger type."""
        result = await db.execute(
            select(Workflow).where(Workflow.trigger_type == trigger_type).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_active(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Workflow]:
        """Get active workflows."""
        result = await db.execute(select(Workflow).where(Workflow.status == "active").offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_scheduled(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Workflow]:
        """Get scheduled workflows."""
        result = await db.execute(
            select(Workflow)
            .where(Workflow.trigger_type == "schedule")
            .where(Workflow.status == "active")
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


workflow_crud = CRUDWorkflow(Workflow)
