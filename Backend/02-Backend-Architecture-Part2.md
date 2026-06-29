# Production-Grade FastAPI Backend - Part 2
## Authentication, Authorization, and Repository Layer

**Version:** 1.0  
**Date:** June 2026

---

## 3. Authentication Module

### 3.1 User Domain Model

```python
# app/domain/models/user.py

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator
from app.domain.entities.base_entity import BaseEntity
from app.domain.models.value_objects import Email, Phone, Address, Permission

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class UserRole(str, Enum):
    ADMIN = "admin"
    ORGANIZATION_ADMIN = "org_admin"
    CHAPTER_LEAD = "chapter_lead"
    MEMBER = "member"
    GUEST = "guest"

class MFAMethod(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    WEBAUTHN = "webauthn"

class UserSettings(BaseModel):
    timezone: str = "UTC"
    language: str = "en"
    email_notifications: bool = True
    sms_notifications: bool = False

class MFAConfig(BaseModel):
    method: MFAMethod
    is_configured: bool = False
    configured_at: Optional[datetime] = None
    backup_codes: List[str] = []

class User(BaseEntity):
    """User domain model"""
    
    email: Email
    phone: Optional[Phone] = None
    first_name: str
    last_name: str
    
    # Authentication
    password_hash: str
    password_changed_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Profile
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    addresses: List[Address] = []
    
    # MFA
    mfa_primary: Optional[MFAConfig] = None
    mfa_secondary: Optional[MFAConfig] = None
    mfa_enabled: bool = False
    
    # Status
    status: UserStatus = UserStatus.ACTIVE
    
    # Roles and Permissions
    roles: List[str] = []  # Role IDs
    permissions: List[Permission] = []
    
    # Organization
    primary_organization_id: str
    organizations: List[str] = []
    
    # Settings
    settings: UserSettings = Field(default_factory=UserSettings)
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self) -> bool:
        """Check if user is locked"""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until
    
    @property
    def is_mfa_enabled(self) -> bool:
        """Check if MFA is enabled"""
        return (
            self.mfa_enabled and
            self.mfa_primary and
            self.mfa_primary.is_configured
        )
    
    def increment_login_attempts(self) -> None:
        """Increment failed login attempts"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_login_attempts(self) -> None:
        """Reset login attempts on successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        from app.core.security import password_hasher
        return password_hasher.verify_password(password, self.password_hash)
    
    def set_password(self, password: str) -> None:
        """Set password hash"""
        from app.core.security import password_hasher
        self.password_hash = password_hasher.hash_password(password)
        self.password_changed_at = datetime.utcnow()
```

### 3.2 Authentication Service

```python
# app/domain/services/auth_service.py

from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.domain.models.user import User, UserStatus
from app.core.security import (
    jwt_handler, password_hasher, token_generator
)
from app.common.exceptions import (
    AuthenticationError, UserNotFoundError, UserLockedError
)

class AuthService:
    """Domain service for authentication logic"""
    
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    async def authenticate(
        self,
        email: str,
        password: str
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and return user + tokens
        
        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        # Get user by email
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(f"User {email} not found")
        
        # Check if user is locked
        if user.is_locked:
            raise UserLockedError(
                f"User account is locked until {user.locked_until}"
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError(
                f"User account is {user.status}"
            )
        
        # Verify password
        if not user.verify_password(password):
            user.increment_login_attempts()
            await self.user_repository.save(user)
            raise AuthenticationError("Invalid credentials")
        
        # Reset login attempts
        user.reset_login_attempts()
        await self.user_repository.save(user)
        
        # Generate tokens
        access_token = jwt_handler.create_access_token(
            subject=user.email.value,
            user_id=str(user.id),
            organization_id=user.primary_organization_id,
            roles=user.roles,
            permissions=[str(p) for p in user.permissions]
        )
        
        refresh_token = jwt_handler.create_refresh_token(
            subject=user.email.value,
            user_id=str(user.id)
        )
        
        return user, access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            payload = jwt_handler.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("user_id")
            user = await self.user_repository.get_by_id(user_id)
            
            if not user or user.status != UserStatus.ACTIVE:
                raise AuthenticationError("User not active")
            
            # Generate new access token
            access_token = jwt_handler.create_access_token(
                subject=user.email.value,
                user_id=str(user.id),
                organization_id=user.primary_organization_id,
                roles=user.roles,
                permissions=[str(p) for p in user.permissions]
            )
            
            return access_token
        
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def validate_token(self, token: str) -> dict:
        """Validate and decode token"""
        return jwt_handler.verify_token(token)
```

