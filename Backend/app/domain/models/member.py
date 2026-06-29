# app/domain/models/member.py

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from app.common.models.base_entity import BaseEntity
from app.common.models.value_objects import Email, Phone, Address


class MembershipStatus(str, Enum):
    """Membership status enum"""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    RESIGNED = "resigned"


class MembershipType(str, Enum):
    """Membership type enum"""
    FULL = "full"
    ASSOCIATE = "associate"
    STUDENT = "student"
    HONORARY = "honorary"


class MembershipTier(str, Enum):
    """Membership tier enum"""
    STANDARD = "standard"
    PREMIUM = "premium"
    LIFETIME = "lifetime"


class MembershipAuditAction(str, Enum):
    """Membership audit action enum"""
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    REACTIVATED = "reactivated"
    UPDATED = "updated"


class MembershipAuditEntry(BaseModel):
    """Membership audit entry"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: MembershipAuditAction
    performed_by_user_id: Optional[str] = None
    performed_by_role: Optional[str] = None
    comment: Optional[str] = None
    resulting_status: MembershipStatus
    metadata: Optional[dict] = Field(default_factory=dict)


class Member(BaseEntity):
    """Member domain model"""
    
    # Basic Information
    user_id: str
    email: Email
    phone: Optional[Phone] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    
    # Membership Details
    membership_number: str
    membership_type: MembershipType = MembershipType.FULL
    membership_tier: MembershipTier = MembershipTier.STANDARD
    status: MembershipStatus = MembershipStatus.ACTIVE
    
    # Dates
    joined_date: datetime
    membership_expiry_date: Optional[datetime] = None
    requested_expiry_months: int = 12
    last_active_at: Optional[datetime] = None
    
    # Contact Information
    addresses: List[Address] = []
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[Phone] = None
    
    # Professional Information
    organization: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    
    # Preferences and Settings
    newsletter_subscription: bool = True
    event_notifications: bool = True
    communication_language: str = "en"

    # Membership workflow
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    approver_id: Optional[str] = None
    approver_role: Optional[str] = None
    review_comments: Optional[str] = None
    audit_log: List[MembershipAuditEntry] = Field(default_factory=list)
    
    # Contributions
    meetings_attended: int = 0
    activities_participated: int = 0
    documents_contributed: int = 0
    total_contribution_hours: float = 0.0
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_membership_expired(self) -> bool:
        """Check if membership has expired"""
        if not self.membership_expiry_date:
            return False
        return datetime.utcnow() > self.membership_expiry_date
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Get days until membership expires"""
        if not self.membership_expiry_date:
            return None
        delta = self.membership_expiry_date - datetime.utcnow()
        return max(0, delta.days)
    
    def activate_membership(self) -> None:
        """Activate membership"""
        self.status = MembershipStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def deactivate_membership(self) -> None:
        """Deactivate membership"""
        self.status = MembershipStatus.INACTIVE
        self.updated_at = datetime.utcnow()
    
    def suspend_membership(self) -> None:
        """Suspend membership"""
        self.status = MembershipStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
    
    def resign_membership(self) -> None:
        """Mark member as resigned"""
        self.status = MembershipStatus.RESIGNED
        self.updated_at = datetime.utcnow()
    
    def update_last_active(self) -> None:
        """Update last active timestamp"""
        self.last_active_at = datetime.utcnow()
    
    def record_meeting_attendance(self) -> None:
        """Record meeting attendance"""
        self.meetings_attended += 1
        self.update_last_active()
    
    def record_activity_participation(self, hours: float = 0.0) -> None:
        """Record activity participation"""
        self.activities_participated += 1
        if hours > 0:
            self.total_contribution_hours += hours
        self.update_last_active()
    
    def record_document_contribution(self) -> None:
        """Record document contribution"""
        self.documents_contributed += 1
        self.update_last_active()
    
    def upgrade_tier(self, new_tier: MembershipTier) -> None:
        """Upgrade membership tier"""
        self.membership_tier = new_tier
        self.updated_at = datetime.utcnow()
    
    def change_membership_type(self, new_type: MembershipType) -> None:
        """Change membership type"""
        self.membership_type = new_type
        self.updated_at = datetime.utcnow()
    
    def renew_membership(self, months: int = 12) -> None:
        """Renew membership"""
        from datetime import timedelta
        if self.membership_expiry_date:
            self.membership_expiry_date += timedelta(days=30*months)
        else:
            self.membership_expiry_date = datetime.utcnow() + timedelta(days=30*months)
        self.status = MembershipStatus.ACTIVE
        self.updated_at = datetime.utcnow()
