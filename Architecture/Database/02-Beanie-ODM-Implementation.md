# Beanie ODM Implementation Guide
## MongoDB Models for NANS

**Version:** 1.0  
**Date:** June 2026  
**Technology:** Beanie ODM with Pydantic v2

---

## 1. Setup and Configuration

### 1.1 Dependencies

```toml
# pyproject.toml

[dependencies]
beanie = "^1.26.0"
pydantic = "^2.0.0"
motor = "^3.3.0"  # Async MongoDB driver
pymongo = "^4.5.0"
python-multipart = "^0.0.6"
email-validator = "^2.1.0"
```

### 1.2 Database Initialization

```python
# app/core/database.py

from beanie import init_beanie
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from typing import List
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncClient] = None
    db: Optional[AsyncDatabase] = None
    
    @classmethod
    async def connect(cls, db_url: str, db_name: str):
        """Initialize database connection"""
        cls.client = AsyncClient(db_url)
        cls.db = cls.client[db_name]
        
        # Import all models
        from app.models import (
            user, organization, meeting, activity, 
            document, notification, audit, system
        )
        
        # Initialize Beanie
        await init_beanie(
            database=cls.db,
            models=[
                # User models
                user.User,
                user.Role,
                user.Session,
                user.MFAToken,
                
                # Organization models
                organization.Organization,
                organization.OrganizationMember,
                
                # Meeting models
                meeting.Meeting,
                meeting.MeetingRegistration,
                meeting.MeetingMinutes,
                
                # Activity models
                activity.Activity,
                activity.ActivityParticipant,
                activity.EngagementScore,
                
                # Document models
                document.Document,
                document.DocumentVersion,
                
                # Communication models
                notification.Notification,
                notification.EmailTemplate,
                
                # Audit models
                audit.AuditLog,
                audit.DataAccessRequest,
                
                # System models
                system.Configuration,
                system.FeatureFlag,
            ]
        )
        
        logger.info(f"Connected to MongoDB: {db_name}")
    
    @classmethod
    async def disconnect(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")

# Usage in FastAPI app
@app.on_event("startup")
async def startup():
    await Database.connect(
        db_url=settings.MONGODB_URL,
        db_name=settings.MONGODB_DATABASE
    )

@app.on_event("shutdown")
async def shutdown():
    await Database.disconnect()
```

---

## 2. User Models

```python
# app/models/user.py

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from enum import Enum
import secrets

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class UserAuthSource(str, Enum):
    DIRECT = "direct"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_MICROSOFT = "oauth_microsoft"
    SAML = "saml"

class Address(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    is_primary: bool = True

class UserSettings(BaseModel):
    timezone: str = "UTC"
    language: str = "en"
    email_notifications: bool = True
    sms_notifications: bool = False
    newsletter: bool = True
    data_sharing: bool = False

class MFAConfig(BaseModel):
    method: Literal["totp", "sms", "email", "webauthn"]
    is_configured: bool = False
    configured_at: Optional[datetime] = None
    backup_codes: List[str] = []

class User(Document):
    # Basic Information
    email: EmailStr
    phone: Optional[str] = None
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
    is_verified: bool = False
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    
    # Organization
    primary_organization_id: PydanticObjectId
    organizations: List[PydanticObjectId] = []
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    version: int = 1
    
    # Settings
    settings: UserSettings = Field(default_factory=UserSettings)
    
    # Metadata
    source: UserAuthSource = UserAuthSource.DIRECT
    external_ids: Dict[str, str] = {}
    ip_address_registered: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def phone_e164(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith('+'):
            raise ValueError('Phone must be in E.164 format')
        return v
    
    class Settings:
        collection = "users"
        indexes = [
            [("email", 1), {"unique": True}],
            [("phone", 1)],
            [("primary_organization_id", 1), ("status", 1)],
            [("organizations", 1), ("status", 1)],
            [("created_at", -1)],
            [("locked_until", 1), {"expireAfterSeconds": 0}],
        ]
    
    def set_password(self, password: str) -> None:
        """Hash and set password using Argon2id"""
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        self.password_hash = ph.hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        from argon2 import PasswordHasher
        from argon2.exceptions import VerifyMismatchError, InvalidHashError
        ph = PasswordHasher()
        try:
            ph.verify(self.password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
    
    def increment_login_attempts(self) -> None:
        """Increment failed login attempts and lock if needed"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_login_attempts(self) -> None:
        """Reset login attempts on successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()

class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

class Role(Document):
    # Basic Info
    name: str
    description: Optional[str] = None
    
    # Scope
    organization_id: Optional[PydanticObjectId] = None
    scope: Literal["system", "organization", "chapter"] = "organization"
    
    # Permissions
    permissions: List[str] = []
    
    # Status
    is_active: bool = True
    is_system_role: bool = False
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PydanticObjectId
    
    class Settings:
        collection = "roles"
        indexes = [
            [("organization_id", 1), ("is_active", 1)],
            [("scope", 1), ("is_active", 1)],
            [("name", 1)],
        ]

class Session(Document):
    """Store user sessions for tracking and security"""
    user_id: PydanticObjectId
    session_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=12))
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "sessions"
        indexes = [
            [("user_id", 1), ("expires_at", -1)],
            [("session_token", 1), {"unique": True}],
            [("expires_at", 1), {"expireAfterSeconds": 0}],  # TTL
        ]

class MFAToken(Document):
    """Temporary MFA verification tokens"""
    user_id: PydanticObjectId
    token: str
    method: Literal["email", "sms"]
    code: Optional[str] = None  # OTP code
    is_used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=5))
    
    class Settings:
        collection = "mfa_tokens"
        indexes = [
            [("user_id", 1), ("method", 1)],
            [("token", 1)],
            [("expires_at", 1), {"expireAfterSeconds": 0}],  # TTL
        ]
```

