# app/application/dtos/user_dto.py

"""
User Data Transfer Objects
Request and response contracts for user operations
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


# ============= REQUEST DTOs =============

class CreateUserRequest(CamelModel):
    """Create user request"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=100)
    organization_id: str
    roles: Optional[List[str]] = Field(default_factory=lambda: ["member"])
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+234123456789",
                "password": "SecurePass123!",
                "organization_id": "org123",
                "roles": ["member"]
            }
        }


class UpdateUserRequest(CamelModel):
    """Update user request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    profile_photo_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+234987654321",
                "bio": "NANS Member",
                "profile_photo_url": "https://example.com/photo.jpg"
            }
        }


class AssignRoleRequest(BaseModel):
    """Assign role to user request"""
    role: str = Field(..., min_length=1)
    
    class Config:
        schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class ChangeUserStatusRequest(BaseModel):
    """Change user status request"""
    status: str = Field(..., min_length=1)
    reason: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "suspended",
                "reason": "Terms violation"
            }
        }


class ConfigureMFARequest(BaseModel):
    """Configure MFA request"""
    method: str = Field(..., description="MFA method: totp, sms, email, webauthn")
    
    class Config:
        schema_extra = {
            "example": {
                "method": "totp"
            }
        }


class AddOrganizationRequest(BaseModel):
    """Add user to organization request"""
    organization_id: str
    
    class Config:
        schema_extra = {
            "example": {
                "organization_id": "org456"
            }
        }


# ============= RESPONSE DTOs =============

class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    status: str
    roles: List[str]
    mfa_enabled: bool
    primary_organization_id: str
    organizations: List[str]
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "phone": "+234123456789",
                "bio": "NANS Member",
                "profile_photo_url": "https://example.com/photo.jpg",
                "status": "active",
                "roles": ["member"],
                "mfa_enabled": False,
                "primary_organization_id": "org123",
                "organizations": ["org123"],
                "last_login_at": "2026-06-23T10:00:00",
                "created_at": "2026-06-23T09:00:00",
                "updated_at": "2026-06-23T10:00:00"
            }
        }


class UserBriefResponse(BaseModel):
    """User brief response (summary)"""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    profile_photo_url: Optional[str] = None
    status: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "profile_photo_url": "https://example.com/photo.jpg",
                "status": "active"
            }
        }


class UserListResponse(BaseModel):
    """User list response"""
    total: int
    skip: int
    limit: int
    items: List[UserResponse]
    
    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "skip": 0,
                "limit": 10,
                "items": []
            }
        }


class CreateUserResponse(CamelModel):
    """Create user response"""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    status: str
    roles: List[str]
    primary_organization_id: str
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "user123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "status": "active",
                "roles": ["member"],
                "primary_organization_id": "org123",
                "created_at": "2026-06-23T09:00:00"
            }
        }


class UserRolesResponse(BaseModel):
    """User roles response"""
    user_id: str
    roles: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "roles": ["member", "admin"]
            }
        }


class UserOrganizationsResponse(BaseModel):
    """User organizations response"""
    user_id: str
    primary_organization_id: str
    organizations: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "primary_organization_id": "org123",
                "organizations": ["org123", "org456"]
            }
        }


class UserStatusResponse(BaseModel):
    """User status response"""
    user_id: str
    status: str
    last_login_at: Optional[datetime] = None
    is_locked: bool = False
    mfa_enabled: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "status": "active",
                "last_login_at": "2026-06-23T10:00:00",
                "is_locked": False,
                "mfa_enabled": False
            }
        }
