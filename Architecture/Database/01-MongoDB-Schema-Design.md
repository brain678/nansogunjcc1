# MongoDB Schema Design
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  
**Technology:** MongoDB with Beanie ODM (Pydantic-based)

---

## 1. Schema Design Principles

### 1.1 Design Philosophy

```
Principles:

1. Embedding vs. Referencing
   ├─ Embed when: Subdocuments always accessed with parent
   │   ├─ Example: User profile → embed address
   │   └─ Avoid: N+1 queries
   │
   ├─ Reference when: Shared across multiple documents
   │   ├─ Example: Multiple meetings → reference organization
   │   └─ Benefit: Reduce duplication
   │
   └─ Decision matrix:
       ├─ Size: Embedded docs < 100 KB
       ├─ Cardinality: 1:1 or 1:few (embed), 1:many (reference)
       ├─ Update frequency: Same update pattern (embed)
       └─ Query patterns: Always accessed together (embed)

2. Atomicity
   ├─ Use document transactions for related updates
   ├─ Multi-document transactions for consistency
   └─ Example: User + profile must be atomic

3. Scalability
   ├─ Shard on organization_id (multi-tenancy)
   ├─ Time-series data: Separate by month
   ├─ Large arrays: Shred into separate documents
   └─ Archive old data to cold storage

4. Performance
   ├─ Denormalize frequently accessed data
   ├─ Create indexes for common queries
   ├─ Avoid large arrays in indexed fields
   └─ Use projection to limit field retrieval

5. Audit Trail
   ├─ Immutable audit_logs collection (append-only)
   ├─ No deletes in audit_logs (except via retention)
   ├─ Hash chaining for tampering detection
   └─ Version history for critical entities
```

### 1.2 Naming Conventions

```
Collection Naming:
├─ Format: {plural_snake_case}
├─ Examples:
│   ├─ users (not user)
│   ├─ organizations
│   ├─ meeting_registrations
│   ├─ activity_participants
│   └─ audit_logs
│
└─ Special prefixes:
    ├─ {entity}_audit: Versioning collection
    │   └─ Example: users_audit, meetings_audit
    │
    ├─ {entity}_archive: Historical/archived data
    │   └─ Example: activities_archive
    │
    └─ {entity}_snapshot: Point-in-time snapshots
        └─ Example: reports_snapshot

Field Naming:
├─ Format: {snake_case}
├─ Reserved fields:
│   ├─ _id: ObjectId (MongoDB-generated)
│   ├─ created_at: ISO 8601 timestamp
│   ├─ updated_at: ISO 8601 timestamp
│   ├─ deleted_at: ISO 8601 (soft delete)
│   └─ version: Integer (for optimistic locking)
│
├─ Foreign keys:
│   ├─ Format: {entity}_id (ObjectId)
│   ├─ Example: user_id, organization_id, meeting_id
│   └─ Index: Created automatically for joins
│
└─ Boolean fields:
    ├─ Format: is_{adjective}
    ├─ Examples: is_active, is_archived, is_verified
    └─ Default: false (explicit)

Temporal Fields:
├─ Timestamps: ISO 8601 (UTC)
│   ├─ created_at: Record creation
│   ├─ updated_at: Last modification
│   ├─ deleted_at: Soft delete marker
│   └─ archived_at: Archive timestamp
│
└─ Date ranges:
    ├─ start_date / end_date: For periods
    ├─ effective_at: When change applies
    └─ expires_at: Expiration timestamp
```

### 1.3 Data Types Mapping

```
Beanie/Pydantic → MongoDB Type:

Primitives:
├─ str → String
├─ int → Int32 / Int64
├─ float → Double
├─ bool → Boolean
├─ datetime → Date
└─ ObjectId → ObjectId

Complex Types:
├─ List[str] → Array of Strings
├─ Dict[str, Any] → Embedded Document
├─ Optional[str] → String (nullable)
├─ Enum → String or Int32
└─ UUID → String (UUID format)

Custom Types:
├─ Email: str (with validation)
├─ Phone: str (E.164 format)
├─ URL: str (with validation)
├─ Currency: Decimal128 (for precision)
├─ GeoPoint: {"type": "Point", "coordinates": [lon, lat]}
└─ FileReference: {"bucket": str, "key": str}
```

---

## 2. Core Collections

### 2.1 Users Collection

