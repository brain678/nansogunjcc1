# app/domain/models/user.py

import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from app.common.models.base_entity import BaseEntity
from app.common.models.value_objects import Email, Phone, Address, Permission


class UserStatus(str, Enum):
    """User status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User role enum"""
    ADMIN = "admin"
    GENERAL_SECRETARY = "general_secretary"
    CHAIRMAN = "chairman"
    MEMBER = "member"


class MFAMethod(str, Enum):
    """MFA method enum"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    WEBAUTHN = "webauthn"


class UserSettings(BaseModel):
    """User settings"""
    timezone: str = "UTC"
    language: str = "en"
    email_notifications: bool = True
    sms_notifications: bool = False


class MFAConfig(BaseModel):
    """MFA configuration"""
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
        """Verify password - implementation will use app.core.security"""
        from app.core.security.password_hasher import password_hasher
        return password_hasher.verify_password(password, self.password_hash)
    
    def set_password(self, password: str) -> None:
        """Set password hash"""
        from app.core.security.password_hasher import password_hasher
        self.password_hash = password_hasher.hash_password(password)
        self.password_changed_at = datetime.utcnow()
    
    def configure_mfa(
        self,
        method: MFAMethod,
        backup_codes: List[str]
    ) -> None:
        """Configure MFA"""
        config = MFAConfig(
            method=method,
            is_configured=True,
            configured_at=datetime.utcnow(),
            backup_codes=backup_codes
        )
        
        if self.mfa_primary is None:
            self.mfa_primary = config
        else:
            self.mfa_secondary = config
        
        if self.mfa_primary and self.mfa_primary.is_configured:
            self.mfa_enabled = True
    
    def disable_mfa(self, method: Optional[MFAMethod] = None) -> None:
        """Disable MFA"""
        if method is None:
            self.mfa_primary = None
            self.mfa_secondary = None
            self.mfa_enabled = False
        else:
            if self.mfa_primary and self.mfa_primary.method == method:
                self.mfa_primary = None
            elif self.mfa_secondary and self.mfa_secondary.method == method:
                self.mfa_secondary = None
            
            # Disable MFA if no methods are configured
            if not self.mfa_primary or not self.mfa_primary.is_configured:
                self.mfa_enabled = False
    
    def is_organization_member(self, org_id: str) -> bool:
        """Check if user is member of organization"""
        return org_id in self.organizations
    
    def add_organization(self, org_id: str) -> None:
        """Add organization membership"""
        if org_id not in self.organizations:
            self.organizations.append(org_id)
    
    def remove_organization(self, org_id: str) -> None:
        """Remove organization membership"""
        if org_id in self.organizations:
            self.organizations.remove(org_id)
    
    def disable_mfa(self) -> None:
        """Disable MFA for user"""
        self.mfa_config.enabled = False
        self.mfa_config.method = None
        self.mfa_config.secret = None
        self.mfa_config.phone = None
        self.mfa_config.verified = False
        self.mfa_config.backup_codes = []
        self.updated_at = datetime.utcnow()
    
    def verify_mfa(self) -> None:
        """Mark MFA as verified"""
        self.mfa_config.verified = True
        self.updated_at = datetime.utcnow()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for MFA recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of generated backup codes
        """
        import secrets
        
        codes = [secrets.token_urlsafe(8) for _ in range(count)]
        self.mfa_config.backup_codes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]
        self.updated_at = datetime.utcnow()
        
        return codes
    
    def use_backup_code(self, code: str) -> bool:
        """
        Use a backup code for MFA recovery
        
        Args:
            code: Backup code to verify
            
        Returns:
            True if code is valid, False otherwise
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash in self.mfa_config.backup_codes:
            self.mfa_config.backup_codes.remove(code_hash)
            self.updated_at = datetime.utcnow()
            return True
        
        return False
    
    def soft_delete(self) -> None:
        """Soft delete user (mark as deleted but keep data)"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft-deleted user"""
        self.deleted_at = None
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def add_role(self, role: str) -> None:
        """Add role to user"""
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.utcnow()
    
    def remove_role(self, role: str) -> None:
        """Remove role from user"""
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def add_permission(self, permission: str) -> None:
        """Add permission to user"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.utcnow()
    
    def remove_permission(self, permission: str) -> None:
        """Remove permission from user"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.updated_at = datetime.utcnow()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def get_display_name(self) -> str:
        """Get user's display name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def __hash__(self):
        """Make user hashable for caching"""
        return hash(self.id)
    
    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, User):
            return self.id == other.id
        return False
