"""
Digital Identity and Membership Card Domain Model
Handles member identification, QR codes, and verification
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from beanie import Document, Link
from pydantic import Field
from app.domain.models.user import User


class UserRole(str, Enum):
    """User roles in the organization"""
    ADMIN = "ADMIN"
    GENERAL_SECRETARY = "GENERAL_SECRETARY"
    CHAIRMAN = "CHAIRMAN"
    MEMBER = "MEMBER"


class MembershipStatus(str, Enum):
    """Membership status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class VerificationMethod(str, Enum):
    """How verification was performed"""
    QR_CODE = "QR_CODE"
    MEMBERSHIP_ID = "MEMBERSHIP_ID"
    MANUAL = "MANUAL"
    BIOMETRIC = "BIOMETRIC"


class IDCardStatus(str, Enum):
    """Status of ID card"""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"


class QRTokenType(str, Enum):
    """Type of QR token"""
    MEMBER_IDENTITY = "MEMBER_IDENTITY"
    MEETING_ATTENDANCE = "MEETING_ATTENDANCE"
    ACTIVITY_CHECKIN = "ACTIVITY_CHECKIN"
    CONGRESS_ACCREDITATION = "CONGRESS_ACCREDITATION"
    ELECTION_VERIFICATION = "ELECTION_VERIFICATION"


class DigitalIdentity(Document):
    """
    Digital Identity - Represents a member's digital identity
    Contains membership ID, QR token, and card information
    """
    
    # References
    user_id: str = Field(..., description="User ID (ObjectId as string)")
    
    # Identity Information
    membership_id: str = Field(..., description="Unique membership ID (NANS-2026-000001)")
    role: UserRole = Field(default=UserRole.MEMBER, description="User role")
    
    # Card Information
    card_status: IDCardStatus = Field(default=IDCardStatus.PENDING, description="Status of ID card")
    card_issue_date: datetime = Field(default_factory=datetime.utcnow, description="When card was issued")
    card_expiry_date: Optional[datetime] = Field(None, description="When card expires")
    
    # QR Token Information
    qr_token: str = Field(..., description="Secure QR verification token")
    qr_token_type: QRTokenType = Field(default=QRTokenType.MEMBER_IDENTITY, description="Type of QR token")
    qr_token_generated_at: datetime = Field(default_factory=datetime.utcnow, description="When QR token was generated")
    qr_token_last_rotated_at: Optional[datetime] = Field(None, description="Last rotation of QR token")
    
    # Profile Information (cached for verification)
    profile_data: dict = Field(
        default_factory=dict,
        description="Cached profile data: first_name, last_name, email, institution, chapter, profile_photo_url"
    )
    
    # Verification Records
    verification_count: int = Field(default=0, description="Number of times verified")
    last_verified_at: Optional[datetime] = Field(None, description="Last verification timestamp")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether identity is active")
    
    class Settings:
        collection = "digital_identities"
        indexes = [
            ["user_id"],
            ["membership_id"],
            ["qr_token"],
            ["card_status"],
            ["created_at"]
        ]


class QRVerificationRecord(Document):
    """
    QR Verification Record - Audit trail for all QR verifications
    Tracks who verified, when, from where, and what was verified
    """
    
    # Verification Information
    qr_token: str = Field(..., description="QR token that was verified")
    user_id: str = Field(..., description="User ID of person being verified")
    verification_method: VerificationMethod = Field(default=VerificationMethod.QR_CODE, description="How verification was done")
    qr_type: QRTokenType = Field(default=QRTokenType.MEMBER_IDENTITY, description="Type of QR token")
    
    # Verifier Information
    verified_by_id: Optional[str] = Field(None, description="User ID of person performing verification")
    verified_by_role: Optional[str] = Field(None, description="Role of person performing verification")
    
    # Context Information
    context_type: str = Field(default="GENERAL", description="Context: GENERAL, MEETING, ACTIVITY, CONGRESS, ELECTION")
    context_id: Optional[str] = Field(None, description="Related document ID (meeting_id, activity_id, etc)")
    
    # Status
    is_valid: bool = Field(default=True, description="Whether verification was successful")
    verification_details: dict = Field(
        default_factory=dict,
        description="Additional verification details"
    )
    
    # System Fields
    verified_at: datetime = Field(default_factory=datetime.utcnow, description="Verification timestamp")
    ip_address: Optional[str] = Field(None, description="IP address of verifier")
    user_agent: Optional[str] = Field(None, description="User agent of verification device")
    
    class Settings:
        collection = "qr_verification_records"
        indexes = [
            ["qr_token"],
            ["user_id"],
            ["verified_by_id"],
            ["context_type"],
            ["context_id"],
            ["verified_at"]
        ]


class MeetingQRToken(Document):
    """
    Meeting QR Token - Unique QR code for meeting attendance tracking
    Enables QR-based check-in for meetings
    """
    
    meeting_id: str = Field(..., description="Meeting ID")
    qr_token: str = Field(..., description="Unique QR token for this meeting")
    
    # Configuration
    is_enabled: bool = Field(default=True, description="Whether QR check-in is enabled")
    status: str = Field(default="ACTIVE", description="ACTIVE, DISABLED, EXPIRED")
    
    # Usage tracking
    check_in_count: int = Field(default=0, description="Number of check-ins via QR")
    unique_members_checked_in: List[str] = Field(default_factory=list, description="List of member IDs who checked in")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="When QR code expires")
    
    class Settings:
        collection = "meeting_qr_tokens"
        indexes = [
            ["meeting_id"],
            ["qr_token"],
            ["status"],
            ["created_at"]
        ]


class ActivityQRToken(Document):
    """
    Activity QR Token - Unique QR code for activity/event check-in
    Enables QR-based check-in for activities
    """
    
    activity_id: str = Field(..., description="Activity ID")
    activity_name: str = Field(..., description="Name of activity/event")
    qr_token: str = Field(..., description="Unique QR token for this activity")
    
    # Configuration
    is_enabled: bool = Field(default=True, description="Whether QR check-in is enabled")
    status: str = Field(default="ACTIVE", description="ACTIVE, DISABLED, EXPIRED")
    
    # Usage tracking
    check_in_count: int = Field(default=0, description="Number of check-ins via QR")
    unique_members_checked_in: List[str] = Field(default_factory=list, description="List of member IDs who checked in")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="When QR code expires")
    
    class Settings:
        collection = "activity_qr_tokens"
        indexes = [
            ["activity_id"],
            ["qr_token"],
            ["status"],
            ["created_at"]
        ]


class AttendanceRecord(Document):
    """
    Attendance Record - Track member participation via QR codes
    Used for meetings and activities
    """
    
    # Participant Information
    user_id: str = Field(..., description="Member ID")
    membership_id: str = Field(..., description="Membership ID")
    
    # Event Information
    event_type: str = Field(default="MEETING", description="MEETING, ACTIVITY, CONGRESS, ELECTION")
    event_id: str = Field(..., description="Meeting ID, Activity ID, etc")
    event_name: str = Field(..., description="Name of event")
    
    # Verification Information
    qr_token: str = Field(..., description="QR token used for check-in")
    verification_method: VerificationMethod = Field(default=VerificationMethod.QR_CODE, description="How check-in was done")
    
    # Check-in Details
    check_in_time: datetime = Field(default_factory=datetime.utcnow, description="When member checked in")
    check_out_time: Optional[datetime] = Field(None, description="When member checked out")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Settings:
        collection = "attendance_records"
        indexes = [
            ["user_id"],
            ["event_type"],
            ["event_id"],
            ["check_in_time"],
            ["created_at"]
        ]
