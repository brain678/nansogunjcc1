# app/presentation/api/v1/routers/users/routes.py

"""
User API Routes
HTTP endpoints for user management
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.application.services.user_application_service import UserApplicationService
from app.domain.services.user_service import UserService
from app.infrastructure.persistence.user_repository import UserRepository
from app.application.dtos.user_dto import (
    CreateUserRequest, UpdateUserRequest, AssignRoleRequest,
    ChangeUserStatusRequest, ConfigureMFARequest, AddOrganizationRequest,
    UserResponse, UserListResponse, CreateUserResponse,
    UserRolesResponse, UserOrganizationsResponse, UserStatusResponse
)
from app.common.exceptions import AppException, ValidationError, EntityNotFoundError


# Initialize router
router = APIRouter(prefix="/api/v1/users", tags=["users"])


# Dependency injection
async def get_user_application_service() -> UserApplicationService:
    """Get user application service"""
    repository = UserRepository()
    domain_service = UserService(repository)
    return UserApplicationService(domain_service)


# ============= USER MANAGEMENT ENDPOINTS =============

@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account"
)
async def create_user(
    request: CreateUserRequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Create new user"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        response = await service.create_user(request)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        import traceback
        logger.error(f"Error creating user: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
    description="Get paginated list of users"
)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """List all users"""
    try:
        if skip < 0 or limit < 1 or limit > 100:
            raise ValidationError("Invalid pagination parameters")
        
        response = await service.list_users(skip, limit)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
    description="Get user by ID"
)
async def get_user(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Get user by ID"""
    try:
        response = await service.get_user(user_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user profile information"
)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Update user"""
    try:
        response = await service.update_user(user_id, request)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete user (soft delete)"
)
async def delete_user(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Delete user"""
    try:
        success = await service.user_service.repository.delete(user_id)
        if not success:
            raise EntityNotFoundError(f"User {user_id} not found")
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============= ROLE MANAGEMENT ENDPOINTS =============

@router.post(
    "/{user_id}/roles",
    response_model=UserRolesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign role",
    description="Assign role to user"
)
async def assign_role(
    user_id: str,
    request: AssignRoleRequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Assign role to user"""
    try:
        response = await service.assign_role(user_id, request)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{user_id}/roles/{role}",
    response_model=UserRolesResponse,
    summary="Remove role",
    description="Remove role from user"
)
async def remove_role(
    user_id: str,
    role: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Remove role from user"""
    try:
        response = await service.remove_role(user_id, role)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============= STATUS MANAGEMENT ENDPOINTS =============

@router.post(
    "/{user_id}/status",
    response_model=UserStatusResponse,
    summary="Change status",
    description="Change user account status"
)
async def change_status(
    user_id: str,
    request: ChangeUserStatusRequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Change user status"""
    try:
        response = await service.change_status(user_id, request)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{user_id}/suspend",
    response_model=UserStatusResponse,
    summary="Suspend user",
    description="Suspend user account"
)
async def suspend_user(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Suspend user"""
    try:
        response = await service.suspend_user(user_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{user_id}/activate",
    response_model=UserStatusResponse,
    summary="Activate user",
    description="Activate user account"
)
async def activate_user(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Activate user"""
    try:
        response = await service.activate_user(user_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============= ORGANIZATION ENDPOINTS =============

@router.get(
    "/organization/{organization_id}/members",
    response_model=UserListResponse,
    summary="List organization users",
    description="Get users in organization"
)
async def list_organization_users(
    organization_id: str,
    skip: int = 0,
    limit: int = 50,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """List users in organization"""
    try:
        if skip < 0 or limit < 1 or limit > 100:
            raise ValidationError("Invalid pagination parameters")
        
        response = await service.list_organization_users(organization_id, skip, limit)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{user_id}/organizations",
    response_model=UserOrganizationsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add organization",
    description="Add user to organization"
)
async def add_organization(
    user_id: str,
    request: AddOrganizationRequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Add user to organization"""
    try:
        response = await service.add_organization(user_id, request)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{user_id}/organizations/{organization_id}",
    response_model=UserOrganizationsResponse,
    summary="Remove organization",
    description="Remove user from organization"
)
async def remove_organization(
    user_id: str,
    organization_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Remove user from organization"""
    try:
        response = await service.remove_organization(user_id, organization_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============= MFA ENDPOINTS =============

@router.post(
    "/{user_id}/mfa",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configure MFA",
    description="Enable MFA for user"
)
async def configure_mfa(
    user_id: str,
    request: ConfigureMFARequest,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Configure MFA for user"""
    try:
        response = await service.configure_mfa(user_id, request)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{user_id}/mfa",
    response_model=UserResponse,
    summary="Disable MFA",
    description="Disable MFA for user"
)
async def disable_mfa(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Disable MFA for user"""
    try:
        response = await service.disable_mfa(user_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============= QUERY ENDPOINTS =============

@router.get(
    "/role/{role}",
    response_model=UserListResponse,
    summary="List users by role",
    description="Get users with specific role"
)
async def list_users_by_role(
    role: str,
    skip: int = 0,
    limit: int = 50,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """List users by role"""
    try:
        if skip < 0 or limit < 1 or limit > 100:
            raise ValidationError("Invalid pagination parameters")
        
        response = await service.list_users_by_role(role, skip, limit)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/active/list",
    response_model=UserListResponse,
    summary="List active users",
    description="Get active user accounts"
)
async def list_active_users(
    skip: int = 0,
    limit: int = 50,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """List active users"""
    try:
        if skip < 0 or limit < 1 or limit > 100:
            raise ValidationError("Invalid pagination parameters")
        
        response = await service.list_active_users(skip, limit)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{user_id}/status",
    response_model=UserStatusResponse,
    summary="Get user status",
    description="Get user account status details"
)
async def get_user_status(
    user_id: str,
    service: UserApplicationService = Depends(get_user_application_service)
):
    """Get user status"""
    try:
        response = await service.get_user_status(user_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
