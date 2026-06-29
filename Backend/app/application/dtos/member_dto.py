# app/application/dtos/member_dto.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.domain.models.member import MembershipType, MembershipTier, MembershipStatus


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class CamelModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


# Request DTOs

class MemberRegisterRequest(CamelModel):
    """Member registration request"""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, description="Birth date in MM-DD format")
    membership_type: MembershipType = MembershipType.FULL
    membership_tier: MembershipTier = MembershipTier.STANDARD
    expiry_months: int = 12


class MemberUpdateProfileRequest(CamelModel):
    """Update member profile request"""
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    newsletter_subscription: Optional[bool] = None
    event_notifications: Optional[bool] = None
    communication_language: Optional[str] = None


class MemberRenewRequest(BaseModel):
    """Member renewal request"""
    months: int = Field(default=12, ge=1, le=60)


class MemberUpgradeTierRequest(BaseModel):
    """Upgrade membership tier request"""
    new_tier: MembershipTier


class MembershipActionRequest(BaseModel):
    """Membership approval action request"""
    comment: Optional[str] = None


class MembershipAuditEntryResponse(CamelModel):
    """Membership audit entry response DTO"""
    timestamp: datetime
    action: str
    performed_by_user_id: Optional[str] = None
    performed_by_role: Optional[str] = None
    comment: Optional[str] = None
    resulting_status: MembershipStatus
    metadata: dict = Field(default_factory=dict)


class AddressResponse(CamelModel):
    """Address response DTO"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str


# Response DTOs

class MemberResponse(CamelModel):
    """Member response DTO"""
    id: str
    user_id: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    full_name: str
    membership_number: str
    membership_type: MembershipType
    membership_tier: MembershipTier
    status: MembershipStatus
    joined_date: datetime
    membership_expiry_date: Optional[datetime]
    requested_expiry_months: int
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    approver_id: Optional[str]
    approver_role: Optional[str]
    review_comments: Optional[str]
    audit_log: list[MembershipAuditEntryResponse] = []
    is_membership_expired: bool
    days_until_expiry: Optional[int]
    bio: Optional[str]
    profile_photo_url: Optional[str]
    document_ids: list[str] = []
    organization: Optional[str]
    position: Optional[str]
    department: Optional[str] = None
    addresses: list[AddressResponse] = []
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    newsletter_subscription: bool
    event_notifications: bool
    communication_language: str
    last_active_at: Optional[datetime] = None
    meetings_attended: int
    activities_participated: int
    documents_contributed: int
    total_contribution_hours: float
    membership_id: Optional[str] = None
    qr_token: Optional[str] = None
    card_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MemberListResponse(BaseModel):
    """Member list response"""
    total: int
    skip: int
    limit: int
    items: list[MemberResponse]


class MemberStatisticsResponse(BaseModel):
    """Member statistics response"""
    total_members: int
    active_members: int
    inactive_members: int
    suspended_members: int
    members_by_type: dict
    members_by_tier: dict
    total_contribution_hours: float
    average_meetings_attended: float


class MembershipExpiringResponse(BaseModel):
    """Members with expiring memberships"""
    member_id: str
    email: str
    full_name: str
    membership_number: str
    expiry_date: datetime
    days_until_expiry: int


class MemberActivityResponse(BaseModel):
    """Member activity log"""
    member_id: str
    meetings_attended: int
    activities_participated: int
    documents_contributed: int
    total_contribution_hours: float
    last_active_at: Optional[datetime]
