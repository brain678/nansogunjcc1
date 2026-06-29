# app/infrastructure/security/permission_engine.py

from typing import List, Optional, Set
from enum import Enum
from functools import lru_cache


class ActionType(str, Enum):
    """Action types for permissions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"


class Scope(str, Enum):
    """Permission scope"""
    OWN = "own"                    # Own resources only
    ORGANIZATION = "organization"  # Organization resources
    CHAPTER = "chapter"            # Chapter resources
    NATIONAL = "national"          # National/All resources


class PermissionMatrix:
    """Define permissions for each role"""
    
    PERMISSIONS = {
        "admin": [
            # Full system access - user management
            "users:create:national",
            "users:read:national",
            "users:update:national",
            "users:delete:national",
            # Organization management
            "organizations:create:national",
            "organizations:read:national",
            "organizations:update:national",
            "organizations:delete:national",
            # Meetings
            "meetings:create:national",
            "meetings:read:national",
            "meetings:update:national",
            "meetings:delete:national",
            "meetings:approve:national",
            # Activities
            "activities:create:national",
            "activities:read:national",
            "activities:update:national",
            "activities:delete:national",
            # Memberships
            "members:read:national",
            "members:approve:national",
            "members:reject:national",
            "members:update:national",
            # Audit and reports
            "audit:read:national",
            "reports:read:national",
            "reports:create:national",
            "settings:update:national",
        ],
        "general_secretary": [
            # User management
            "users:create:organization",
            "users:read:organization",
            "users:update:organization",
            "users:delete:organization",
            # Meetings management
            "meetings:create:organization",
            "meetings:read:organization",
            "meetings:update:organization",
            "meetings:delete:organization",
            "meetings:approve:organization",
            # Activities management
            "activities:create:organization",
            "activities:read:organization",
            "activities:update:organization",
            "activities:delete:organization",
            # Memberships
            "members:read:organization",
            "members:approve:organization",
            "members:reject:organization",
            "members:update:organization",
            # Documents
            "documents:read:organization",
            "documents:create:organization",
            "documents:update:organization",
            # Reports
            "reports:read:organization",
            "reports:create:organization",
        ],
        "chairman": [
            # User access
            "users:read:organization",
            # Meetings - approval authority
            "meetings:read:organization",
            "meetings:approve:organization",
            "meetings:reject:organization",
            # Memberships
            "members:read:organization",
            "members:approve:organization",
            "members:reject:organization",
            "members:update:organization",
            # Activities oversight
            "activities:read:organization",
            "activities:approve:organization",
            # Reports access
            "reports:read:organization",
            "reports:create:organization",
        ],
        "member": [
            # Own user profile
            "users:read:own",
            "users:update:own",
            # Meetings access (read-only)
            "meetings:read:organization",
            # Activities access (read-only)
            "activities:read:organization",
            # Documents access (read-only)
            "documents:read:organization",
        ],
    }
    
    @classmethod
    @lru_cache(maxsize=256)
    def get_permissions(cls, role: str) -> Set[str]:
        """Get permissions for role"""
        return set(cls.PERMISSIONS.get(role, []))
    
    @classmethod
    @lru_cache(maxsize=512)
    def has_permission(
        cls,
        role: str,
        resource: str,
        action: str,
        scope: str
    ) -> bool:
        """Check if role has permission"""
        permission = f"{resource}:{action}:{scope}"
        permissions = cls.get_permissions(role)
        return permission in permissions


class PermissionEngine:
    """RBAC permission engine"""
    
    def __init__(self):
        self.permission_matrix = PermissionMatrix()
    
    def has_permission(
        self,
        user_roles: List[str],
        resource: str,
        action: str,
        scope: str = Scope.OWN,
        context: Optional[dict] = None
    ) -> bool:
        """
        Check if user has permission
        
        Args:
            user_roles: List of user roles
            resource: Resource name (users, meetings, etc.)
            action: Action (create, read, update, delete)
            scope: Scope (own, organization, national)
            context: Additional context for permission check
        
        Returns:
            True if user has permission
        """
        for role in user_roles:
            if self.permission_matrix.has_permission(
                role, resource, action, scope
            ):
                # Perform additional checks if context provided
                if context:
                    if self._evaluate_context(role, scope, context):
                        return True
                else:
                    return True
        
        return False
    
    def has_any_permission(
        self,
        user_roles: List[str],
        required_permissions: List[tuple]
    ) -> bool:
        """Check if user has any of the required permissions"""
        for resource, action, scope in required_permissions:
            if self.has_permission(user_roles, resource, action, scope):
                return True
        return False
    
    def has_all_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[tuple]
    ) -> bool:
        """Check if user has all required permissions"""
        for resource, action, scope in required_permissions:
            if not self.has_permission(user_roles, resource, action, scope):
                return False
        return True
    
    def filter_accessible_resources(
        self,
        user_roles: List[str],
        resource: str,
        action: str,
        resources: List[dict]
    ) -> List[dict]:
        """Filter resources based on permissions"""
        accessible = []
        for res in resources:
            scope = res.get("scope", Scope.OWN)
            if self.has_permission(user_roles, resource, action, scope):
                accessible.append(res)
        return accessible
    
    def _evaluate_context(
        self,
        role: str,
        scope: str,
        context: dict
    ) -> bool:
        """Evaluate additional context for permission"""
        # Check if user is owner for OWN scope
        if scope == Scope.OWN:
            user_id = context.get("user_id")
            resource_owner = context.get("owner_id")
            return user_id == resource_owner
        
        # Check organization membership
        if scope in [Scope.ORGANIZATION, Scope.CHAPTER]:
            user_org_id = context.get("user_org_id")
            resource_org_id = context.get("resource_org_id")
            return user_org_id == resource_org_id
        
        return True


# Global instance
_permission_engine: Optional[PermissionEngine] = None


def get_permission_engine() -> PermissionEngine:
    """Get or create permission engine"""
    global _permission_engine
    if _permission_engine is None:
        _permission_engine = PermissionEngine()
    return _permission_engine
