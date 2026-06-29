"""API dependencies for authentication and authorization"""

from fastapi import Depends, HTTPException, Request
from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.security.permission_engine import Scope, get_permission_engine
from app.infrastructure.persistence.user_repository import UserRepository
from app.core.config import settings


async def get_current_user(request: Request):
    """Extract and validate current user from JWT token"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = auth_header[7:]
    jwt_handler = JWTHandler(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = jwt_handler.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    user = await UserRepository().get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_current_user_id(current_user = Depends(get_current_user)) -> str:
    """Extract the current authenticated user's ID"""
    return str(current_user.id)


def require_permission(user, resource: str, action: str, scope: str, context: dict | None = None):
    """Ensure current user has required permission"""
    permission_engine = get_permission_engine()

    if scope == "any":
        required_permissions = [
            (resource, action, Scope.OWN.value),
            (resource, action, Scope.ORGANIZATION.value),
            (resource, action, Scope.CHAPTER.value),
            (resource, action, Scope.NATIONAL.value),
        ]
        if not permission_engine.has_any_permission(user.roles, required_permissions):
            raise HTTPException(status_code=403, detail="Forbidden")
        return

    if not permission_engine.has_permission(
        user.roles,
        resource,
        action,
        scope,
        context or {}
    ):
        raise HTTPException(status_code=403, detail="Forbidden")


def require_any_permission(user, permissions: list[tuple[str, str, str]], context: dict | None = None):
    """Ensure current user has any of the required permissions"""
    permission_engine = get_permission_engine()
    expanded_permissions: list[tuple[str, str, str]] = []
    for resource, action, scope in permissions:
        if scope == "any":
            expanded_permissions.extend([
                (resource, action, Scope.OWN.value),
                (resource, action, Scope.ORGANIZATION.value),
                (resource, action, Scope.CHAPTER.value),
                (resource, action, Scope.NATIONAL.value),
            ])
        else:
            expanded_permissions.append((resource, action, scope))

    if not permission_engine.has_any_permission(user.roles, expanded_permissions):
        raise HTTPException(status_code=403, detail="Forbidden")