### 3.3 Application Auth Service

```python
# app/application/services/auth_service.py

from datetime import datetime
from app.domain.services.auth_service import AuthService as DomainAuthService
from app.application.dto.request_dto import LoginRequest, RefreshTokenRequest
from app.application.dto.response_dto import TokenResponse, UserResponse
from app.common.exceptions import ValidationError

class AuthService:
    """Application service for authentication"""
    
    def __init__(self, domain_auth_service: DomainAuthService):
        self.domain_auth_service = domain_auth_service
    
    async def login(self, request: LoginRequest) -> TokenResponse:
        """Login user and return tokens"""
        user, access_token, refresh_token = await self.domain_auth_service.authenticate(
            email=request.email,
            password=request.password
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=86400  # 24 hours
        )
    
    async def refresh(self, request: RefreshTokenRequest) -> TokenResponse:
        """Refresh access token"""
        access_token = await self.domain_auth_service.refresh_access_token(
            request.refresh_token
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400
        )
```

---

## 4. Permission Engine (RBAC)

### 4.1 Permission Engine

```python
# app/infrastructure/security/permission_engine.py

from typing import List, Optional, Set
from enum import Enum
from functools import lru_cache
from app.domain.models.value_objects import Permission

class ActionType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"

class Scope(str, Enum):
    OWN = "own"                    # Own resources only
    ORGANIZATION = "organization"  # Organization resources
    CHAPTER = "chapter"            # Chapter resources
    NATIONAL = "national"          # National/All resources

class PermissionMatrix:
    """Define permissions for each role"""
    
    PERMISSIONS = {
        "admin": [
            "users:create:national",
            "users:read:national",
            "users:update:national",
            "users:delete:national",
            "organizations:create:national",
            "organizations:read:national",
            "organizations:update:national",
            "organizations:delete:national",
            "meetings:create:national",
            "meetings:read:national",
            "meetings:update:national",
            "meetings:delete:national",
            "audit:read:national",
            "reports:read:national",
        ],
        "org_admin": [
            "users:create:organization",
            "users:read:organization",
            "users:update:organization",
            "users:delete:organization",
            "meetings:create:organization",
            "meetings:read:organization",
            "meetings:update:organization",
            "meetings:delete:organization",
            "activities:create:organization",
            "activities:read:organization",
            "activities:update:organization",
            "reports:read:organization",
        ],
        "chapter_lead": [
            "users:read:chapter",
            "meetings:create:chapter",
            "meetings:read:chapter",
            "meetings:update:chapter",
            "activities:create:chapter",
            "activities:read:chapter",
            "reports:read:chapter",
        ],
        "member": [
            "users:read:own",
            "users:update:own",
            "meetings:read:organization",
            "activities:read:organization",
            "documents:read:organization",
        ],
        "guest": [
            "meetings:read:organization",
        ],
    }
    
    @classmethod
    @lru_cache(maxsize=128)
    def get_permissions(cls, role: str) -> Set[str]:
        """Get permissions for role"""
        return set(cls.PERMISSIONS.get(role, []))
    
    @classmethod
    @lru_cache(maxsize=256)
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
        # Example: Check if user is owner for OWN scope
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
```

### 4.2 Permission Cache

```python
# app/infrastructure/cache/permission_cache.py

from typing import Set, List, Optional
import json
from datetime import timedelta

class PermissionCache:
    """Cache user permissions for performance"""
    
    def __init__(self, cache_service):
        self.cache_service = cache_service
        self.ttl = timedelta(hours=1)
    
    async def get_user_permissions(
        self,
        user_id: str
    ) -> Optional[Set[str]]:
        """Get cached user permissions"""
        key = f"permissions:{user_id}"
        cached = await self.cache_service.get(key)
        if cached:
            return set(json.loads(cached))
        return None
    
    async def set_user_permissions(
        self,
        user_id: str,
        permissions: Set[str]
    ) -> None:
        """Cache user permissions"""
        key = f"permissions:{user_id}"
        await self.cache_service.set(
            key,
            json.dumps(list(permissions)),
            self.ttl
        )
    
    async def invalidate_user_permissions(self, user_id: str) -> None:
        """Invalidate cached permissions"""
        key = f"permissions:{user_id}"
        await self.cache_service.delete(key)
    
    async def get_role_permissions(
        self,
        role: str
    ) -> Optional[Set[str]]:
        """Get cached role permissions"""
        key = f"role_permissions:{role}"
        cached = await self.cache_service.get(key)
        if cached:
            return set(json.loads(cached))
        return None
```