```python
# Collection: users
# Purpose: Store user account information and authentication details
# Sharding key: organization_id (multi-tenancy)

class Address(BaseModel):
    street: str
    city: str
    state: Optional[str]
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
    method: Literal["totp", "sms", "email", "webauthn"]  # Enabled method
    is_configured: bool = False
    configured_at: Optional[datetime] = None
    backup_codes: List[str] = []  # Hashed backup codes

class User(Document):
    # Basic Information
    email: EmailStr  # Unique per system
    phone: Optional[str]  # E.164 format
    first_name: str
    last_name: str
    
    # Authentication
    password_hash: str  # Argon2id hashed
    password_changed_at: datetime
    last_login_at: Optional[datetime]
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Profile
    bio: Optional[str]
    profile_photo_url: Optional[HttpUrl]
    addresses: List[Address] = []
    
    # MFA Configuration
    mfa_primary: Optional[MFAConfig]
    mfa_secondary: Optional[MFAConfig]
    mfa_enabled: bool = False
    
    # Status
    status: Literal["active", "inactive", "suspended", "deleted"] = "active"
    is_verified: bool = False
    email_verified_at: Optional[datetime]
    phone_verified_at: Optional[datetime]
    
    # Organization
    primary_organization_id: ObjectId  # Main org
    organizations: List[ObjectId] = []  # All org memberships
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    version: int = 1  # For optimistic locking
    
    # Settings
    settings: UserSettings = Field(default_factory=UserSettings)
    
    # Metadata
    source: Literal["direct", "oauth_google", "oauth_microsoft", "saml"] = "direct"
    external_ids: Dict[str, str] = {}  # {"oauth_google": "..."} 
    ip_address_registered: Optional[str]
    
    class Settings:
        collection = "users"
        
        # Indexes
        indexes = [
            "email",  # Unique query by email
            "phone",  # Query by phone
            ([("primary_organization_id", 1), ("status", 1)], {}),  # Org members
            ([("organizations", 1), ("status", 1)], {}),  # User orgs
            ([("created_at", -1)], {}),  # Recent users
            ([("email_verified_at", 1)], {}),  # Unverified users
            ([("locked_until", 1)], {}),  # Locked accounts (TTL)
        ]
    
    # Validation
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email required')
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone must be E.164 format')
        return v

# Indexes:
# - unique_email: db.users.createIndex({ email: 1 }, { unique: true })
# - phone: db.users.createIndex({ phone: 1 })
# - org_status: db.users.createIndex({ primary_organization_id: 1, status: 1 })
# - created: db.users.createIndex({ created_at: -1 })
# - locked_ttl: db.users.createIndex({ locked_until: 1 }, { expireAfterSeconds: 0 })
```

### 2.2 Organizations Collection

```python
# Collection: organizations
# Purpose: Manage organizational hierarchy and metadata
# Sharding key: _id (each org independent)

class ContactInfo(BaseModel):
    email: EmailStr
    phone: Optional[str]
    website: Optional[HttpUrl]

class OrganizationMetadata(BaseModel):
    founded_year: Optional[int]
    member_count: int = 0
    annual_budget: Optional[str]
    industry: Optional[str]
    custom_fields: Dict[str, Any] = {}

class Organization(Document):
    # Basic Information
    name: str  # Unique per level
    slug: str  # URL-friendly identifier
    type: Literal["national", "chapter", "sub_group", "department", "working_group"]
    
    # Hierarchy
    parent_id: Optional[ObjectId] = None  # Parent organization
    path: str  # "/national/chapter_1/sub_group_1" (denormalized)
    level: int = 0  # Depth in hierarchy
    
    # Details
    description: Optional[str]
    logo_url: Optional[HttpUrl]
    cover_image_url: Optional[HttpUrl]
    
    # Contact
    contact: Optional[ContactInfo]
    location: Optional[str]
    timezone: str = "UTC"
    
    # Status
    status: Literal["active", "inactive", "suspended", "archived"] = "active"
    is_public: bool = True
    
    # Membership
    member_count: int = 0  # Denormalized for performance
    active_member_count: int = 0  # Count of active members
    
    # Settings
    require_approval_for_membership: bool = False
    allow_member_self_registration: bool = True
    max_members: Optional[int] = None
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: ObjectId  # Creator user
    version: int = 1
    
    # Metadata
    metadata: OrganizationMetadata = Field(default_factory=OrganizationMetadata)
    
    class Settings:
        collection = "organizations"
        indexes = [
            ([("parent_id", 1), ("status", 1)], {}),  # Child orgs
            ([("type", 1), ("status", 1)], {}),  # By type
            ([("level", 1), ("status", 1)], {}),  # By hierarchy level
            ([("created_at", -1)], {}),  # Recent orgs
            "slug",  # URL lookup
            ([("is_public", 1), ("status", 1)], {}),  # Public orgs
        ]
```

### 2.3 Roles Collection

