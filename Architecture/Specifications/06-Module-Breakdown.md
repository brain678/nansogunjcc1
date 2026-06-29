# Module Breakdown and Architecture
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Module Hierarchy Overview

```
NANS Platform
├── User Management Module
├── Organization Management Module
├── Meeting Management Module
├── Activity Management Module
├── Document Management Module
├── Notification and Communication Module
├── Audit and Compliance Module
├── Reporting and Analytics Module
├── Integration and API Module
└── System Infrastructure Module
```

---

## 2. User Management Module

### 2.1 Purpose
Manage user accounts, authentication, authorization, and profile management.

### 2.2 Components

#### Authentication Service
- OAuth 2.0 / OpenID Connect provider integration
- JWT token generation and validation
- Password encryption and hashing
- Multi-factor authentication (MFA)
- Session management
- Device fingerprinting

**Responsibilities:**
- User login/logout
- Token refresh
- Session validation
- MFA enforcement

**Technology:** 
- FastAPI endpoints
- JWT library
- Redis for token storage

---

#### User Service
- User account lifecycle management
- Profile management
- User preference storage
- Account deactivation and removal

**Responsibilities:**
- Create/read/update/delete user accounts
- Profile photo management
- Preference management
- Account status tracking

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- File storage service

---

#### Role and Permission Service
- Role assignment and management
- Permission checking and enforcement
- Delegation handling
- Scope management

**Responsibilities:**
- Assign/revoke roles
- Evaluate permissions
- Check access control
- Log permission changes

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Redis for permission caching
- Custom RBAC/ABAC engine

---

#### Directory Service
- Member directory searchability
- Directory filtering and sorting
- Export functionality

**Responsibilities:**
- Index member profiles
- Support full-text search
- Export directory data
- Privacy filtering

**Technology:**
- Elasticsearch or MongoDB search
- FastAPI endpoints

---

### 2.3 Data Models

```
User
├── id (ObjectId)
├── email (String, unique)
├── password_hash (String)
├── first_name (String)
├── last_name (String)
├── phone (String)
├── date_of_birth (Date)
├── profile_photo_url (String)
├── status (Enum: active, inactive, suspended, deleted)
├── mfa_enabled (Boolean)
├── created_at (DateTime)
├── updated_at (DateTime)
├── preferences (Object)
│   ├── notification_email (Boolean)
│   ├── notification_sms (Boolean)
│   ├── notification_frequency (Enum)
│   └── timezone (String)
└── audit_metadata (Object)

Role
├── id (ObjectId)
├── name (String, unique)
├── description (String)
├── level (Enum: national, chapter, member, functional)
├── permissions (Array<String>)
├── scope (Enum: national, chapter, personal)
├── delegatable (Boolean)
└── created_at (DateTime)

Permission
├── id (ObjectId)
├── name (String, unique)
├── description (String)
├── category (String)
└── resource_type (String)
```

---

### 2.4 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login user |
| `/auth/logout` | POST | Logout user |
| `/auth/refresh` | POST | Refresh token |
| `/auth/mfa/setup` | POST | Setup MFA |
| `/users/{id}/profile` | GET | Get profile |
| `/users/{id}/profile` | PUT | Update profile |
| `/users/{id}/password` | PUT | Change password |
| `/users/search` | GET | Search directory |
| `/roles/{id}` | GET | Get role |
| `/roles` | POST | Create role |
| `/users/{id}/roles` | GET | Get user roles |
| `/users/{id}/roles` | POST | Assign role |

---

## 3. Organization Management Module

### 3.1 Purpose
Manage organizational hierarchy, chapters, divisions, and member enrollment.

### 3.2 Components

#### Organization Service
- Create and manage organizations
- Organizational hierarchy management
- Policy and configuration management

**Responsibilities:**
- Create/read/update/delete organizations
- Manage parent-child relationships
- Prevent circular references
- Store organizational settings

**Technology:**
- FastAPI endpoints
- Beanie ODM with graph modeling
- MongoDB for hierarchy storage

---

#### Member Service
- Enroll and manage members
- Membership status tracking
- Bulk import functionality

**Responsibilities:**
- Create/read/update/delete member records
- Manage membership tiers
- Process bulk imports
- Track membership lifecycle

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Celery for bulk processing
- Email service for notifications

---

#### Hierarchy Service
- Efficient hierarchy traversal
- Role inheritance calculation
- Scope determination