---

## 3. Organization Models

```python
# app/models/organization.py

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class OrganizationType(str, Enum):
    NATIONAL = "national"
    CHAPTER = "chapter"
    SUB_GROUP = "sub_group"
    DEPARTMENT = "department"
    WORKING_GROUP = "working_group"

class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class ContactInfo(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None

class OrganizationMetadata(BaseModel):
    founded_year: Optional[int] = None
    member_count: int = 0
    annual_budget: Optional[str] = None
    industry: Optional[str] = None
    custom_fields: Dict[str, Any] = {}

class Organization(Document):
    # Basic Information
    name: str
    slug: str
    type: OrganizationType
    
    # Hierarchy
    parent_id: Optional[PydanticObjectId] = None
    path: str = "/"
    level: int = 0
    
    # Details
    description: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    cover_image_url: Optional[HttpUrl] = None
    
    # Contact
    contact: Optional[ContactInfo] = None
    location: Optional[str] = None
    timezone: str = "UTC"
    
    # Status
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    is_public: bool = True
    
    # Membership
    member_count: int = 0
    active_member_count: int = 0
    
    # Settings
    require_approval_for_membership: bool = False
    allow_member_self_registration: bool = True
    max_members: Optional[int] = None
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PydanticObjectId
    version: int = 1
    
    # Metadata
    metadata: OrganizationMetadata = Field(default_factory=OrganizationMetadata)
    
    class Settings:
        collection = "organizations"
        indexes = [
            [("parent_id", 1), ("status", 1)],
            [("type", 1), ("status", 1)],
            [("level", 1), ("status", 1)],
            [("created_at", -1)],
            [("slug", 1)],
            [("is_public", 1), ("status", 1)],
        ]

class MembershipRole(BaseModel):
    role_id: PydanticObjectId
    assigned_at: datetime
    assigned_by: PydanticObjectId
    expires_at: Optional[datetime] = None

class MembershipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    INVITED = "invited"

class OrganizationMember(Document):
    # Identification
    organization_id: PydanticObjectId
    user_id: PydanticObjectId
    
    # Membership
    status: MembershipStatus = MembershipStatus.ACTIVE
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None
    
    # Roles
    roles: List[MembershipRole] = []
    primary_role_id: Optional[PydanticObjectId] = None
    
    # Denormalized user data
    user_email: str
    user_name: str
    user_phone: Optional[str] = None
    
    # Permissions
    effective_permissions: List[str] = []
    permissions_updated_at: Optional[datetime] = None
    
    # Engagement
    participation_score: int = 0
    meetings_attended: int = 0
    activities_participated: int = 0
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    
    class Settings:
        collection = "organization_members"
        indexes = [
            [("organization_id", 1), ("user_id", 1), {"unique": True}],
            [("organization_id", 1), ("status", 1)],
            [("organization_id", 1), ("joined_at", -1)],
            [("user_id", 1), ("organization_id", 1)],
            [("organization_id", 1), ("participation_score", -1)],
        ]
```