```python
# Collection: roles
# Purpose: Define role definitions with permissions
# Notes: System-wide or org-specific

class Role(Document):
    # Basic Info
    name: str  # Unique per organization
    description: Optional[str]
    
    # Scope
    organization_id: Optional[ObjectId] = None  # None = system-wide
    scope: Literal["system", "organization", "chapter"] = "organization"
    
    # Permissions
    permissions: List[str] = []  # e.g., ["users:read", "meetings:create"]
    
    # Status
    is_active: bool = True
    is_system_role: bool = False  # Cannot be modified if True
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: ObjectId
    
    class Settings:
        collection = "roles"
        indexes = [
            ([("organization_id", 1), ("is_active", 1)], {}),  # Org roles
            ([("scope", 1), ("is_active", 1)], {}),  # By scope
            "name",  # Lookup by name
        ]
```

### 2.4 Organization Members Collection

```python
# Collection: organization_members
# Purpose: Manage membership and roles per organization
# Sharding key: organization_id

class MembershipRole(BaseModel):
    role_id: ObjectId
    assigned_at: datetime
    assigned_by: ObjectId
    expires_at: Optional[datetime] = None

class OrganizationMember(Document):
    # Identification
    organization_id: ObjectId  # Shard key
    user_id: ObjectId
    
    # Membership
    status: Literal["active", "inactive", "suspended", "pending", "invited"] = "active"
    joined_at: datetime
    left_at: Optional[datetime] = None
    
    # Roles
    roles: List[MembershipRole] = []  # Multiple roles per member
    primary_role_id: Optional[ObjectId] = None
    
    # Denormalized user data (for quick access)
    user_email: str
    user_name: str
    user_phone: Optional[str]
    
    # Permissions (cached for performance)
    effective_permissions: List[str] = []  # Computed permissions
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
            ([("organization_id", 1), ("user_id", 1)], {"unique": True}),  # Unique member
            ([("organization_id", 1), ("status", 1)], {}),  # Org members
            ([("organization_id", 1), ("joined_at", -1)], {}),  # Recent joins
            ([("user_id", 1), ("organization_id", 1)], {}),  # User's orgs
            ([("organization_id", 1), ("participation_score", -1)], {}),  # Top participants
        ]
```

---

## 3. Meeting Collections

### 3.1 Meetings Collection

```python
# Collection: meetings
# Purpose: Store meeting information and lifecycle
# Sharding key: organization_id

class MeetingAgendaItem(BaseModel):
    title: str
    description: Optional[str]
    duration_minutes: Optional[int]
    presenter: Optional[str]
    order: int

class MeetingAttachement(BaseModel):
    name: str
    url: HttpUrl
    file_type: str
    uploaded_at: datetime

class Meeting(Document):
    # Basic Information
    title: str
    description: Optional[str]
    organization_id: ObjectId  # Shard key
    
    # Scheduling
    scheduled_at: datetime  # When meeting is scheduled
    start_time: Optional[datetime]  # When meeting actually started
    end_time: Optional[datetime]  # When meeting ended
    duration_minutes: int
    timezone: str = "UTC"
    
    # Location
    meeting_type: Literal["in_person", "virtual", "hybrid"]
    location: Optional[str]  # Physical location
    meeting_link: Optional[HttpUrl]  # Zoom, Teams, etc.
    
    # Facilitator & Organizer
    organizer_id: ObjectId
    facilitator_id: ObjectId
    co_facilitators: List[ObjectId] = []
    
    # Attendees (denormalized count for performance)
    capacity: Optional[int] = None
    registered_count: int = 0
    checked_in_count: int = 0
    no_show_count: int = 0
    
    # Agenda
    agenda: List[MeetingAgendaItem] = []
    
    # Attachments
    attachments: List[MeetingAttachement] = []
    
    # Status
    status: Literal["draft", "scheduled", "active", "completed", "cancelled"] = "draft"
    visibility: Literal["public", "members_only", "private"] = "members_only"
    
    # Configuration
    registration_enabled: bool = True
    registration_deadline: Optional[datetime]
    waitlist_enabled: bool = False
    allow_guests: bool = False
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: ObjectId
    version: int = 1
    
    class Settings:
        collection = "meetings"
        indexes = [
            ([("organization_id", 1), ("scheduled_at", -1)], {}),  # Org calendar
            ([("organization_id", 1), ("status", 1)], {}),  # By status
            ([("facilitator_id", 1), ("scheduled_at", -1)], {}),  # Facilitator schedule
            ([("status", 1), ("scheduled_at", -1)], {}),  # Global calendar
            ([("created_at", -1)], {}),  # Recent
            ([("scheduled_at", 1)], {"expireAfterSeconds": 7776000}),  # Auto-archive (90 days)
        ]
```

### 3.2 Meeting Registrations Collection