**Responsibilities:**
- Query organization tree
- Calculate inherited permissions
- Determine user scope
- Optimize hierarchy queries

**Technology:**
- MongoDB aggregation pipeline
- Redis for caching
- Custom graph algorithms

---

### 3.3 Data Models

```
Organization
├── id (ObjectId)
├── name (String, unique)
├── description (String)
├── parent_id (ObjectId, nullable)
├── level (Enum: national, chapter, division, sub-group)
├── location (Object)
│   ├── address (String)
│   ├── city (String)
│   ├── state (String)
│   ├── country (String)
│   └── zip_code (String)
├── contact_info (Object)
│   ├── email (String)
│   ├── phone (String)
│   └── website (String)
├── logo_url (String)
├── status (Enum: active, inactive, archived)
├── settings (Object)
│   ├── meeting_frequency (String)
│   ├── membership_required (Boolean)
│   └── public_profile (Boolean)
├── member_count (Integer)
├── created_at (DateTime)
└── updated_at (DateTime)

Membership
├── id (ObjectId)
├── user_id (ObjectId)
├── organization_id (ObjectId)
├── tier (Enum: standard, premium, lifetime)
├── status (Enum: active, inactive, suspended)
├── joined_date (DateTime)
├── renewal_date (DateTime)
├── metadata (Object)
└── created_at (DateTime)
```

---

### 3.4 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/organizations` | POST | Create organization |
| `/organizations/{id}` | GET | Get organization |
| `/organizations/{id}` | PUT | Update organization |
| `/organizations/{id}/hierarchy` | GET | Get hierarchy tree |
| `/organizations/{id}/members` | GET | Get members |
| `/organizations/{id}/members` | POST | Add member |
| `/organizations/bulk-import` | POST | Bulk import members |
| `/memberships/{id}` | GET | Get membership |
| `/memberships/{id}` | PUT | Update membership |

---

## 4. Meeting Management Module

### 4.1 Purpose
Manage meeting lifecycle from creation through minutes and archival.

### 4.2 Components

#### Meeting Service
- Create and manage meetings
- Meeting scheduling and calendar management
- Recurring meeting support

**Responsibilities:**
- CRUD operations for meetings
- Conflict detection
- Recurrence pattern handling
- Calendar synchronization

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- iCal library for calendar format

---

#### Registration Service
- Manage meeting registrations
- Waitlist management
- Capacity enforcement

**Responsibilities:**
- Register/unregister attendees
- Manage waitlists
- Enforce capacity limits
- Send confirmations

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Notification service integration

---

#### Check-in Service
- Manage attendee check-in
- QR code generation
- Attendance tracking

**Responsibilities:**
- Generate QR codes
- Process check-ins
- Track late arrivals
- Produce attendance reports

**Technology:**
- QR code library
- FastAPI endpoints
- Real-time updates via WebSocket

---

#### Minutes Service
- Template management
- Action item tracking
- Decision recording
- Approval workflow

**Responsibilities:**
- Create/edit minutes from templates
- Track action items
- Record decisions
- Manage approval workflow
- Distribute approved minutes

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Workflow engine integration
- Document service integration

---

### 4.3 Data Models

```
Meeting
├── id (ObjectId)
├── organization_id (ObjectId)
├── title (String)
├── description (String)
├── type (Enum: virtual, in-person, hybrid)
├── scheduled_at (DateTime)
├── duration_minutes (Integer)
├── location (String)
├── virtual_meeting_link (String)
├── agenda (Array<String>)
├── organizer_id (ObjectId)
├── facilitator_id (ObjectId)
├── capacity (Integer)
├── is_recurring (Boolean)
├── recurrence_pattern (Object)
├── status (Enum: draft, scheduled, active, completed, cancelled)
├── created_at (DateTime)
└── updated_at (DateTime)

MeetingRegistration
├── id (ObjectId)
├── meeting_id (ObjectId)
├── user_id (ObjectId)
├── registered_at (DateTime)
├── status (Enum: registered, waitlisted, checked-in, no-show, cancelled)
├── check_in_time (DateTime)
└── metadata (Object)

MeetingMinutes
├── id (ObjectId)
├── meeting_id (ObjectId)
├── recorder_id (ObjectId)
├── attendees (Array<ObjectId>)
├── action_items (Array<Object>)
│   ├── description (String)
│   ├── owner_id (ObjectId)
│   ├── due_date (DateTime)
│   └── status (Enum: open, completed, cancelled)
├── decisions (Array<Object>)
│   ├── decision (String)
│   ├── impact (String)
│   └── owner_id (ObjectId)
├── approval_status (Enum: draft, approved, archived)
├── approver_id (ObjectId)
├── created_at (DateTime)
└── updated_at (DateTime)
```