---

## 5. Repository Layer

### 5.1 Base Repository Interface

```python
# app/application/interfaces/repository.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from app.domain.entities.base_entity import BaseEntity

T = TypeVar('T', bound=BaseEntity)

class IRepository(ABC, Generic[T]):
    """Repository interface"""
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: Optional[str] = None
    ) -> List[T]:
        """Find all entities with pagination"""
        pass
    
    @abstractmethod
    async def find_one(self, **kwargs) -> Optional[T]:
        """Find single entity by criteria"""
        pass
    
    @abstractmethod
    async def find(self, **kwargs) -> List[T]:
        """Find entities by criteria"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity"""
        pass
    
    @abstractmethod
    async def count(self, **kwargs) -> int:
        """Count entities"""
        pass
    
    @abstractmethod
    async def exists(self, **kwargs) -> bool:
        """Check if entity exists"""
        pass
```

### 5.2 Beanie Repository Implementation

```python
# app/infrastructure/persistence/repository_base.py

from typing import Generic, TypeVar, List, Optional, Dict, Any
from beanie import Document
from app.application.interfaces.repository import IRepository
from app.common.exceptions import EntityNotFoundError

T = TypeVar('T', bound=Document)

class BeanieRepository(IRepository[T], Generic[T]):
    """Base repository implementation using Beanie ODM"""
    
    def __init__(self, model: type[T]):
        self.model = model
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        try:
            return await self.model.get(entity_id)
        except Exception:
            return None
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: Optional[str] = None
    ) -> List[T]:
        """Find all entities with pagination"""
        query = self.model.find()
        
        if sort_by:
            query = query.sort(sort_by, -1)
        
        return await query.skip(skip).limit(limit).to_list(None)
    
    async def find_one(self, **kwargs) -> Optional[T]:
        """Find single entity by criteria"""
        return await self.model.find_one(kwargs)
    
    async def find(self, **kwargs) -> List[T]:
        """Find entities by criteria"""
        return await self.model.find(kwargs).to_list(None)
    
    async def create(self, entity: T) -> T:
        """Create new entity"""
        return await entity.save()
    
    async def update(self, entity: T) -> T:
        """Update entity"""
        return await entity.save()
    
    async def delete(self, entity_id: str) -> bool:
        """Delete entity"""
        entity = await self.get_by_id(entity_id)
        if not entity:
            raise EntityNotFoundError(f"Entity {entity_id} not found")
        await entity.delete()
        return True
    
    async def count(self, **kwargs) -> int:
        """Count entities"""
        if kwargs:
            return await self.model.find(kwargs).count()
        return await self.model.find_all().count()
    
    async def exists(self, **kwargs) -> bool:
        """Check if entity exists"""
        entity = await self.find_one(**kwargs)
        return entity is not None
```

### 5.3 User Repository

```python
# app/infrastructure/persistence/user_repository.py

from typing import Optional, List
from app.infrastructure.persistence.repository_base import BeanieRepository
from app.models.user import User

class UserRepository(BeanieRepository[User]):
    """User repository"""
    
    def __init__(self):
        super().__init__(User)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return await self.find_one(email=email.lower())
    
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """Find user by phone"""
        return await self.find_one(phone=phone)
    
    async def find_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Find users by organization"""
        users = await self.model.find(
            {"organizations": org_id}
        ).skip(skip).limit(limit).to_list(None)
        return users
    
    async def find_active_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Find active users"""
        return await self.model.find(
            {"status": "active"}
        ).skip(skip).limit(limit).to_list(None)
    
    async def find_by_role(
        self,
        role_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Find users by role"""
        users = await self.model.find(
            {"roles": role_id}
        ).skip(skip).limit(limit).to_list(None)
        return users
    
    async def count_by_organization(self, org_id: str) -> int:
        """Count users in organization"""
        return await self.model.find(
            {"organizations": org_id}
        ).count()
```