```python
# Collection: meeting_registrations
# Purpose: Track attendee registrations and status
# Sharding key: meeting_id

class MeetingRegistration(Document):
    # Key
    meeting_id: ObjectId  # Shard key
    user_id: ObjectId
    
    # Denormalized data
    user_email: str
    user_name: str
    
    # Registration Details
    registered_at: datetime
    registration_status: Literal["registered", "waitlisted", "cancelled", "absent"] = "registered"
    
    # Check-in
    checked_in_at: Optional[datetime] = None
    is_late: bool = False
    
    # Metadata
    dietary_restrictions: Optional[str]
    special_accommodations: Optional[str]
    custom_fields: Dict[str, Any] = {}
    
    # Status
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "meeting_registrations"
        indexes = [
            ([("meeting_id", 1), ("user_id", 1)], {"unique": True}),  # Unique registration
            ([("meeting_id", 1), ("registration_status", 1)], {}),  # By status
            ([("meeting_id", 1), ("checked_in_at", 1)], {}),  # Attendance
            ([("user_id", 1), ("meeting_id", 1)], {}),  # User meetings
            ([("created_at", -1)], {}),  # Recent
        ]
```

### 3.3 Meeting Minutes Collection

```python
# Collection: meeting_minutes
# Purpose: Store meeting minutes and action items
# Sharding key: meeting_id

class ActionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    description: Optional[str]
    assigned_to: ObjectId
    due_date: datetime
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "in_progress", "completed", "cancelled"] = "pending"
    completed_at: Optional[datetime] = None

class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    description: str
    owner: ObjectId
    impact: Optional[str]

class MeetingMinutes(Document):
    # Key
    meeting_id: ObjectId  # Unique per meeting
    
    # Content
    title: str
    summary: str
    detailed_notes: Optional[str]
    
    # Attendees
    attendees: List[ObjectId]
    absent: List[ObjectId] = []
    
    # Action Items & Decisions
    action_items: List[ActionItem] = []
    decisions: List[Decision] = []
    next_steps: Optional[str]
    recommendations: Optional[str]
    
    # Approval
    status: Literal["draft", "submitted", "approved", "published"] = "draft"
    submitted_by: ObjectId
    submitted_at: Optional[datetime]
    approved_by: Optional[ObjectId]
    approved_at: Optional[datetime]
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    
    class Settings:
        collection = "meeting_minutes"
        indexes = [
            "meeting_id",  # Lookup by meeting
            ([("meeting_id", 1), ("status", 1)], {}),
            ([("approved_at", -1)], {}),  # Recent approved
        ]
```

---

## 4. Activity Collections

### 4.1 Activities Collection

```python
# Collection: activities
# Purpose: Track organizational activities and engagement
# Sharding key: organization_id

class ActivityCategory(BaseModel):
    name: str
    description: Optional[str]

class Activity(Document):
    # Basic Info
    title: str
    description: Optional[str]
    category: str  # workshop, training, social, event, etc.
    organization_id: ObjectId  # Shard key
    
    # Scheduling
    start_date: date
    end_date: Optional[date]
    location: str
    
    # Organizer
    organizer_id: ObjectId
    coordinators: List[ObjectId] = []
    
    # Participation
    expected_participants: int = 0
    actual_participants: int = 0
    
    # Status
    status: Literal["active", "completed", "archived", "cancelled"] = "active"
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Settings:
        collection = "activities"
        indexes = [
            ([("organization_id", 1), ("start_date", -1)], {}),  # Org activities
            ([("organization_id", 1), ("status", 1)], {}),  # By status
            ([("status", 1), ("start_date", -1)], {}),  # Global activities
        ]
```

### 4.2 Activity Participants Collection

```python
# Collection: activity_participants
# Purpose: Track participant engagement in activities
# Sharding key: activity_id

class ActivityParticipant(Document):
    # Key
    activity_id: ObjectId  # Shard key
    user_id: ObjectId
    organization_id: ObjectId
    
    # Participation
    participation_date: date
    participation_type: Literal["attended", "presented", "organized", "facilitated"]
    
    # Engagement
    hours: int = 0  # Hours participated
    engagement_points: int = 0  # Calculated engagement
    
    # Status
    is_active: bool = True
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    recorded_by: ObjectId
    
    class Settings:
        collection = "activity_participants"
        indexes = [
            ([("activity_id", 1), ("user_id", 1)], {"unique": True}),
            ([("activity_id", 1), ("participation_type", 1)], {}),
            ([("user_id", 1), ("participation_date", -1)], {}),
            ([("organization_id", 1), ("user_id", 1)], {}),
        ]
```

### 4.3 Engagement Scores Collection