---

### 4.4 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/meetings` | POST | Create meeting |
| `/meetings/{id}` | GET | Get meeting |
| `/meetings/{id}` | PUT | Update meeting |
| `/meetings/{id}/cancel` | POST | Cancel meeting |
| `/meetings/{id}/register` | POST | Register attendee |
| `/meetings/{id}/unregister` | DELETE | Unregister attendee |
| `/meetings/{id}/check-in` | POST | Check in attendee |
| `/meetings/{id}/minutes` | POST | Record minutes |
| `/meetings/{id}/minutes/{mid}` | PUT | Update minutes |
| `/meetings/{id}/minutes/{mid}/approve` | POST | Approve minutes |

---

## 5. Activity Management Module

### 5.1 Purpose
Track organizational activities and member participation.

### 5.2 Components

#### Activity Service
- Create and manage activities
- Activity categorization
- Activity lifecycle

**Responsibilities:**
- CRUD operations for activities
- Category management
- Status tracking
- Outcome recording

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB

---

#### Participation Service
- Record participant participation
- Engagement scoring
- Participation history

**Responsibilities:**
- Record participation
- Calculate engagement scores
- Track participation streaks
- Generate participation reports

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Analytics service integration

---

### 5.3 Data Models

```
Activity
├── id (ObjectId)
├── organization_id (ObjectId)
├── title (String)
├── description (String)
├── category (String)
├── tags (Array<String>)
├── organizer_id (ObjectId)
├── start_date (DateTime)
├── end_date (DateTime)
├── location (String)
├── status (Enum: planned, in-progress, completed, cancelled)
├── participant_count (Integer)
├── outcomes (Object)
└── created_at (DateTime)

Participation
├── id (ObjectId)
├── activity_id (ObjectId)
├── user_id (ObjectId)
├── participation_date (DateTime)
├── participation_type (String)
├── engagement_points (Integer)
└── created_at (DateTime)

EngagementMetrics
├── id (ObjectId)
├── user_id (ObjectId)
├── organization_id (ObjectId)
├── total_participation_count (Integer)
├── engagement_score (Float)
├── participation_streak (Integer)
├── last_participation_date (DateTime)
├── engagement_level (Enum: low, medium, high)
└── updated_at (DateTime)
```

---

## 6. Document Management Module

### 6.1 Purpose
Store, organize, and manage organizational documents.

### 6.2 Components

#### Document Service
- Document upload and storage
- Document versioning
- Document metadata management

**Responsibilities:**
- Store documents
- Manage versions
- Handle metadata
- Coordinate with storage service

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Object storage (S3 or equivalent)

---

#### Permissions Service
- Document-level access control
- Share link generation
- Permission audit

**Responsibilities:**
- Manage document permissions
- Generate sharing links
- Track document access
- Enforce expiration

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Cache for permission checks

---

#### Search Service
- Full-text document search
- Metadata filtering

**Responsibilities:**
- Index documents
- Execute searches
- Filter results

**Technology:**
- Elasticsearch or MongoDB full-text search
- FastAPI endpoints

---

### 6.3 Data Models

```
Document
├── id (ObjectId)
├── organization_id (ObjectId)
├── uploader_id (ObjectId)
├── title (String)
├── description (String)
├── file_path (String)
├── file_size (Integer)
├── file_type (String)
├── tags (Array<String>)
├── current_version (Integer)
├── status (Enum: draft, published, archived)
├── virus_scanned (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)

DocumentVersion
├── id (ObjectId)
├── document_id (ObjectId)
├── version_number (Integer)
├── file_path (String)
├── uploaded_by (ObjectId)
├── created_at (DateTime)
└── change_summary (String)

DocumentShare
├── id (ObjectId)
├── document_id (ObjectId)
├── shared_by (ObjectId)
├── shared_with (ObjectId or Array<ObjectId>)
├── permission_level (Enum: view, comment, edit)
├── expiry_date (DateTime, nullable)
├── share_token (String, unique)
└── created_at (DateTime)
```

---

## 7. Notification and Communication Module

### 7.1 Purpose
Multi-channel notification delivery and user communication.

