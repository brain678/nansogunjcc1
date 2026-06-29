# app/application/services/user_application_service.py

"""
User Application Service
Orchestrates user operations between DTOs and domain logic
"""

from typing import Optional, List
from app.domain.services.user_service import UserService
from app.domain.models.user import User, UserStatus, UserRole, MFAMethod
from app.common.models.value_objects import Email, Phone
from app.application.dtos.user_dto import (
    CreateUserRequest, UpdateUserRequest, AssignRoleRequest,
    ChangeUserStatusRequest, ConfigureMFARequest, AddOrganizationRequest,
    UserResponse, UserBriefResponse, UserListResponse, CreateUserResponse,
    UserRolesResponse, UserOrganizationsResponse, UserStatusResponse
)
from app.common.exceptions import ValidationError, EntityNotFoundError
from app.core.security.password_hasher import password_hasher


class UserApplicationService:
    """Application service for user operations"""
    
    def __init__(self, user_service: UserService):
        """
        Initialize user application service
        
        Args:
            user_service: Domain user service
        """
        self.user_service = user_service
    
    def _user_to_response(self, user: User) -> UserResponse:
        """Map User entity to UserResponse DTO"""
        return UserResponse(
            id=str(user.id),
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone.value if user.phone else None,
            bio=user.bio,
            profile_photo_url=user.profile_photo_url,
            status=user.status.value,
            roles=user.roles,
            mfa_enabled=user.mfa_enabled,
            primary_organization_id=user.primary_organization_id,
            organizations=user.organizations,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def _user_to_brief_response(self, user: User) -> UserBriefResponse:
        """Map User entity to UserBriefResponse DTO"""
        return UserBriefResponse(
            id=str(user.id),
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            profile_photo_url=user.profile_photo_url,
            status=user.status.value
        )
    
    async def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Create new user
        
        Args:
            request: Create user request
            
        Returns:
            Created user response
        """
        # Validate password strength
        if len(request.password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Create email value object
        try:
            email = Email(value=request.email)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Create phone value object if provided
        phone = None
        if request.phone:
            try:
                phone = Phone(value=request.phone)
            except ValueError as e:
                raise ValidationError(str(e))
        
        # Hash password
        password_hash = password_hasher.hash_password(request.password)
        
        # Create user via domain service
        user = await self.user_service.create_user(
            email=email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=phone,
            password_hash=password_hash,
            organization_id=request.organization_id,
            roles=request.roles
        )
        
        # Save to repository
        user = await self.user_service.repository.create(user)
        
        return CreateUserResponse(
            id=str(user.id),
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            status=user.status.value,
            roles=user.roles,
            primary_organization_id=user.primary_organization_id,
            created_at=user.created_at
        )
    
    async def get_user(self, user_id: str) -> UserResponse:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User response
        """
        user = await self.user_service.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        return self._user_to_response(user)
    
    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User response
        """
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise EntityNotFoundError(f"User with email {email} not found")
        
        return self._user_to_response(user)
    
    async def list_users(self, skip: int = 0, limit: int = 50) -> UserListResponse:
        """
        List all users
        
        Args:
            skip: Number to skip
            limit: Limit results
            
        Returns:
            User list response
        """
        users = await self.user_service.repository.find_all(skip, limit)
        total = await self.user_service.repository.count()
        
        return UserListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._user_to_response(u) for u in users]
        )
    
    async def list_organization_users(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> UserListResponse:
        """
        List users in organization
        
        Args:
            organization_id: Organization ID
            skip: Number to skip
            limit: Limit results
            
        Returns:
            User list response
        """
        users = await self.user_service.get_users_by_organization(
            organization_id, skip, limit
        )
        total = await self.user_service.repository.count_by_organization(organization_id)
        
        return UserListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._user_to_response(u) for u in users]
        )
    
    async def list_users_by_role(
        self,
        role: str,
        skip: int = 0,
        limit: int = 50
    ) -> UserListResponse:
        """
        List users by role
        
        Args:
            role: User role
            skip: Number to skip
            limit: Limit results
            
        Returns:
            User list response
        """
        users = await self.user_service.get_users_by_role(
            UserRole(role), skip, limit
        )
        
        return UserListResponse(
            total=len(users),
            skip=skip,
            limit=limit,
            items=[self._user_to_response(u) for u in users]
        )
    
    async def list_active_users(self, skip: int = 0, limit: int = 50) -> UserListResponse:
        """
        List active users
        
        Args:
            skip: Number to skip
            limit: Limit results
            
        Returns:
            User list response
        """
        users = await self.user_service.get_active_users(skip, limit)
        
        return UserListResponse(
            total=len(users),
            skip=skip,
            limit=limit,
            items=[self._user_to_response(u) for u in users]
        )
    
    async def update_user(
        self,
        user_id: str,
        request: UpdateUserRequest
    ) -> UserResponse:
        """
        Update user
        
        Args:
            user_id: User ID
            request: Update request
            
        Returns:
            Updated user response
        """
        phone = None
        if request.phone:
            phone = Phone(value=request.phone)
        
        user = await self.user_service.update_user(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=phone,
            bio=request.bio,
            profile_photo_url=request.profile_photo_url
        )
        
        # Save to repository
        user = await self.user_service.repository.update(user)
        
        return self._user_to_response(user)
    
    async def assign_role(
        self,
        user_id: str,
        request: AssignRoleRequest
    ) -> UserRolesResponse:
        """
        Assign role to user
        
        Args:
            user_id: User ID
            request: Assign role request
            
        Returns:
            User roles response
        """
        user = await self.user_service.assign_role(user_id, request.role)
        user = await self.user_service.repository.update(user)
        
        return UserRolesResponse(
            user_id=str(user.id),
            roles=user.roles
        )
    
    async def remove_role(
        self,
        user_id: str,
        role: str
    ) -> UserRolesResponse:
        """
        Remove role from user
        
        Args:
            user_id: User ID
            role: Role to remove
            
        Returns:
            User roles response
        """
        user = await self.user_service.remove_role(user_id, role)
        user = await self.user_service.repository.update(user)
        
        return UserRolesResponse(
            user_id=str(user.id),
            roles=user.roles
        )
    
    async def change_status(
        self,
        user_id: str,
        request: ChangeUserStatusRequest
    ) -> UserStatusResponse:
        """
        Change user status
        
        Args:
            user_id: User ID
            request: Status change request
            
        Returns:
            User status response
        """
        new_status = UserStatus(request.status)
        user = await self.user_service.change_status(user_id, new_status)
        user = await self.user_service.repository.update(user)
        
        return UserStatusResponse(
            user_id=str(user.id),
            status=user.status.value,
            last_login_at=user.last_login_at,
            is_locked=user.is_locked,
            mfa_enabled=user.mfa_enabled
        )
    
    async def suspend_user(self, user_id: str) -> UserStatusResponse:
        """
        Suspend user
        
        Args:
            user_id: User ID
            
        Returns:
            User status response
        """
        user = await self.user_service.suspend_user(user_id)
        user = await self.user_service.repository.update(user)
        
        return UserStatusResponse(
            user_id=str(user.id),
            status=user.status.value,
            is_locked=user.is_locked
        )
    
    async def activate_user(self, user_id: str) -> UserStatusResponse:
        """
        Activate user
        
        Args:
            user_id: User ID
            
        Returns:
            User status response
        """
        user = await self.user_service.activate_user(user_id)
        user = await self.user_service.repository.update(user)
        
        return UserStatusResponse(
            user_id=str(user.id),
            status=user.status.value,
            is_locked=user.is_locked
        )
    
    async def deactivate_user(self, user_id: str) -> UserStatusResponse:
        """
        Deactivate user
        
        Args:
            user_id: User ID
            
        Returns:
            User status response
        """
        user = await self.user_service.deactivate_user(user_id)
        user = await self.user_service.repository.update(user)
        
        return UserStatusResponse(
            user_id=str(user.id),
            status=user.status.value,
            is_locked=user.is_locked
        )
    
    async def add_organization(
        self,
        user_id: str,
        request: AddOrganizationRequest
    ) -> UserOrganizationsResponse:
        """
        Add user to organization
        
        Args:
            user_id: User ID
            request: Add organization request
            
        Returns:
            User organizations response
        """
        user = await self.user_service.add_organization(user_id, request.organization_id)
        user = await self.user_service.repository.update(user)
        
        return UserOrganizationsResponse(
            user_id=str(user.id),
            primary_organization_id=user.primary_organization_id,
            organizations=user.organizations
        )
    
    async def remove_organization(
        self,
        user_id: str,
        organization_id: str
    ) -> UserOrganizationsResponse:
        """
        Remove user from organization
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            
        Returns:
            User organizations response
        """
        user = await self.user_service.remove_organization(user_id, organization_id)
        user = await self.user_service.repository.update(user)
        
        return UserOrganizationsResponse(
            user_id=str(user.id),
            primary_organization_id=user.primary_organization_id,
            organizations=user.organizations
        )
    
    async def configure_mfa(
        self,
        user_id: str,
        request: ConfigureMFARequest
    ) -> UserResponse:
        """
        Configure MFA for user
        
        Args:
            user_id: User ID
            request: Configure MFA request
            
        Returns:
            Updated user response
        """
        import secrets
        
        method = MFAMethod(request.method)
        backup_codes = [secrets.token_urlsafe(8) for _ in range(10)]
        
        user = await self.user_service.configure_mfa(user_id, method, backup_codes)
        user = await self.user_service.repository.update(user)
        
        return self._user_to_response(user)
    
    async def disable_mfa(self, user_id: str) -> UserResponse:
        """
        Disable MFA for user
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user response
        """
        user = await self.user_service.disable_mfa(user_id)
        user = await self.user_service.repository.update(user)
        
        return self._user_to_response(user)
    
    async def get_user_status(self, user_id: str) -> UserStatusResponse:
        """
        Get user status details
        
        Args:
            user_id: User ID
            
        Returns:
            User status response
        """
        user = await self.user_service.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        return UserStatusResponse(
            user_id=str(user.id),
            status=user.status.value,
            last_login_at=user.last_login_at,
            is_locked=user.is_locked,
            mfa_enabled=user.mfa_enabled
        )
