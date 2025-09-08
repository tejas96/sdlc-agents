"""Project CRUD operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.project import Project, ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Project | None:
        """Get project by slug."""
        result = await db.execute(select(Project).where(Project.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        """Get projects by owner."""
        result = await db.execute(
            select(Project).where(Project.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        """Get projects by status."""
        result = await db.execute(
            select(Project).where(Project.status == status).offset(skip).limit(limit)
        )
        return result.scalars().all()


project_crud = CRUDProject(Project)