```python
# Collection: engagement_scores
# Purpose: Track member engagement metrics
# Sharding key: organization_id

class EngagementScore(Document):
    # Key
    organization_id: ObjectId  # Shard key
    user_id: ObjectId
    
    # Scores
    total_score: int = 0
    lifetime_score: int = 0
    ytd_score: int = 0  # Year-to-date
    monthly_scores: Dict[str, int] = {}  # {"2026-06": 150}
    
    # Breakdown
    meetings_attended: int = 0
    activities_participated: int = 0
    leadership_points: int = 0
    
    # Streak
    streak_days: int = 0
    last_activity_date: Optional[date] = None
    
    # Level
    engagement_level: Literal["low", "medium", "high", "excellent"] = "low"
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "engagement_scores"
        indexes = [
            ([("organization_id", 1), ("user_id", 1)], {"unique": True}),
            ([("organization_id", 1), ("total_score", -1)], {}),  # Leaderboard
            ([("organization_id", 1), ("engagement_level", 1)], {}),
            ([("calculated_at", -1)], {}),  # Recent calcs
        ]
```

---

## 5. Document Management Collections

### 5.1 Documents Collection

```python
# Collection: documents
# Purpose: Store document metadata
# Sharding key: organization_id

class DocumentTag(BaseModel):
    name: str
    color: Optional[str]

class Document(Document):
    # Basic Info
    title: str
    description: Optional[str]
    organization_id: ObjectId  # Shard key
    
    # Storage
    file_key: str  # S3 key or storage reference
    file_size_bytes: int
    mime_type: str
    
    # Categorization
    document_type: Literal["agenda", "minutes", "policy", "report", "other"]
    tags: List[DocumentTag] = []
    
    # Owner & Access
    owner_id: ObjectId
    shared_with: List[ObjectId] = []  # User IDs
    shared_organizations: List[ObjectId] = []  # Org IDs
    
    # Metadata
    related_meeting_id: Optional[ObjectId]
    related_activity_id: Optional[ObjectId]
    
    # Status
    is_archived: bool = False
    is_deleted: bool = False
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: ObjectId
    download_count: int = 0
    
    class Settings:
        collection = "documents"
        indexes = [
            ([("organization_id", 1), ("is_archived", 1), ("is_deleted", 1)], {}),
            ([("owner_id", 1), ("created_at", -1)], {}),  # User documents
            ([("related_meeting_id", 1)], {}),  # Meeting documents
            ([("tags.name", 1), ("organization_id", 1)], {}),  # Search by tag
        ]
```

### 5.2 Document Versions Collection

```python
# Collection: document_versions
# Purpose: Track document version history
# Sharding key: document_id

class DocumentVersion(Document):
    # Reference
    document_id: ObjectId  # Shard key
    
    # Version Info
    version_number: int  # 1, 2, 3...
    version_label: Optional[str]  # "Draft", "Final", etc.
    
    # Storage
    file_key: str
    file_size_bytes: int
    
    # Change Info
    change_description: Optional[str]
    changed_by: ObjectId
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "document_versions"
        indexes = [
            ([("document_id", 1), ("version_number", -1)], {}),
            ([("document_id", 1), ("created_at", -1)], {}),
        ]
```

---

## 6. Communication Collections

### 6.1 Notifications Collection

```python
# Collection: notifications
# Purpose: Store user notifications
# Sharding key: user_id

class Notification(Document):
    # Key
    user_id: ObjectId  # Shard key
    
    # Content
    title: str
    message: str
    notification_type: Literal["meeting", "activity", "system", "alert", "admin"]
    
    # Reference
    related_entity_type: Optional[str]  # "meeting", "activity", "document"
    related_entity_id: Optional[ObjectId]
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    # Channel
    channels: List[Literal["in_app", "email", "sms"]] = ["in_app"]
    delivery_status: Dict[str, str] = {}  # {"email": "sent", "sms": "failed"}
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime]  # Auto-delete if set
    
    class Settings:
        collection = "notifications"
        indexes = [
            ([("user_id", 1), ("is_read", 1), ("created_at", -1)], {}),  # Unread
            ([("user_id", 1), ("created_at", -1)], {}),  # Recent
            ([("expires_at", 1)], {"expireAfterSeconds": 0}),  # TTL for auto-delete
        ]
```

### 6.2 Email Templates Collection

```python
# Collection: email_templates
# Purpose: Store email templates for notifications
# Notes: System-wide configuration

class EmailTemplate(Document):
    # Identity
    template_id: str  # "meeting_invitation", "minutes_approved"
    name: str
    description: Optional[str]
    
    # Content
    subject: str
    body_html: str
    body_text: str
    
    # Configuration
    variables: List[str] = []  # Placeholder variables
    preview_text: Optional[str]
    
    # Status
    is_active: bool = True
    version: int = 1
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: ObjectId
    
    class Settings:
        collection = "email_templates"
        indexes = [
            "template_id",  # Lookup by ID
            ([("is_active", 1)], {}),  # Active templates
        ]
```

---

## 7. Audit and Compliance Collections

### 7.1 Audit Logs Collection (Immutable)