### 7.2 Components

#### Notification Service
- Create and queue notifications
- Channel selection
- Preference enforcement

**Responsibilities:**
- Create notifications
- Queue for delivery
- Respect user preferences
- Track notification status

**Technology:**
- FastAPI endpoints
- Celery for async processing
- Redis for queue

---

#### Email Service
- Email template rendering
- Email delivery
- Bounce handling

**Responsibilities:**
- Render email templates
- Send emails
- Track deliverability
- Handle bounces

**Technology:**
- SendGrid or similar provider
- Email template engine
- Bounce tracking

---

#### SMS Service
- SMS delivery
- Character counting

**Responsibilities:**
- Send SMS messages
- Handle delivery status
- Track costs

**Technology:**
- Twilio or similar provider
- Message formatting

---

### 7.3 Data Models

```
Notification
├── id (ObjectId)
├── recipient_id (ObjectId)
├── channel (Enum: email, sms, in-app, push)
├── type (Enum: meeting_reminder, activity_update, announcement, etc.)
├── subject (String)
├── content (String)
├── template_id (String, nullable)
├── template_data (Object)
├── status (Enum: queued, sent, delivered, failed, bounced)
├── created_at (DateTime)
├── sent_at (DateTime)
└── delivered_at (DateTime)

NotificationPreference
├── id (ObjectId)
├── user_id (ObjectId)
├── email_enabled (Boolean)
├── sms_enabled (Boolean)
├── in_app_enabled (Boolean)
├── push_enabled (Boolean)
├── notification_frequency (Enum: immediate, daily, weekly)
├── quiet_hours (Object)
│   ├── start (Time)
│   └── end (Time)
└── updated_at (DateTime)
```

---

## 8. Audit and Compliance Module

### 8.1 Purpose
Comprehensive audit trail recording and compliance reporting.

### 8.2 Components

#### Audit Service
- Log all system activities
- Maintain immutable audit trail
- Query and filter capabilities

**Responsibilities:**
- Record all changes
- Ensure immutability
- Query logs efficiently
- Generate audit reports

**Technology:**
- Append-only MongoDB collection
- FastAPI endpoints
- Immutable storage

---

#### Compliance Service
- GDPR/CCPA/SOC2 compliance
- Privacy policy enforcement
- Consent management

**Responsibilities:**
- Manage consent
- Process data requests
- Enforce privacy policies
- Generate compliance reports

**Technology:**
- FastAPI endpoints
- Beanie ODM for MongoDB
- Compliance workflow engine

---

### 8.3 Data Models

```
AuditLog
├── id (ObjectId)
├── timestamp (DateTime)
├── user_id (ObjectId)
├── action (String)
├── resource_type (String)
├── resource_id (ObjectId)
├── organization_id (ObjectId)
├── before_state (Object)
├── after_state (Object)
├── ip_address (String)
├── user_agent (String)
├── status (Enum: success, failure)
└── error_message (String, nullable)

Consent
├── id (ObjectId)
├── user_id (ObjectId)
├── consent_type (Enum: privacy_policy, terms_of_service, marketing, etc.)
├── consented_at (DateTime)
├── version (String)
└── metadata (Object)

DataRequest
├── id (ObjectId)
├── user_id (ObjectId)
├── request_type (Enum: access, export, deletion)
├── status (Enum: pending, processing, completed, denied)
├── requested_at (DateTime)
├── completed_at (DateTime)
├── result_url (String)
└── metadata (Object)
```

---

## 9. Reporting and Analytics Module

### 9.1 Purpose
Generate reports and provide analytics dashboards.

### 9.2 Components

#### Analytics Service
- Metrics collection and calculation
- Real-time dashboards
- Historical data analysis

**Responsibilities:**
- Calculate metrics
- Store metrics
- Query metrics efficiently
- Feed dashboards

**Technology:**
- FastAPI endpoints
- Redis for real-time metrics
- BI tools integration

---

#### Report Service
- Generate reports on demand
- Schedule report generation
- Export reports

**Responsibilities:**
- Generate reports
- Schedule execution
- Export in multiple formats
- Distribute reports

**Technology:**
- FastAPI endpoints
- Celery for scheduled jobs
- Report generation library

---

### 9.3 Data Models