---

## 4. Meeting Models

```python
# app/models/meeting.py

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class MeetingStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MeetingType(str, Enum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    HYBRID = "hybrid"

class MeetingVisibility(str, Enum):
    PUBLIC = "public"
    MEMBERS_ONLY = "members_only"
    PRIVATE = "private"

class MeetingAgendaItem(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    presenter: Optional[str] = None
    order: int

class MeetingAttachment(BaseModel):
    name: str
    url: HttpUrl
    file_type: str
    uploaded_at: datetime

class Meeting(Document):
    # Basic Information
    title: str
    description: Optional[str] = None
    organization_id: PydanticObjectId
    
    # Scheduling
    scheduled_at: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int
    timezone: str = "UTC"
    
    # Location
    meeting_type: MeetingType
    location: Optional[str] = None
    meeting_link: Optional[HttpUrl] = None
    
    # People
    organizer_id: PydanticObjectId
    facilitator_id: PydanticObjectId
    co_facilitators: List[PydanticObjectId] = []
    
    # Attendees
    capacity: Optional[int] = None
    registered_count: int = 0
    checked_in_count: int = 0
    no_show_count: int = 0
    
    # Agenda & Attachments
    agenda: List[MeetingAgendaItem] = []
    attachments: List[MeetingAttachment] = []
    
    # Status
    status: MeetingStatus = MeetingStatus.DRAFT
    visibility: MeetingVisibility = MeetingVisibility.MEMBERS_ONLY
    
    # Configuration
    registration_enabled: bool = True
    registration_deadline: Optional[datetime] = None
    waitlist_enabled: bool = False
    allow_guests: bool = False
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PydanticObjectId
    version: int = 1
    
    class Settings:
        collection = "meetings"
        indexes = [
            [("organization_id", 1), ("scheduled_at", -1)],
            [("organization_id", 1), ("status", 1)],
            [("facilitator_id", 1), ("scheduled_at", -1)],
            [("status", 1), ("scheduled_at", -1)],
            [("created_at", -1)],
        ]

class RegistrationStatus(str, Enum):
    REGISTERED = "registered"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"
    ABSENT = "absent"

class MeetingRegistration(Document):
    # Key
    meeting_id: PydanticObjectId
    user_id: PydanticObjectId
    
    # Denormalized data
    user_email: str
    user_name: str
    
    # Registration Details
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    registration_status: RegistrationStatus = RegistrationStatus.REGISTERED
    
    # Check-in
    checked_in_at: Optional[datetime] = None
    is_late: bool = False
    
    # Metadata
    dietary_restrictions: Optional[str] = None
    special_accommodations: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    
    # Status
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "meeting_registrations"
        indexes = [
            [("meeting_id", 1), ("user_id", 1), {"unique": True}],
            [("meeting_id", 1), ("registration_status", 1)],
            [("meeting_id", 1), ("checked_in_at", 1)],
            [("user_id", 1), ("meeting_id", 1)],
            [("created_at", -1)],
        ]

class ActionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    title: str
    description: Optional[str] = None
    assigned_to: PydanticObjectId
    due_date: datetime
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "in_progress", "completed", "cancelled"] = "pending"
    completed_at: Optional[datetime] = None

class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    title: str
    description: str
    owner: PydanticObjectId
    impact: Optional[str] = None

class MinutesStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PUBLISHED = "published"

class MeetingMinutes(Document):
    # Key
    meeting_id: PydanticObjectId
    
    # Content
    title: str
    summary: str
    detailed_notes: Optional[str] = None
    
    # Attendees
    attendees: List[PydanticObjectId] = []
    absent: List[PydanticObjectId] = []
    
    # Action Items & Decisions
    action_items: List[ActionItem] = []
    decisions: List[Decision] = []
    next_steps: Optional[str] = None
    recommendations: Optional[str] = None
    
    # Approval
    status: MinutesStatus = MinutesStatus.DRAFT
    submitted_by: PydanticObjectId
    submitted_at: Optional[datetime] = None
    approved_by: Optional[PydanticObjectId] = None
    approved_at: Optional[datetime] = None
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    
    class Settings:
        collection = "meeting_minutes"
        indexes = [
            [("meeting_id", 1)],
            [("meeting_id", 1), ("status", 1)],
            [("approved_at", -1)],
        ]
```