```python
# Collection: audit_logs
# Purpose: Immutable append-only audit trail
# Notes: NO DELETES, NO UPDATES (except retention policy)
# Sharding key: organization_id

class AuditLog(Document):
    # Immutable identifier
    audit_log_id: str = Field(default_factory=lambda: str(ObjectId()))
    
    # Timestamps
    timestamp: datetime  # When action occurred
    
    # Actor
    user_id: ObjectId
    user_email: str
    ip_address: str
    user_agent: str
    session_id: str
    
    # Action
    action_type: str  # "meeting.create", "user.update"
    action_category: str  # "meeting", "user", "organization"
    action: str  # "create", "update", "delete"
    
    # Resource
    resource_type: str
    resource_id: ObjectId
    resource_name: Optional[str]
    
    # Organization
    organization_id: ObjectId  # Shard key
    
    # Change Details
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    changes: List[Dict[str, Any]] = []  # Field-level changes
    
    # Result
    status: Literal["success", "failure"] = "success"
    status_code: int = 200
    error_message: Optional[str] = None
    
    # Metadata
    request_id: str  # Trace request
    execution_time_ms: int = 0
    data_size_bytes: int = 0
    
    # Security
    severity: Literal["info", "warning", "critical"] = "info"
    
    # Hash Chain (Tamper Detection)
    hash: str  # SHA-256 hash of this record
    previous_hash: str  # Link to previous record
    
    # Retention
    retention_until: datetime  # When can be deleted (7 years)
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Settings:
        collection = "audit_logs"
        
        # Compound indexes for common queries
        indexes = [
            ([("organization_id", 1), ("timestamp", -1)], {}),  # Org timeline
            ([("user_id", 1), ("timestamp", -1)], {}),  # User actions
            ([("resource_type", 1), ("resource_id", 1), ("timestamp", -1)], {}),  # Resource history
            ([("action_type", 1), ("timestamp", -1)], {}),  # Action timeline
            ([("timestamp", 1)], {}),  # Chronological
            ([("retention_until", 1)], {"expireAfterSeconds": 0}),  # TTL for 7-year deletion
            ([("severity", 1), ("timestamp", -1)], {}),  # Critical actions
        ]
    
    # Validation
    @field_validator('hash')
    @classmethod
    def validate_hash(cls, v):
        # In implementation: Verify SHA-256 format
        if len(v) != 64:  # SHA-256 hex length
            raise ValueError('Invalid hash format')
        return v
```

### 7.2 Data Access Requests Collection

```python
# Collection: data_access_requests
# Purpose: Track GDPR/CCPA data requests
# Sharding key: organization_id

class DataAccessRequest(Document):
    # Identification
    request_id: str = Field(default_factory=lambda: str(ObjectId()))
    organization_id: ObjectId  # Shard key
    user_id: ObjectId
    
    # Request Details
    request_type: Literal["export", "access", "delete", "correct"]
    reason: str
    
    # Status
    status: Literal["submitted", "processing", "approved", "denied", "completed", "cancelled"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Processing
    processed_by: Optional[ObjectId]
    notes: Optional[str]
    
    # Response
    data_export_url: Optional[str]  # Signed URL for download
    expiry_at: Optional[datetime]  # URL expiration
    
    # Compliance
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    
    class Settings:
        collection = "data_access_requests"
        indexes = [
            ([("organization_id", 1), ("status", 1)], {}),
            ([("user_id", 1), ("created_at", -1)], {}),
            ([("created_at", -1)], {}),  # Recent requests
        ]
```

### 7.3 Data Deletion Log Collection

```python
# Collection: data_deletion_logs
# Purpose: Track GDPR right-to-erasure compliance
# Notes: Immutable compliance record

class DeletionLog(Document):
    # Identification
    deletion_id: str = Field(default_factory=lambda: str(ObjectId()))
    
    # Subject
    organization_id: ObjectId
    user_id: ObjectId
    
    # Deletion Details
    deletion_type: Literal["account", "data", "archive"]
    deletion_reason: str
    
    # Records Deleted
    entities_deleted: Dict[str, int]  # {"meetings": 5, "activities": 2}
    
    # Verification
    deleted_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_by: ObjectId
    verification_hash: str  # Hash of deletion receipt
    
    # Retention
    retention_until: datetime  # 7-year compliance retention
    
    class Settings:
        collection = "data_deletion_logs"
        indexes = [
            ([("user_id", 1)], {}),
            ([("deleted_at", -1)], {}),
            ([("retention_until", 1)], {"expireAfterSeconds": 0}),
        ]
```

---

## 8. System Collections

### 8.1 Configurations Collection

