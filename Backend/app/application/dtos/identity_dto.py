"""
DTOs for Digital Identity and QR System APIs
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Identity Generation DTOs ====================

class CreateIdentityRequest(BaseModel):
    """Request to create digital identity"""
    role: str = Field(..., description="User role: ADMIN, GENERAL_SECRETARY, CHAIRMAN, MEMBER")
    institution: str = Field(default="Not Specified", description="User's institution")
    chapter: str = Field(default="General", description="User's chapter")
    profile_photo_url: Optional[str] = Field(None, description="URL to profile photo")


class IdentityResponse(BaseModel):
    """Response with identity information"""
    user_id: str
    membership_id: str
    qr_token: str
    card_status: str
    role: str
    created_at: str


# ==================== Digital Card DTOs ====================

class DigitalCardResponse(BaseModel):
    """Response with digital card information"""
    membership_id: str
    full_name: str
    role: str
    email: str
    phone: Optional[str] = None
    institution: str
    chapter: str
    profile_photo_url: Optional[str] = None
    member_since: str
    card_issue_date: str
    card_expiry_date: Optional[str] = None
    card_status: str
    qr_token: str
    verification_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "membership_id": "NANS-2026-000001",
                "full_name": "John Doe",
                "role": "MEMBER",
                "email": "john@example.com",
                "phone": "+2341234567890",
                "institution": "University of Lagos",
                "chapter": "Lagos Chapter",
                "profile_photo_url": "https://...",
                "member_since": "2024-01-15T10:00:00",
                "card_issue_date": "2026-01-15T10:00:00",
                "card_expiry_date": "2027-01-15T10:00:00",
                "card_status": "ACTIVE",
                "qr_token": "abc123def456...",
                "verification_count": 5
            }
        }


class CardStatusResponse(BaseModel):
    """Response with card status"""
    membership_id: str
    card_status: str
    is_active: bool
    verification_count: int
    last_verified_at: Optional[str] = None
    created_at: str


class RegenerateQRResponse(BaseModel):
    """Response when QR code is regenerated"""
    membership_id: str
    qr_token: str
    last_rotated_at: Optional[str] = None
    message: str = "QR code regenerated successfully"


class DisableCardResponse(BaseModel):
    """Response when card is disabled"""
    membership_id: str
    card_status: str
    message: str = "ID card disabled successfully"


class ActivateCardResponse(BaseModel):
    """Response when card is activated"""
    membership_id: str
    card_status: str
    message: str = "ID card activated successfully"


# ==================== QR Verification DTOs ====================

class VerifyQRRequest(BaseModel):
    """Request to verify QR token"""
    qr_token: str = Field(..., description="QR token to verify")


class VerifyQRResponse(BaseModel):
    """Response from QR verification"""
    is_valid: bool
    user_id: str
    membership_id: str
    full_name: str
    role: str
    email: str
    institution: str
    chapter: str
    membership_status: str
    member_since: str
    profile_photo_url: Optional[str] = None
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


class InvalidQRResponse(BaseModel):
    """Response when QR verification fails"""
    is_valid: bool = False
    detail: str
    timestamp: str


# ==================== Meeting QR DTOs ====================

class CreateMeetingQRRequest(BaseModel):
    """Request to create meeting QR"""
    meeting_id: str = Field(..., description="Meeting ID")


class MeetingQRResponse(BaseModel):
    """Response with meeting QR information"""
    meeting_id: str
    qr_token: str
    is_enabled: bool = True
    status: str = "ACTIVE"
    created_at: str
    verification_url: str


class CheckInMeetingRequest(BaseModel):
    """Request to check-in to meeting"""
    qr_token: str = Field(..., description="QR token to check-in with")
    event_id: str = Field(..., description="Meeting ID for check-in")


class CheckInMeetingResponse(BaseModel):
    """Response from meeting check-in"""
    attendance_id: str
    user_id: str
    membership_id: str
    event_type: str = "MEETING"
    event_id: str
    check_in_time: str
    message: str = "Check-in successful"


# ==================== Activity QR DTOs ====================

class CreateActivityQRRequest(BaseModel):
    """Request to create activity QR"""
    activity_id: str = Field(..., description="Activity ID")
    activity_name: str = Field(..., description="Name of activity/event")


class ActivityQRResponse(BaseModel):
    """Response with activity QR information"""
    activity_id: str
    activity_name: str
    qr_token: str
    is_enabled: bool = True
    status: str = "ACTIVE"
    created_at: str
    verification_url: str


class CheckInActivityRequest(BaseModel):
    """Request to check-in to activity"""
    qr_token: str = Field(..., description="QR token to check-in with")
    event_id: str = Field(..., description="Activity ID for check-in")


class CheckInActivityResponse(BaseModel):
    """Response from activity check-in"""
    attendance_id: str
    user_id: str
    membership_id: str
    event_type: str = "ACTIVITY"
    event_id: str
    event_name: str
    check_in_time: str
    message: str = "Check-in successful"


# ==================== Statistics DTOs ====================

class IdentityStatisticsResponse(BaseModel):
    """Statistics about digital identities"""
    total_identities: int
    active_cards: int
    disabled_cards: int
    expired_cards: int
    pending_cards: int
    total_verifications: int
    members_by_role: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_identities": 100,
                "active_cards": 95,
                "disabled_cards": 3,
                "expired_cards": 1,
                "pending_cards": 1,
                "total_verifications": 500,
                "members_by_role": {
                    "MEMBER": 80,
                    "CHAIRMAN": 1,
                    "GENERAL_SECRETARY": 1,
                    "ADMIN": 2
                }
            }
        }


class AttendanceStatisticsResponse(BaseModel):
    """Statistics about attendance"""
    event_type: str
    event_id: str
    total_check_ins: int
    unique_members: int
    last_check_in: Optional[str] = None