```
Report
├── id (ObjectId)
├── name (String)
├── description (String)
├── report_type (String)
├── creator_id (ObjectId)
├── definition (Object)
│   ├── metrics (Array<String>)
│   ├── filters (Object)
│   └── grouping (Array<String>)
├── schedule (String, nullable)
├── distribution_list (Array<String>)
├── created_at (DateTime)
└── updated_at (DateTime)

Metric
├── id (ObjectId)
├── name (String)
├── calculation (String)
├── dimension (Array<String>)
├── data_points (Array<Object>)
│   ├── timestamp (DateTime)
│   └── value (Number)
└── updated_at (DateTime)
```

---

## 10. Integration and API Module

### 10.1 Purpose
Provide external APIs and integrate with third-party services.

### 10.2 Components

#### API Gateway
- Request routing
- Rate limiting
- API key management
- CORS handling

**Technology:**
- Kong or AWS API Gateway
- FastAPI middlewares

---

#### Webhook Service
- Webhook event triggering
- Retry logic
- Webhook management

**Technology:**
- Celery for async delivery
- Retry mechanism

---

#### OAuth Provider Integration
- Third-party provider integration
- Token management

**Technology:**
- OAuth 2.0 libraries
- Token refresh mechanism

---

## 11. System Infrastructure Module

### 11.1 Purpose
Manage system-level infrastructure and utilities.

### 11.2 Components

#### Cache Service
- Distributed caching
- Cache invalidation
- Cache warming

**Technology:**
- Redis cluster
- Serialization libraries

---

#### Queue Service
- Asynchronous job processing
- Job scheduling
- Retry mechanisms

**Technology:**
- Celery with Redis or RabbitMQ
- APScheduler for scheduling

---

#### Logging Service
- Centralized logging
- Log aggregation
- Log analysis

**Technology:**
- ELK stack
- Structured logging

---

#### Monitoring Service
- Application monitoring
- Performance monitoring
- Alert management

**Technology:**
- Prometheus
- Grafana
- AlertManager

---

## 12. Module Integration Points

### 12.1 Cross-Module Dependencies

```
User Management
    ├── Organization Management (member validation)
    ├── Audit and Compliance (user events)
    └── Notification (user preferences)

Organization Management
    ├── User Management (member management)
    ├── Meeting Management (organization reference)
    ├── Activity Management (organization reference)
    └── Audit and Compliance (hierarchy changes)

Meeting Management
    ├── Organization Management (location reference)
    ├── Notification (attendance reminders)
    ├── Document Management (minutes/documents)
    └── Audit and Compliance (meeting events)

Activity Management
    ├── Organization Management (activity location)
    ├── User Management (participation tracking)
    ├── Audit and Compliance (participation events)
    └── Reporting (engagement metrics)

Document Management
    ├── User Management (permissions)
    ├── Organization Management (organization documents)
    └── Audit and Compliance (document access)

Notification
    ├── User Management (preferences, email)
    ├── Meeting Management (reminders)
    ├── Activity Management (updates)
    └── System Infrastructure (queue service)

Audit and Compliance
    ├── All modules (audit trails)
    ├── User Management (data privacy)
    └── Reporting (compliance reports)

Reporting and Analytics
    ├── All modules (data sources)
    ├── Audit and Compliance (audit reports)
    └── System Infrastructure (analytics storage)
```

---

## 13. Module Deployment Strategy

### 13.1 Deployment Units

Each module deploys as independent microservice or grouped services:

```
Deployment Unit 1: User & Auth Services
├── Authentication Service
├── User Service
└── Role & Permission Service

Deployment Unit 2: Organization Services
├── Organization Service
├── Member Service
└── Hierarchy Service

Deployment Unit 3: Meeting & Activity Services
├── Meeting Service
├── Registration Service
├── Minutes Service
└── Activity Service

Deployment Unit 4: Document & Notification Services
├── Document Service
├── Notification Service
├── Email Service
└── SMS Service

Deployment Unit 5: Audit & Analytics Services
├── Audit Service
├── Analytics Service
├── Report Service
└── Compliance Service

Deployment Unit 6: Infrastructure Services
├── Cache Service
├── Queue Service
├── Logging Service
└── Monitoring Service
```

---

## 14. Module Versioning

### 14.1 API Versioning

All API endpoints versioned:
- Current: `/api/v1/*`
- Deprecated: `/api/v0/*` (sunset after 6 months)
- Future: `/api/v2/*` (development)

### 14.2 Backward Compatibility

- Breaking changes require new major version
- Minor changes backward compatible
- Deprecation warnings for 6+ months before removal

