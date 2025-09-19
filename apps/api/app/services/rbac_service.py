"""Role-Based Access Control (RBAC) service."""

from datetime import datetime
from typing import Optional

from app.models.rbac import DEFAULT_ROLES, Permission, PermissionType, ResourcePermission, Role, RoleType, UserRole
from app.models.user import User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RBACService:
    """Service for managing role-based access control."""

    async def has_permission(
        self,
        user: User,
        permission: PermissionType,
        session: Optional[AsyncSession] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
    ) -> bool:
        """Check if user has a specific permission."""

        # System admin has all permissions
        if user.is_superuser:
            return True

        # Check role-based permissions
        user_permissions = await self.get_user_permissions(user, session)
        if permission in user_permissions:
            return True

        # Check resource-specific permissions
        if resource_type and resource_id and session:
            resource_perms = await self.get_user_resource_permissions(user.id, resource_type, resource_id, session)
            if permission in resource_perms:
                return True

        return False

    async def get_user_permissions(self, user: User, session: Optional[AsyncSession] = None) -> list[PermissionType]:
        """Get all permissions for a user based on their roles."""
        permissions = set()

        if not session:
            logger.warning("No database session provided for permission check")
            return list(permissions)

        # Get user's roles
        stmt = select(Role).join(UserRole).where(UserRole.user_id == user.id)
        result = await session.execute(stmt)
        user_roles = result.scalars().all()

        # Collect permissions from all roles
        for role in user_roles:
            role_permissions = await self.get_role_permissions(role.id, session)
            permissions.update(role_permissions)

        return list(permissions)

    async def get_role_permissions(self, role_id: int, session: AsyncSession) -> list[PermissionType]:
        """Get all permissions for a specific role."""
        stmt = select(Permission.permission_type).join(Role.permissions).where(Role.id == role_id)
        result = await session.execute(stmt)
        permissions = result.scalars().all()
        return [PermissionType(perm) for perm in permissions]

    async def get_user_resource_permissions(
        self, user_id: int, resource_type: str, resource_id: int, session: AsyncSession
    ) -> list[PermissionType]:
        """Get resource-specific permissions for a user."""
        stmt = select(ResourcePermission).where(
            ResourcePermission.user_id == user_id,
            ResourcePermission.resource_type == resource_type,
            ResourcePermission.resource_id == resource_id,
            # Check if permission hasn't expired
            (ResourcePermission.expires_at.is_(None) | (ResourcePermission.expires_at > datetime.utcnow().isoformat())),
        )
        result = await session.execute(stmt)
        permissions = result.scalars().all()
        return [perm.permission_type for perm in permissions]

    async def assign_role_to_user(
        self, user_id: int, role_id: int, granted_by: int, session: AsyncSession, expires_at: Optional[str] = None
    ) -> bool:
        """Assign a role to a user."""
        try:
            # Check if user already has this role
            existing_stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            existing_result = await session.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                logger.info(f"User {user_id} already has role {role_id}")
                return True

            # Create new user role assignment
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                granted_by=granted_by,
                granted_at=datetime.utcnow().isoformat(),
                expires_at=expires_at,
            )

            session.add(user_role)
            await session.commit()

            logger.info(f"Assigned role {role_id} to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            await session.rollback()
            return False

    async def revoke_role_from_user(self, user_id: int, role_id: int, session: AsyncSession) -> bool:
        """Revoke a role from a user."""
        try:
            stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            result = await session.execute(stmt)
            user_role = result.scalar_one_or_none()

            if user_role:
                await session.delete(user_role)
                await session.commit()
                logger.info(f"Revoked role {role_id} from user {user_id}")
                return True
            else:
                logger.info(f"User {user_id} doesn't have role {role_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to revoke role: {e}")
            await session.rollback()
            return False

    async def grant_resource_permission(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        permission_type: PermissionType,
        granted_by: int,
        session: AsyncSession,
        expires_at: Optional[str] = None,
    ) -> bool:
        """Grant a specific permission on a resource to a user."""
        try:
            resource_permission = ResourcePermission(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_type=permission_type,
                granted_by=granted_by,
                granted_at=datetime.utcnow().isoformat(),
                expires_at=expires_at,
            )

            session.add(resource_permission)
            await session.commit()

            logger.info(f"Granted {permission_type} on {resource_type}:{resource_id} to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to grant resource permission: {e}")
            await session.rollback()
            return False

    async def revoke_resource_permission(
        self, user_id: int, resource_type: str, resource_id: int, permission_type: PermissionType, session: AsyncSession
    ) -> bool:
        """Revoke a specific permission on a resource from a user."""
        try:
            stmt = select(ResourcePermission).where(
                ResourcePermission.user_id == user_id,
                ResourcePermission.resource_type == resource_type,
                ResourcePermission.resource_id == resource_id,
                ResourcePermission.permission_type == permission_type,
            )
            result = await session.execute(stmt)
            permission = result.scalar_one_or_none()

            if permission:
                await session.delete(permission)
                await session.commit()
                logger.info(f"Revoked {permission_type} on {resource_type}:{resource_id} from user {user_id}")
                return True
            else:
                logger.info(f"User {user_id} doesn't have {permission_type} on {resource_type}:{resource_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to revoke resource permission: {e}")
            await session.rollback()
            return False

    async def get_user_roles(self, user_id: int, session: AsyncSession) -> list[Role]:
        """Get all roles assigned to a user."""
        stmt = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create_role(
        self, name: str, role_type: RoleType, description: str, permissions: list[PermissionType], session: AsyncSession
    ) -> Optional[Role]:
        """Create a new role with specified permissions."""
        try:
            # Create the role
            role = Role(name=name, role_type=role_type, description=description, is_system_role=False)

            session.add(role)
            await session.flush()  # Get the role ID

            # Add permissions to the role
            for perm_type in permissions:
                # Get or create permission
                perm_stmt = select(Permission).where(Permission.permission_type == perm_type)
                perm_result = await session.execute(perm_stmt)
                permission = perm_result.scalar_one_or_none()

                if permission:
                    role.permissions.append(permission)

            await session.commit()
            logger.info(f"Created role {name} with {len(permissions)} permissions")
            return role

        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            await session.rollback()
            return None

    async def initialize_default_roles_and_permissions(self, session: AsyncSession) -> bool:
        """Initialize default roles and permissions in the database."""
        try:
            # Create all permissions first
            all_permissions = []
            for perm_type in PermissionType:
                # Check if permission already exists
                stmt = select(Permission).where(Permission.permission_type == perm_type)
                result = await session.execute(stmt)
                existing_perm = result.scalar_one_or_none()

                if not existing_perm:
                    permission = Permission(
                        name=perm_type.value,
                        permission_type=perm_type,
                        description=f"Permission for {perm_type.value}",
                        resource_type=perm_type.value.split(":")[0],  # Extract resource type
                    )
                    session.add(permission)
                    all_permissions.append(permission)

            await session.flush()

            # Create default roles
            for role_type, role_config in DEFAULT_ROLES.items():
                # Check if role already exists
                stmt = select(Role).where(Role.role_type == role_type)
                result = await session.execute(stmt)
                existing_role = result.scalar_one_or_none()

                if not existing_role:
                    role = Role(
                        name=role_config["name"],
                        role_type=role_type,
                        description=role_config["description"],
                        is_system_role=True,
                    )
                    session.add(role)
                    await session.flush()

                    # Add permissions to role
                    for perm_type in role_config["permissions"]:
                        perm_stmt = select(Permission).where(Permission.permission_type == perm_type)
                        perm_result = await session.execute(perm_stmt)
                        permission = perm_result.scalar_one_or_none()

                        if permission:
                            role.permissions.append(permission)

            await session.commit()
            logger.info("Initialized default roles and permissions")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize RBAC: {e}")
            await session.rollback()
            return False


# Global RBAC service instance
rbac_service = RBACService()