---

## 5. Audit Models

```python
# app/models/audit.py

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
import hashlib

class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AuditLog(Document):
    # Immutable identifier
    audit_log_id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Actor
    user_id: PydanticObjectId
    user_email: str
    ip_address: str
    user_agent: str
    session_id: str
    
    # Action
    action_type: str
    action_category: str
    action: str
    
    # Resource
    resource_type: str
    resource_id: PydanticObjectId
    resource_name: Optional[str] = None
    
    # Organization
    organization_id: PydanticObjectId
    
    # Change Details
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    changes: List[Dict[str, Any]] = []
    
    # Result
    status: Literal["success", "failure"] = "success"
    status_code: int = 200
    error_message: Optional[str] = None
    
    # Metadata
    request_id: str
    execution_time_ms: int = 0
    data_size_bytes: int = 0
    
    # Security
    severity: AuditSeverity = AuditSeverity.INFO
    
    # Hash Chain
    hash: str = ""
    previous_hash: str = ""
    
    # Retention
    retention_until: datetime = Field(
        default_factory=lambda: datetime.utcnow().replace(year=datetime.utcnow().year + 7)
    )
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Settings:
        collection = "audit_logs"
        indexes = [
            [("organization_id", 1), ("timestamp", -1)],
            [("user_id", 1), ("timestamp", -1)],
            [("resource_type", 1), ("resource_id", 1), ("timestamp", -1)],
            [("action_type", 1), ("timestamp", -1)],
            [("timestamp", 1)],
            [("retention_until", 1), {"expireAfterSeconds": 0}],
            [("severity", 1), ("timestamp", -1)],
        ]
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of audit log"""
        data = f"{self.audit_log_id}{self.timestamp}{self.user_id}{self.action_type}{self.resource_id}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class DataAccessRequestStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DataAccessRequest(Document):
    # Identification
    request_id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    organization_id: PydanticObjectId
    user_id: PydanticObjectId
    
    # Request Details
    request_type: Literal["export", "access", "delete", "correct"]
    reason: str
    
    # Status
    status: DataAccessRequestStatus = DataAccessRequestStatus.SUBMITTED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Processing
    processed_by: Optional[PydanticObjectId] = None
    notes: Optional[str] = None
    
    # Response
    data_export_url: Optional[str] = None
    expiry_at: Optional[datetime] = None
    
    # Compliance
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    
    class Settings:
        collection = "data_access_requests"
        indexes = [
            [("organization_id", 1), ("status", 1)],
            [("user_id", 1), ("created_at", -1)],
            [("created_at", -1)],
        ]
```

---

## 6. Usage Examples

### 6.1 Creating Documents

```python
# Create a new user
from app.models.user import User

user = User(
    email="user@example.com",
    first_name="John",
    last_name="Doe",
    phone="+14155552671",
    primary_organization_id=org_id,
    password_hash="will_be_set"
)
user.set_password("SecurePassword123!")
await user.insert()

# Create a meeting
from app.models.meeting import Meeting, MeetingType, MeetingVisibility

meeting = Meeting(
    title="Q2 Planning Meeting",
    organization_id=org_id,
    scheduled_at=datetime(2026, 7, 15, 14, 0),
    duration_minutes=120,
    meeting_type=MeetingType.VIRTUAL,
    organizer_id=user_id,
    facilitator_id=user_id,
    meeting_link="https://zoom.us/meeting/123"
)
await meeting.insert()
```

### 6.2 Querying Documents

