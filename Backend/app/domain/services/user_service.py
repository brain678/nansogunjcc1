# app/domain/services/user_service.py

"""
User Domain Service - Business logic for user operations
Encapsulates core user domain rules and workflows
"""

from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.models.user import User, UserStatus, UserRole, MFAMethod
from app.common.models.value_objects import Email, Phone, Address
from app.common.exceptions import ValidationError, EntityNotFoundError


class UserService:
    """Domain service for user operations"""
    
    def __init__(self, user_repository):
        """
        Initialize user service
        
        Args:
            user_repository: User repository for data access
        """
        self.repository = user_repository
    
    async def create_user(
        self,
        email: Email,
        first_name: str,
        last_name: str,
        phone: Optional[Phone] = None,
        password_hash: str = "",
        organization_id: str = None,
        roles: Optional[List[str]] = None
    ) -> User:
        """
        Create new user
        
        Args:
            email: User email
            first_name: First name
            last_name: Last name
            phone: Optional phone number
            password_hash: Password hash (empty if not set)
            organization_id: Primary organization ID
            roles: Initial roles (defaults to ["member"])
            
        Returns:
            Created user
            
        Raises:
            ValidationError: If validation fails
        """
        # Validation
        if not email or not first_name or not last_name:
            raise ValidationError("Email, first name, and last name are required")
        
        if len(first_name.strip()) == 0 or len(last_name.strip()) == 0:
            raise ValidationError("First name and last name cannot be empty")
        
        # Check if email already exists
        existing_user = await self.repository.find_by_email(email.value)
        if existing_user:
            raise ValidationError(f"User with email {email.value} already exists")
        
        # Create user
        user = User(
            email=email,
            phone=phone,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            password_hash=password_hash,
            primary_organization_id=organization_id,
            organizations=[organization_id] if organization_id else [],
            roles=roles or ["member"],
            status=UserStatus.ACTIVE
        )
        
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        if not user_id:
            raise ValidationError("User ID cannot be empty")
        
        return await self.repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        if not email:
            raise ValidationError("Email cannot be empty")
        
        return await self.repository.find_by_email(email)
    
    async def get_users_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get users by organization
        
        Args:
            organization_id: Organization ID
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        if not organization_id:
            raise ValidationError("Organization ID cannot be empty")
        
        if limit > 100:
            limit = 100  # Max limit
        
        return await self.repository.find_by_organization(
            organization_id, skip, limit
        )
    
    async def get_users_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get users by role
        
        Args:
            role: User role
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        if not role:
            raise ValidationError("Role cannot be empty")
        
        if limit > 100:
            limit = 100
        
        return await self.repository.find_by_role(role.value, skip, limit)
    
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Get active users
        
        Args:
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of active users
        """
        if limit > 100:
            limit = 100
        
        return await self.repository.find_by_status(UserStatus.ACTIVE.value, skip, limit)
    
    async def update_user(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[Phone] = None,
        bio: Optional[str] = None,
        profile_photo_url: Optional[str] = None
    ) -> User:
        """
        Update user profile
        
        Args:
            user_id: User ID
            first_name: New first name
            last_name: New last name
            phone: New phone
            bio: New bio
            profile_photo_url: New profile photo URL
            
        Returns:
            Updated user
            
        Raises:
            EntityNotFoundError: If user not found
            ValidationError: If validation fails
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        # Update fields
        if first_name:
            if len(first_name.strip()) == 0:
                raise ValidationError("First name cannot be empty")
            user.first_name = first_name.strip()
        
        if last_name:
            if len(last_name.strip()) == 0:
                raise ValidationError("Last name cannot be empty")
            user.last_name = last_name.strip()
        
        if phone is not None:
            user.phone = phone
        
        if bio is not None:
            user.bio = bio
        
        if profile_photo_url is not None:
            user.profile_photo_url = profile_photo_url
        
        user.updated_at = datetime.utcnow()
        return user
    
    async def assign_role(self, user_id: str, role: str) -> User:
        """
        Assign role to user
        
        Args:
            user_id: User ID
            role: Role to assign
            
        Returns:
            Updated user
            
        Raises:
            EntityNotFoundError: If user not found
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        if role not in user.roles:
            user.roles.append(role)
            user.updated_at = datetime.utcnow()
        
        return user
    
    async def remove_role(self, user_id: str, role: str) -> User:
        """
        Remove role from user
        
        Args:
            user_id: User ID
            role: Role to remove
            
        Returns:
            Updated user
            
        Raises:
            EntityNotFoundError: If user not found
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        if role in user.roles:
            user.roles.remove(role)
            user.updated_at = datetime.utcnow()
        
        # Ensure user has at least member role
        if not user.roles:
            user.roles = ["member"]
        
        return user
    
    async def change_status(self, user_id: str, new_status: UserStatus) -> User:
        """
        Change user status
        
        Args:
            user_id: User ID
            new_status: New status
            
        Returns:
            Updated user
            
        Raises:
            EntityNotFoundError: If user not found
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.status = new_status
        user.updated_at = datetime.utcnow()
        
        return user
    
    async def suspend_user(self, user_id: str, reason: Optional[str] = None) -> User:
        """
        Suspend user account
        
        Args:
            user_id: User ID
            reason: Optional suspension reason
            
        Returns:
            Updated user
        """
        return await self.change_status(user_id, UserStatus.SUSPENDED)
    
    async def activate_user(self, user_id: str) -> User:
        """
        Activate user account
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        return await self.change_status(user_id, UserStatus.ACTIVE)
    
    async def deactivate_user(self, user_id: str) -> User:
        """
        Deactivate user account
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        return await self.change_status(user_id, UserStatus.INACTIVE)
    
    async def add_organization(self, user_id: str, organization_id: str) -> User:
        """
        Add user to organization
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            
        Returns:
            Updated user
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        if organization_id not in user.organizations:
            user.organizations.append(organization_id)
            user.updated_at = datetime.utcnow()
        
        return user
    
    async def remove_organization(self, user_id: str, organization_id: str) -> User:
        """
        Remove user from organization
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            
        Returns:
            Updated user
            
        Raises:
            ValidationError: If trying to remove primary organization
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        if organization_id == user.primary_organization_id:
            raise ValidationError("Cannot remove primary organization")
        
        if organization_id in user.organizations:
            user.organizations.remove(organization_id)
            user.updated_at = datetime.utcnow()
        
        return user
    
    async def check_is_locked(self, user_id: str) -> bool:
        """
        Check if user is locked due to failed login attempts
        
        Args:
            user_id: User ID
            
        Returns:
            True if locked, False otherwise
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        return user.is_locked
    
    async def increment_login_attempts(self, user_id: str) -> User:
        """
        Increment login attempts and lock if needed
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.increment_login_attempts()
        return user
    
    async def reset_login_attempts(self, user_id: str) -> User:
        """
        Reset login attempts on successful login
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.reset_login_attempts()
        return user
    
    async def configure_mfa(
        self,
        user_id: str,
        method: MFAMethod,
        backup_codes: List[str]
    ) -> User:
        """
        Configure MFA for user
        
        Args:
            user_id: User ID
            method: MFA method
            backup_codes: Backup codes
            
        Returns:
            Updated user
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.configure_mfa(method, backup_codes)
        user.mfa_enabled = True
        user.updated_at = datetime.utcnow()
        
        return user
    
    async def disable_mfa(self, user_id: str) -> User:
        """
        Disable MFA for user
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        user = await self.get_user(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.mfa_primary = None
        user.mfa_secondary = None
        user.mfa_enabled = False
        user.updated_at = datetime.utcnow()
        
        return user
    
    async def get_user_count(self, organization_id: Optional[str] = None) -> int:
        """
        Get count of users
        
        Args:
            organization_id: Optional organization filter
            
        Returns:
            User count
        """
        if organization_id:
            return await self.repository.count_by_organization(organization_id)
        return await self.repository.count()