### 5.4 Unit of Work Pattern

```python
# app/infrastructure/persistence/unit_of_work.py

from app.infrastructure.persistence.user_repository import UserRepository
from app.infrastructure.persistence.meeting_repository import MeetingRepository
from app.infrastructure.persistence.organization_repository import OrganizationRepository

class UnitOfWork:
    """Unit of Work pattern for transactional operations"""
    
    def __init__(self):
        self.users = UserRepository()
        self.meetings = MeetingRepository()
        self.organizations = OrganizationRepository()
        self._session = None
    
    async def __aenter__(self):
        """Context manager entry"""
        from app.core.database import db_manager
        self._session = await db_manager.client.start_session()
        self._session.start_transaction()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            await self._session.abort_transaction()
        else:
            await self._session.commit_transaction()
        self._session.end_session()
    
    async def commit(self):
        """Commit transaction"""
        if self._session:
            await self._session.commit_transaction()
    
    async def rollback(self):
        """Rollback transaction"""
        if self._session:
            await self._session.abort_transaction()
```

---

## 6. Application Service Layer

### 6.1 User Service

```python
# app/application/services/user_service.py

from typing import Optional, List
from app.domain.models.user import User, UserStatus
from app.application.dto.request_dto import CreateUserRequest, UpdateUserRequest
from app.application.dto.response_dto import UserResponse
from app.application.dto.mapper import UserMapper
from app.infrastructure.persistence.user_repository import UserRepository
from app.common.exceptions import (
    EntityNotFoundError, ValidationError, DuplicateResourceError
)

class UserService:
    """Application service for user operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository
        self.mapper = UserMapper()
    
    async def create_user(
        self,
        request: CreateUserRequest,
        org_id: str
    ) -> UserResponse:
        """Create new user"""
        # Check if user already exists
        existing = await self.repository.find_by_email(request.email)
        if existing:
            raise DuplicateResourceError(f"User {request.email} already exists")
        
        # Create user
        user = User(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            primary_organization_id=org_id,
            organizations=[org_id]
        )
        user.set_password(request.password)
        
        # Save to repository
        saved_user = await self.repository.create(user)
        
        return self.mapper.to_response(saved_user)
    
    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        return self.mapper.to_response(user)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[UserResponse]:
        """List users"""
        users = await self.repository.find_all(skip=skip, limit=limit)
        return [self.mapper.to_response(u) for u in users]
    
    async def update_user(
        self,
        user_id: str,
        request: UpdateUserRequest
    ) -> UserResponse:
        """Update user"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        # Update fields
        if request.first_name:
            user.first_name = request.first_name
        if request.last_name:
            user.last_name = request.last_name
        if request.phone:
            user.phone = request.phone
        
        # Save
        updated = await self.repository.update(user)
        return self.mapper.to_response(updated)
    
    async def delete_user(self, user_id: str) -> None:
        """Delete user"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        await self.repository.delete(user_id)
    
    async def suspend_user(self, user_id: str) -> UserResponse:
        """Suspend user"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found")
        
        user.status = UserStatus.SUSPENDED
        updated = await self.repository.update(user)
        return self.mapper.to_response(updated)
```

### 6.2 DTO and Mapper

```python
# app/application/dto/request_dto.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(..., min_length=12)
    phone: Optional[str] = None

class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# app/application/dto/response_dto.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    status: str
    created_at: datetime
    last_login_at: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

# app/application/dto/mapper.py

from app.domain.models.user import User
from app.application.dto.response_dto import UserResponse

class UserMapper:
    """Map between domain models and DTOs"""
    
    @staticmethod
    def to_response(user: User) -> UserResponse:
        """Convert User to UserResponse"""
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            first_name=user.first_name,
            last_name=user.last_name,
            phone=str(user.phone) if user.phone else None,
            status=user.status.value,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
```

This completes Part 2. Let me continue with Part 3: API Layer, Middleware, and Exception Handling.
