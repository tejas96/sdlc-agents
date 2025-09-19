"""Role-Based Access Control (RBAC) models."""

from enum import Enum
from typing import TYPE_CHECKING

from app.models.base import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class PermissionType(str, Enum):
    """Permission types for RBAC."""

    # Project permissions
    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE = "project:manage"

    # Agent permissions
    AGENT_VIEW = "agent:view"
    AGENT_CREATE = "agent:create"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    AGENT_MANAGE = "agent:manage"

    # Workflow permissions
    WORKFLOW_VIEW = "workflow:view"
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_MANAGE = "workflow:manage"

    # Integration permissions
    INTEGRATION_VIEW = "integration:view"
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"
    INTEGRATION_MANAGE = "integration:manage"

    # User management permissions
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_AUDIT = "system:audit"


class RoleType(str, Enum):
    """Predefined role types."""

    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


# Forward declaration for association tables
class RolePermission(SQLModel, table=True):
    """Association table for Role-Permission many-to-many relationship."""

    __tablename__ = "role_permissions"

    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    permission_id: int = Field(foreign_key="permissions.id", primary_key=True)


class UserRole(SQLModel, table=True):
    """Association table for User-Role many-to-many relationship."""

    __tablename__ = "user_roles"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    granted_by: int = Field(foreign_key="users.id", description="User who granted this role")
    granted_at: str = Field(description="When the role was granted")
    expires_at: str | None = Field(default=None, description="When the role expires (optional)")


class Permission(BaseModel, table=True):
    """Permission model for RBAC."""

    __tablename__ = "permissions"

    name: str = Field(unique=True, index=True, description="Permission name")
    permission_type: PermissionType = Field(description="Permission type")
    description: str = Field(description="Permission description")
    resource_type: str = Field(description="Resource type this permission applies to")

    # Relationships
    roles: list["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class Role(BaseModel, table=True):
    """Role model for RBAC."""

    __tablename__ = "roles"

    name: str = Field(unique=True, index=True, description="Role name")
    role_type: RoleType = Field(description="Role type")
    description: str = Field(description="Role description")
    is_system_role: bool = Field(default=False, description="Whether this is a system-defined role")

    # Relationships
    permissions: list[Permission] = Relationship(back_populates="roles", link_model=RolePermission)
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)


class ResourcePermission(BaseModel, table=True):
    """Resource-specific permissions for fine-grained access control."""

    __tablename__ = "resource_permissions"

    user_id: int = Field(foreign_key="users.id", description="User ID")
    resource_type: str = Field(description="Type of resource (project, agent, etc.)")
    resource_id: int = Field(description="ID of the specific resource")
    permission_type: PermissionType = Field(description="Permission type")
    granted_by: int = Field(foreign_key="users.id", description="User who granted this permission")
    granted_at: str = Field(description="When the permission was granted")
    expires_at: str | None = Field(default=None, description="When the permission expires (optional)")


# Default role definitions
DEFAULT_ROLES = {
    RoleType.ADMIN: {
        "name": "System Administrator",
        "description": "Full system access and administration privileges",
        "permissions": [
            PermissionType.SYSTEM_ADMIN,
            PermissionType.SYSTEM_CONFIG,
            PermissionType.SYSTEM_MONITOR,
            PermissionType.SYSTEM_AUDIT,
            PermissionType.USER_MANAGE,
            PermissionType.PROJECT_MANAGE,
            PermissionType.AGENT_MANAGE,
            PermissionType.WORKFLOW_MANAGE,
            PermissionType.INTEGRATION_MANAGE,
        ],
    },
    RoleType.MANAGER: {
        "name": "Project Manager",
        "description": "Manage projects, agents, and team permissions",
        "permissions": [
            PermissionType.PROJECT_MANAGE,
            PermissionType.AGENT_MANAGE,
            PermissionType.WORKFLOW_MANAGE,
            PermissionType.INTEGRATION_VIEW,
            PermissionType.USER_VIEW,
            PermissionType.SYSTEM_MONITOR,
        ],
    },
    RoleType.DEVELOPER: {
        "name": "Developer",
        "description": "Create and execute agents and workflows",
        "permissions": [
            PermissionType.PROJECT_VIEW,
            PermissionType.PROJECT_CREATE,
            PermissionType.PROJECT_UPDATE,
            PermissionType.AGENT_VIEW,
            PermissionType.AGENT_CREATE,
            PermissionType.AGENT_UPDATE,
            PermissionType.AGENT_EXECUTE,
            PermissionType.WORKFLOW_VIEW,
            PermissionType.WORKFLOW_CREATE,
            PermissionType.WORKFLOW_UPDATE,
            PermissionType.WORKFLOW_EXECUTE,
            PermissionType.INTEGRATION_VIEW,
            PermissionType.INTEGRATION_CREATE,
        ],
    },
    RoleType.VIEWER: {
        "name": "Viewer",
        "description": "Read-only access to projects and results",
        "permissions": [
            PermissionType.PROJECT_VIEW,
            PermissionType.AGENT_VIEW,
            PermissionType.WORKFLOW_VIEW,
            PermissionType.INTEGRATION_VIEW,
        ],
    },
    RoleType.GUEST: {
        "name": "Guest",
        "description": "Limited read-only access",
        "permissions": [
            PermissionType.PROJECT_VIEW,
        ],
    },
}