```python
# Get user by email
user = await User.find_one(User.email == "user@example.com")

# Get all meetings for an organization
meetings = await Meeting.find(
    Meeting.organization_id == org_id,
    Meeting.status == "scheduled"
).sort("scheduled_at", -1).to_list(10)

# Find organization members with a specific role
members = await OrganizationMember.find(
    OrganizationMember.organization_id == org_id,
    OrganizationMember.status == "active"
).sort("participation_score", -1).to_list(100)

# Count active registrations for a meeting
count = await MeetingRegistration.find(
    MeetingRegistration.meeting_id == meeting_id,
    MeetingRegistration.registration_status == "registered"
).count()
```

### 6.3 Updating Documents

```python
# Update user status
user = await User.get(user_id)
user.status = "active"
user.is_verified = True
user.updated_at = datetime.utcnow()
await user.save()

# Increment meeting attendance count
meeting = await Meeting.get(meeting_id)
meeting.checked_in_count += 1
await meeting.save()

# Use UpdateQuery for bulk operations
from beanie import UpdateQuery

result = await User.find(User.status == "inactive").update(
    {"$set": {"status": "deleted", "deleted_at": datetime.utcnow()}},
    multi=True
)
print(f"Updated {result.modified_count} users")
```

### 6.4 Transactions

```python
# Multi-document transaction
from beanie import client

async def register_user_for_meeting(user_id, meeting_id):
    """Register user and update meeting count atomically"""
    async with await client.start_session() as session:
        async with session.start_transaction():
            # Create registration
            registration = MeetingRegistration(
                meeting_id=meeting_id,
                user_id=user_id,
                user_email=user.email,
                user_name=user.full_name
            )
            await registration.insert(session=session)
            
            # Update meeting count
            meeting = await Meeting.get(meeting_id, session=session)
            meeting.registered_count += 1
            await meeting.save(session=session)
            
            return registration

await register_user_for_meeting(user_id, meeting_id)
```

### 6.5 Aggregation Pipeline

```python
# Get top participants by engagement score
from beanie import aggregation

pipeline = [
    {"$match": {"organization_id": org_id}},
    {"$sort": {"total_score": -1}},
    {"$limit": 10},
    {"$project": {
        "user_id": 1,
        "total_score": 1,
        "engagement_level": 1,
        "meetings_attended": 1,
        "activities_participated": 1
    }}
]

results = await EngagementScore.aggregate(pipeline).to_list(None)

# Count meetings by status
pipeline = [
    {"$match": {"organization_id": org_id}},
    {"$group": {
        "_id": "$status",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]

status_counts = await Meeting.aggregate(pipeline).to_list(None)
```

### 6.6 Async Iteration

```python
# Process large result sets
async for meeting in Meeting.find(
    Meeting.organization_id == org_id,
    Meeting.status == "completed"
):
    print(f"Processing {meeting.title}")
    # Do work on each meeting
    
# With limit
async for user in User.find(User.status == "active").limit(100):
    await send_notification(user)
```

---

## 7. Best Practices

### 7.1 Connection Management

```python
# Good: Using dependency injection
from fastapi import Depends

async def get_db() -> AsyncDatabase:
    return Database.db

@app.get("/users/{user_id}")
async def get_user(
    user_id: PydanticObjectId,
    db: AsyncDatabase = Depends(get_db)
):
    user = await User.get(user_id)
    return user
```

### 7.2 Error Handling

```python
from beanie.exceptions import DocumentNotFound
from pymongo.errors import DuplicateKeyError

try:
    user = await User.get(user_id)
except DocumentNotFound:
    raise HTTPException(status_code=404, detail="User not found")
except Exception as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")

try:
    user = await user.insert()
except DuplicateKeyError:
    raise HTTPException(status_code=409, detail="User already exists")
```

### 7.3 Performance

```python
# Use projection to limit fields
user = await User.find_one(
    User.email == email,
    projection={"email": 1, "password_hash": 1, "status": 1}
)

# Use indexes wisely
# Index on frequently filtered/sorted fields
# Avoid indexing low-cardinality fields

# Cache frequently accessed data
from cachetools import TTLCache
user_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL
```

### 7.4 Data Validation

```python
# Use Pydantic validators for complex rules
from pydantic import field_validator

class User(Document):
    password_hash: str
    
    @field_validator('password_hash')
    @classmethod
    def validate_password_hash(cls, v):
        if len(v) < 60:  # Argon2id output
            raise ValueError('Invalid password hash')
        return v
```

