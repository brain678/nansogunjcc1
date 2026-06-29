"""
Value Objects for Digital Identity and QR System
"""

import re
import secrets
import string
from typing import Optional
from pydantic import BaseModel, field_validator


class MembershipID(BaseModel):
    """
    Membership ID value object - Format: NANS-YYYY-XXXXXX
    Example: NANS-2026-000001
    """
    
    value: str
    
    @field_validator('value')
    @classmethod
    def validate_membership_id(cls, v: str) -> str:
        """Validate membership ID format"""
        if not re.match(r'^NANS-\d{4}-\d{6}$', v):
            raise ValueError(
                f"Invalid membership ID format: {v}. Expected format: NANS-YYYY-XXXXXX"
            )
        return v
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, MembershipID):
            return self.value == other.value
        return self.value == other
    
    def __hash__(self):
        return hash(self.value)


class QRToken(BaseModel):
    """
    QR Token value object - Secure verification token for QR codes
    Format: 64-character hexadecimal string
    Generated using cryptographically secure random bytes
    """
    
    value: str
    
    @field_validator('value')
    @classmethod
    def validate_qr_token(cls, v: str) -> str:
        """Validate QR token format"""
        if not re.match(r'^[a-f0-9]{64}$', v):
            raise ValueError(
                f"Invalid QR token format. Expected 64-character hexadecimal string, got: {len(v)} chars"
            )
        return v
    
    @classmethod
    def generate(cls) -> 'QRToken':
        """Generate a new secure QR token"""
        # Generate 32 random bytes and convert to hex (64 characters)
        token = secrets.token_hex(32)
        return cls(value=token)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, QRToken):
            return self.value == other.value
        return self.value == other
    
    def __hash__(self):
        return hash(self.value)


class VerificationResponse(BaseModel):
    """
    Response for QR verification
    Contains member information without sensitive data
    """
    
    is_valid: bool
    user_id: str
    membership_id: str
    full_name: str
    role: str
    email: str
    
    # Organization Information
    institution: str
    chapter: str
    
    # Membership Information
    membership_status: str
    member_since: str
    
    # Profile
    profile_photo_url: Optional[str] = None
    
    # Verification Details
    verified_at: str
    verification_method: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "user_id": "507f1f77bcf86cd799439011",
                "membership_id": "NANS-2026-000001",
                "full_name": "John Doe",
                "role": "MEMBER",
                "email": "john@example.com",
                "institution": "University of Lagos",
                "chapter": "Lagos Chapter",
                "membership_status": "ACTIVE",
                "member_since": "2024-01-15",
                "profile_photo_url": "https://...",
                "verified_at": "2026-06-24T05:40:00Z",
                "verification_method": "QR_CODE"
            }
        }


class IDCardData(BaseModel):
    """Data structure for digital ID card"""
    
    membership_id: str
    full_name: str
    role: str
    email: str
    phone: Optional[str] = None
    institution: str
    chapter: str
    profile_photo_url: Optional[str] = None
    member_since: str
    membership_status: str
    qr_token: str
    card_issue_date: str
    card_expiry_date: Optional[str] = None


class QRCodeData(BaseModel):
    """Data structure for QR code content"""
    
    token: str
    verification_url: str
    member_id: str
    issued_at: str
    expires_at: Optional[str] = None
    type: str  # MEMBER_IDENTITY, MEETING_ATTENDANCE, etc
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456...",
                "verification_url": "https://nans.org/verify/abc123def456",
                "member_id": "NANS-2026-000001",
                "issued_at": "2026-06-24T00:00:00Z",
                "expires_at": "2027-06-24T00:00:00Z",
                "type": "MEMBER_IDENTITY"
            }
        }
