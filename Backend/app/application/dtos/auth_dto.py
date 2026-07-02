"""
Authentication DTOs - Data Transfer Objects for auth operations
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from datetime import datetime


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


# ============= Request DTOs =============

class LoginRequest(CamelModel):
    """User login request"""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }


class RefreshTokenRequest(CamelModel):
    """Refresh token request"""
    refresh_token: str = Field(description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ForgotPasswordRequest(CamelModel):
    """Forgot password request"""
    email: EmailStr = Field(description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class ResetPasswordRequest(CamelModel):
    """Reset password request"""
    token: str = Field(description="Password reset token")
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NewSecurePassword123!"
            }
        }


class ForgotPasswordResponse(CamelModel):
    """Forgot password response"""
    message: str = Field(description="Response message")
    reset_token: Optional[str] = Field(None, description="Password reset token")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password reset instructions sent.",
                "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class MessageResponse(CamelModel):
    """Generic message response"""
    message: str = Field(description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password has been reset successfully."
            }
        }


class RegisterRequest(CamelModel):
    """User registration request"""
    email: EmailStr = Field(description="User email address")
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, description="Phone number")
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, uppercase, lowercase, number, special char)"
    )
    
    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain special character")
        return v
    
    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "phone": "+1234567890",
                "password": "SecurePassword123!"
            }
        }


class ChangePasswordRequest(CamelModel):
    """Change password request"""
    current_password: str = Field(description="Current password")
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password"
    )
    new_password_confirm: str = Field(description="Confirm new password")
    
    @validator("new_password_confirm")
    def passwords_match(cls, v, values):
        """Verify passwords match"""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("New passwords do not match")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!"
            }
        }


class MFAEnableRequest(BaseModel):
    """Enable MFA request"""
    method: str = Field(description="MFA method (totp, sms, email, webauthn)")
    phone: Optional[str] = Field(None, description="Phone number for SMS method")
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "totp"
            }
        }


class MFAVerifyRequest(BaseModel):
    """Verify MFA request"""
    code: str = Field(min_length=6, max_length=6, description="OTP code for TOTP")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class MFABackupCodesRequest(BaseModel):
    """Generate backup codes request"""
    password: str = Field(description="User password for verification")
    count: int = Field(default=10, ge=5, le=20, description="Number of codes to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "SecurePassword123!",
                "count": 10
            }
        }


# ============= Response DTOs =============

class TokenResponse(CamelModel):
    """Token response"""
    access_token: str = Field(description="Access token")
    refresh_token: str = Field(description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }


class AccessTokenResponse(CamelModel):
    """Access token only response"""
    access_token: str = Field(description="Access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }


class ProfilePhotoResponse(CamelModel):
    """Profile photo upload response"""
    url: str = Field(description="Public URL of uploaded profile photo")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "http://localhost:8000/uploads/abcdef123456.jpg"
            }
        }


class UserResponse(BaseModel):
    """User response DTO"""
    id: str = Field(description="User ID")
    email: str = Field(description="User email")
    username: str = Field(description="Username")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    is_active: bool = Field(description="Is user active")
    is_email_verified: bool = Field(description="Is email verified")
    roles: list = Field(description="User roles")
    organization_id: str = Field(description="Organization ID")
    phone: Optional[str] = Field(None, description="Phone number")
    last_login_at: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(description="Account creation time")

    @field_validator("phone", mode="before")
    def normalize_phone(cls, value):
        if value is None:
            return None
        return str(value)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_email_verified": True,
                "roles": ["member"],
                "organization_id": "org_123",
                "last_login_at": "2024-06-23T10:30:00Z",
                "created_at": "2024-06-01T10:00:00Z"
            }
        }


class UserDetailResponse(UserResponse):
    """Detailed user response with additional info"""
    mfa_enabled: bool = Field(description="Is MFA enabled")
    mfa_method: Optional[str] = Field(None, description="MFA method")
    last_login_ip: Optional[str] = Field(None, description="Last login IP")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_email_verified": True,
                "roles": ["member"],
                "organization_id": "org_123",
                "mfa_enabled": True,
                "mfa_method": "totp",
                "last_login_at": "2024-06-23T10:30:00Z",
                "last_login_ip": "192.168.1.1",
                "created_at": "2024-06-01T10:00:00Z"
            }
        }


class AuthSuccessResponse(BaseModel):
    """Successful authentication response"""
    user: UserResponse = Field(description="User data")
    tokens: TokenResponse = Field(description="Token pair")
    mfa_required: bool = Field(default=False, description="Is MFA required")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user_123",
                    "email": "user@example.com",
                    "username": "john_doe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_email_verified": True,
                    "roles": ["member"],
                    "organization_id": "org_123",
                    "created_at": "2024-06-01T10:00:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900
                },
                "mfa_required": False
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(description="Error code")
    message: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "authentication_failed",
                "message": "Invalid email or password",
                "status_code": 401,
                "timestamp": "2024-06-23T10:30:00Z"
            }
        }


class MFASetupResponse(BaseModel):
    """MFA setup response"""
    method: str = Field(description="MFA method enabled")
    secret: Optional[str] = Field(None, description="Secret for TOTP (QR code)")
    backup_codes: Optional[list] = Field(None, description="Backup codes for recovery")
    message: str = Field(description="Setup instructions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "totp",
                "secret": "JBSWY3DPEBLW64TMMQ======",
                "backup_codes": [
                    "code1_backup",
                    "code2_backup"
                ],
                "message": "Scan QR code with authenticator app"
            }
        }


class UserProfileResponse(CamelModel):
    """User profile response - for current user"""
    id: str = Field(description="User ID")
    email: str = Field(description="User email")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    profile_photo_url: Optional[str] = Field(None, description="Profile photo URL")
    roles: list = Field(description="User roles")
    mfa_enabled: bool = Field(description="Is MFA enabled")
    status: str = Field(description="User status")
    membership_status: Optional[str] = Field(None, description="Membership status")
    membership_number: Optional[str] = Field(None, description="Membership number")
    membership_review_comments: Optional[str] = Field(None, description="Latest review or rejection reason")
    membership_rejected_at: Optional[datetime] = Field(None, description="Rejection timestamp")
    qr_token: Optional[str] = Field(None, description="Membership QR token")
    last_login_at: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(description="Account creation time")

    @field_validator("phone", mode="before")
    def normalize_phone(cls, value):
        if value is None:
            return None
        return str(value)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "roles": ["member"],
                "mfa_enabled": True,
                "status": "active",
                "last_login_at": "2024-06-23T10:30:00Z",
                "created_at": "2024-06-01T10:00:00Z"
            }
        }


class LoginResponse(CamelModel):
    """Login response"""
    user: UserProfileResponse = Field(description="User profile")
    token: TokenResponse = Field(description="Access and refresh tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user_123",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "roles": ["member"],
                    "mfa_enabled": False,
                    "status": "active",
                    "created_at": "2024-06-01T10:00:00Z"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900
                }
            }
        }


class LogoutResponse(CamelModel):
    """Logout response"""
    message: str = Field(description="Logout message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Successfully logged out"
            }
        }