```python
# Collection: configurations
# Purpose: System-wide configurations and settings
# Notes: Singleton or small set of global configs

class Configuration(Document):
    # Identity
    config_key: str  # "app.max_file_upload_mb", "security.password_policy"
    description: str
    
    # Value
    value: Any  # Can be string, number, boolean, object
    value_type: str  # "string", "int", "boolean", "json"
    
    # Validation
    default_value: Any
    validation_rule: Optional[str]  # Regex or description
    
    # Status
    is_active: bool = True
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: ObjectId
    
    class Settings:
        collection = "configurations"
        indexes = [
            "config_key",  # Lookup
            ([("is_active", 1)], {}),
        ]
```

### 8.2 Feature Flags Collection

```python
# Collection: feature_flags
# Purpose: Feature toggles for gradual rollout
# Notes: Cached in Redis for performance

class FeatureFlag(Document):
    # Identity
    flag_name: str  # "enable_new_dashboard", "beta_feature_x"
    description: Optional[str]
    
    # Status
    is_enabled: bool = False
    
    # Rollout
    rollout_percentage: int = 0  # 0-100%
    enabled_organizations: List[ObjectId] = []  # Whitelist
    enabled_users: List[ObjectId] = []  # Whitelist
    
    # Dates
    enabled_at: Optional[datetime]
    disabled_at: Optional[datetime]
    sunset_date: Optional[datetime]  # When feature becomes permanent
    
    # System
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: ObjectId
    
    class Settings:
        collection = "feature_flags"
        indexes = [
            "flag_name",
            ([("is_enabled", 1), ("updated_at", -1)], {}),
        ]
```

---

## 9. Relationships and Foreign Keys

### 9.1 Entity Relationship Diagram

```
Users
├─→ Organizations (N:M via organization_members)
├─→ Roles (N:M via membership roles)
├─→ Meetings (1:N as organizer/facilitator)
├─→ Activities (1:N as organizer)
└─→ Sessions (1:N)

Organizations
├─→ Users (N:M via organization_members)
├─→ Meetings (1:N)
├─→ Activities (1:N)
├─→ Documents (1:N)
├─→ Roles (1:N organization-specific)
└─→ Sub-Organizations (Parent 1:N Children)

Meetings
├─→ Organization (N:1)
├─→ Organizer/Facilitator (N:1 to Users)
├─→ Registrations (1:N)
├─→ Minutes (1:1)
└─→ Documents (1:N)

Activities
├─→ Organization (N:1)
├─→ Participants (1:N)
└─→ Engagement Scores (1:N updates)

Documents
├─→ Owner (User, N:1)
├─→ Organization (N:1)
├─→ Versions (1:N)
└─→ Shared Users/Orgs (N:M)
```

### 9.2 Referential Integrity

```
Maintained at Application Level:

1. Foreign Key Validation
   ├─ On insert: Verify referenced document exists
   ├─ On delete: Check for dependent documents
   ├─ On update: Cascade or restrict
   └─ Soft deletes: Preserve references

2. Denormalization Strategy
   ├─ Cache frequently accessed parent data
   ├─ Update denormalized fields on parent change
   ├─ Use event system or background jobs
   └─ Accept eventual consistency

3. Orphan Handling
   ├─ Meeting with no organizer: Prevent deletion
   ├─ Organization with members: Soft delete org
   ├─ Document with no owner: Transfer or archive
   └─ Audit trail: Always retained
```

---

## 10. Indexes Summary

### 10.1 Index Strategy

```
Indexing Rules:

1. Always index:
   ├─ Foreign keys
   ├─ Frequently filtered fields
   ├─ Sort fields
   └─ Range query fields

2. Compound indexes for:
   ├─ multi-field filters (org + status)
   ├─ filter + sort combinations
   └─ pagination queries

3. Avoid indexing:
   ├─ High cardinality with low selectivity
   ├─ Large embedded arrays
   ├─ Rarely used fields
   └─ Fields with < 100 distinct values

4. TTL Indexes for:
   ├─ Session expiration
   ├─ Token blacklists
   ├─ Temporary data cleanup
   └─ Audit log retention
```

### 10.2 Performance Indexes (All Collections)

```
users:
- Single: email (unique), phone, primary_organization_id, created_at
- Compound: (primary_organization_id, status), (locked_until, expireAfterSeconds)

organizations:
- Single: slug, type, parent_id, created_at
- Compound: (parent_id, status), (level, status)

organization_members:
- Unique: (organization_id, user_id)
- Compound: (organization_id, status), (organization_id, joined_at)

meetings:
- Single: organization_id, facilitator_id, status
- Compound: (organization_id, scheduled_at), (status, scheduled_at)

meeting_registrations:
- Unique: (meeting_id, user_id)
- Compound: (meeting_id, registration_status), (user_id, meeting_id)

activities:
- Compound: (organization_id, start_date), (organization_id, status)

documents:
- Single: organization_id, owner_id
- Compound: (organization_id, is_archived, is_deleted)

audit_logs:
- Single: timestamp, severity, organization_id
- Compound: (organization_id, timestamp), (resource_type, resource_id, timestamp)
- TTL: (retention_until, expireAfterSeconds: 0)
```

---

## 11. Data Validation Rules

### 11.1 Field-Level Validation

```python
# Applied in Beanie models using Pydantic validators

class UserValidation:
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: str = Field(..., regex=r'^\+[1-9]\d{1,14}$')  # E.164
    password_hash: str = Field(min_length=60)  # Argon2 output
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

class MeetingValidation:
    title: str = Field(min_length=1, max_length=500)
    scheduled_at: datetime = Field(...)  # Must be future date
    duration_minutes: int = Field(ge=5, le=480)  # 5 min to 8 hours
    capacity: int = Field(ge=1, le=10000)
    
    @validator('scheduled_at')
    def future_date(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Meeting must be scheduled for future')
        return v

class DocumentValidation:
    title: str = Field(max_length=1000)
    file_size_bytes: int = Field(le=104857600)  # 100 MB max
    mime_type: str = Field(regex=r'^[a-zA-Z0-9]+/[a-zA-Z0-9\+\-\.]+$')
```

### 11.2 Collection-Level Validation

```python
# Enforce at database level

unique_constraints = {
    'users': [('email',)],
    'organization_members': [('organization_id', 'user_id')],
    'meeting_registrations': [('meeting_id', 'user_id')],
}

required_fields = {
    'users': ['email', 'password_hash', 'first_name', 'last_name'],
    'meetings': ['title', 'organization_id', 'scheduled_at', 'organizer_id'],
    'activities': ['title', 'organization_id', 'start_date'],
}

enum_constraints = {
    'users.status': ['active', 'inactive', 'suspended', 'deleted'],
    'meetings.status': ['draft', 'scheduled', 'active', 'completed', 'cancelled'],
    'organizations.type': ['national', 'chapter', 'sub_group', 'department', 'working_group'],
}
```

---

## 12. Consistency and ACID Properties

### 12.1 Multi-Document Transactions

```python
# MongoDB 4.0+ supports multi-document ACID transactions

# Example: Update meeting and attendance atomically
async def update_meeting_with_attendance(session, meeting_id, updates):
    """Ensure meeting and registrations stay consistent"""
    async with await client.start_session() as session:
        async with session.start_transaction():
            # Update meeting
            await meetings.update_one(
                {"_id": meeting_id},
                {"$set": updates},
                session=session
            )
            
            # Update related registrations atomically
            await meeting_registrations.update_many(
                {"meeting_id": meeting_id},
                {"$set": {"updated_at": datetime.utcnow()}},
                session=session
            )
            
            # All succeed or all roll back
```

### 12.2 Version-Based Optimistic Locking

```python
# Prevent concurrent modification conflicts

async def update_user_safely(user_id, updates, current_version):
    """Update user only if version matches"""
    result = await users.update_one(
        {"_id": user_id, "version": current_version},
        {
            "$set": updates,
            "$inc": {"version": 1}
        }
    )
    
    if result.modified_count == 0:
        raise ConflictError("User was modified by another process")
    
    return True
```

---

## 13. Performance Optimization Strategies

### 13.1 Query Optimization

```
Optimization Techniques:

1. Projection
   ├─ Only fetch needed fields
   ├─ Exclude large arrays/subdocs
   └─ Example: {email: 1, name: 1, status: 1}

2. Filtering
   ├─ Filter at DB level first
   ├─ Use indexed fields when possible
   ├─ Combine conditions efficiently
   └─ Example: status=active AND organization_id=org_123

3. Aggregation Pipeline
   ├─ Group, match, sort in DB
   ├─ Avoid app-level processing
   ├─ Project minimal fields
   └─ Example: $group → $sort → $limit

4. Pagination
   ├─ Cursor-based for large datasets
   ├─ Limit max results per query
   ├─ Index on sort field
   └─ Example: {created_at: -1} for cursor

5. Denormalization
   ├─ Cache parent data in children
   ├─ Update on parent change
   └─ Example: user_name in registration
```

### 13.2 Storage Optimization

```
Strategies:

1. Compression
   ├─ Large text fields: Compress before store
   ├─ MongoDB compression: WiredTiger default
   └─ Archive: Separate collection for old data

2. TTL Indexes
   ├─ Auto-delete: Sessions after 24h
   ├─ Auto-delete: Notifications after 30 days
   ├─ Auto-delete: Audit logs after 7 years
   └─ Query: Remove expired docs periodically

3. Archival
   ├─ Move completed meetings to archive
   ├─ Separate collection for historical data
   ├─ S3 cold storage for < 1-year-old archives
   └─ Query: Separate archive queries
```

