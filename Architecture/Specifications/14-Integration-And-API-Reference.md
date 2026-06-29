# Integration and API Reference Guide
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. API Overview

### 1.1 API Endpoints Structure

```
Base URL: https://api.nans.org/api/v1

Endpoint Pattern: 
  https://api.nans.org/api/v1/{resource}/{resource_id}/{sub_resource}

Examples:
├─ https://api.nans.org/api/v1/users
├─ https://api.nans.org/api/v1/users/user_123
├─ https://api.nans.org/api/v1/users/user_123/meetings
├─ https://api.nans.org/api/v1/organizations/org_456
├─ https://api.nans.org/api/v1/organizations/org_456/members
└─ https://api.nans.org/api/v1/meetings/meeting_789/attendees

API Versioning:
├─ Current: v1
├─ Versioning strategy: URL-based (/api/v1, /api/v2)
├─ Support windows:
│   ├─ Current version: 2 years
│   ├─ Previous version: 1 year (maintenance only)
│   └─ Deprecation notice: 6 months before removal
└─ Backward compatibility: Best effort for 1 version
```

### 1.2 Authentication

```
Authentication Methods:

JWT Bearer Token:
├─ Header: Authorization: Bearer <jwt_token>
├─ Token format: {header}.{payload}.{signature}
├─ Lifetime: 15 minutes (access token)
├─ Refresh: POST /auth/refresh with refresh_token
├─ Revocation: Blacklist on logout/password change
└─ Scope: Permissions embedded in token

OAuth 2.0:
├─ Supported providers: Google, Microsoft, Custom
├─ Flow: Authorization Code flow
├─ Redirect URI: https://app.nans.org/auth/callback
├─ Scope: openid, email, profile, custom
└─ Token exchange: Server-to-server

API Keys (Service Accounts):
├─ Format: sk_live_xxx (production) or sk_test_xxx (development)
├─ Header: X-API-Key: <api_key>
├─ Rotation: Every 90 days recommended
├─ Scopes: Limited to specific actions
├─ Rate limit: Higher than user tokens
└─ Usage: Service-to-service, batch operations

CORS Configuration:
├─ Allowed origins: https://app.nans.org (prod)
├─ Allowed methods: GET, POST, PUT, DELETE, PATCH
├─ Allowed headers: Content-Type, Authorization, X-Request-ID
├─ Credentials: Included (for cookie-based auth)
├─ Max age: 86400 seconds
└─ Preflight caching: Enabled
```

---

## 2. Core API Resources

### 2.1 User Management APIs

```
Resource: /api/v1/users

Endpoints:

1. Create User (POST)
   ├─ Path: POST /users
   ├─ Auth: Admin role
   ├─ Request body:
   │   ├─ email: string (unique)
   │   ├─ first_name: string
   │   ├─ last_name: string
   │   ├─ phone: string
   │   ├─ organization_id: ObjectId
   │   ├─ password: string (min 12 chars)
   │   └─ roles: string[]
   │
   ├─ Response: 201 Created
   │   ├─ user_id: ObjectId
   │   ├─ email: string
   │   ├─ status: "active"
   │   └─ created_at: ISO 8601
   │
   └─ Errors: 400 (validation), 409 (duplicate), 403 (unauthorized)

2. Get User (GET)
   ├─ Path: GET /users/{user_id}
   ├─ Auth: Authenticated user (self) or admin
   ├─ Response: 200 OK
   │   ├─ user_id: ObjectId
   │   ├─ email: string
   │   ├─ name: string
   │   ├─ profile: {...}
   │   ├─ organizations: {...}
   │   ├─ roles: string[]
   │   └─ engagement_score: number
   │
   └─ Errors: 404 (not found), 403 (forbidden)

3. Update User Profile (PATCH)
   ├─ Path: PATCH /users/{user_id}
   ├─ Auth: Authenticated user (self) or admin
   ├─ Request body (any of):
   │   ├─ first_name: string
   │   ├─ last_name: string
   │   ├─ phone: string
   │   ├─ bio: string
   │   ├─ profile_photo_url: string
   │   └─ preferences: {...}
   │
   ├─ Response: 200 OK
   │   └─ Updated user object
   │
   └─ Errors: 400 (validation), 404 (not found), 409 (conflict)

4. List Users (GET)
   ├─ Path: GET /users?organization_id={org_id}&role={role}&status={status}
   ├─ Query params:
   │   ├─ organization_id: ObjectId (optional)
   │   ├─ role: string (optional)
   │   ├─ status: active|inactive (optional)
   │   ├─ limit: integer (1-1000, default 100)
   │   ├─ offset: integer (default 0)
   │   └─ sort: string (email, name, created_at)
   │
   ├─ Auth: Admin or org admin
   ├─ Response: 200 OK
   │   ├─ total_count: integer
   │   ├─ returned_count: integer
   │   ├─ offset: integer
   │   └─ users: User[]
   │
   └─ Errors: 403 (forbidden)

5. Change Password (POST)
   ├─ Path: POST /users/{user_id}/password
   ├─ Auth: Authenticated user (self)
   ├─ Request body:
   │   ├─ current_password: string
   │   └─ new_password: string (min 12 chars)
   │
   ├─ Response: 200 OK
   │   ├─ message: "Password changed successfully"
   │   └─ requires_reauth: boolean
   │
   └─ Errors: 400 (validation), 401 (wrong password), 403 (forbidden)

6. Enable MFA (POST)
   ├─ Path: POST /users/{user_id}/mfa/enable
   ├─ Auth: Authenticated user (self)
   ├─ Query: method=totp|sms|email
   ├─ Response: 200 OK
   │   ├─ method: string
   │   ├─ secret: string (if TOTP)
   │   ├─ qr_code_url: string
   │   └─ backup_codes: string[]
   │
   └─ Errors: 400 (already enabled), 403 (forbidden)

7. Delete User (DELETE)
   ├─ Path: DELETE /users/{user_id}
   ├─ Auth: Admin only
   ├─ Response: 204 No Content
   ├─ Side effects:
   │   ├─ User soft-deleted
   │   ├─ Account deactivated
   │   ├─ All sessions invalidated
   │   ├─ Data anonymized (GDPR compliant)
   │   └─ Audit logged
   │
   └─ Errors: 403 (forbidden), 404 (not found)
```

### 2.2 Meeting Management APIs

```
Resource: /api/v1/meetings

Endpoints:

1. Create Meeting (POST)
   ├─ Path: POST /meetings
   ├─ Auth: Chapter admin or higher
   ├─ Request body:
   │   ├─ title: string (required)
   │   ├─ description: string
   │   ├─ organization_id: ObjectId (required)
   │   ├─ scheduled_at: ISO 8601 (required)
   │   ├─ duration_minutes: integer (required)
   │   ├─ location: string
   │   ├─ meeting_link: URL (for virtual meetings)
   │   ├─ capacity: integer (max attendees)
   │   ├─ organizer_id: ObjectId
   │   ├─ facilitator_id: ObjectId (required)
   │   ├─ agenda: string[]
   │   ├─ meeting_type: in_person|virtual|hybrid
   │   ├─ visibility: public|private|members_only
   │   └─ registration_enabled: boolean
   │
   ├─ Response: 201 Created
   │   ├─ meeting_id: ObjectId
   │   ├─ status: "draft"
   │   ├─ created_at: ISO 8601
   │   └─ organizer_url: string (for editing)
   │
   └─ Errors: 400 (validation), 403 (unauthorized), 409 (conflict)

2. Publish Meeting (PATCH)
   ├─ Path: PATCH /meetings/{meeting_id}
   ├─ Query: action=publish
   ├─ Auth: Meeting organizer or admin
   ├─ Request body: {} (empty)
   ├─ Response: 200 OK
   │   └─ status: "scheduled"
   │
   ├─ Side effects:
   │   ├─ Notifications sent to eligible attendees
   │   ├─ Calendar invites generated
   │   ├─ Public availability updated
   │   └─ Cache invalidated
   │
   └─ Errors: 400 (invalid state), 403 (forbidden), 404 (not found)

3. Register for Meeting (POST)
   ├─ Path: POST /meetings/{meeting_id}/registrations
   ├─ Auth: Authenticated member
   ├─ Request body:
   │   ├─ user_id: ObjectId (auto-filled or provided)
   │   ├─ dietary_restrictions: string
   │   ├─ special_accommodations: string
   │   └─ agreed_to_terms: boolean
   │
   ├─ Response: 201 Created
   │   ├─ registration_id: ObjectId
   │   ├─ status: "registered" | "waitlisted"
   │   ├─ confirmation_sent: boolean
   │   └─ created_at: ISO 8601
   │
   ├─ Errors: 
   │   ├─ 400 (already registered, capacity full)
   │   ├─ 403 (not eligible, suspended)
   │   └─ 404 (meeting not found)
   │
   └─ Automatic waitlist management if capacity exceeded

4. Check In Member (POST)
   ├─ Path: POST /meetings/{meeting_id}/check-in
   ├─ Auth: Facilitator or admin
   ├─ Request body:
   │   ├─ member_email: string OR
   │   ├─ member_id: ObjectId OR
   │   └─ qr_code_token: string
   │
   ├─ Response: 200 OK
   │   ├─ registration_id: ObjectId
   │   ├─ member_name: string
   │   ├─ check_in_time: ISO 8601
   │   ├─ late: boolean
   │   └─ attendance_summary: {...}
   │
   └─ Errors: 400 (not registered), 403 (forbidden), 404 (not found)

5. Record Meeting Minutes (POST)
   ├─ Path: POST /meetings/{meeting_id}/minutes
   ├─ Auth: Facilitator or admin
   ├─ Request body:
   │   ├─ attendee_list: ObjectId[]
   │   ├─ action_items: [
   │   │   ├─ description: string
   │   │   ├─ assigned_to: ObjectId
   │   │   ├─ due_date: ISO 8601
   │   │   └─ priority: low|medium|high
   │   ├─ decisions: string[]
   │   ├─ notes: string
   │   ├─ recommendations: string
   │   └─ next_steps: string
   │
   ├─ Response: 201 Created
   │   ├─ minutes_id: ObjectId
   │   ├─ status: "draft"
   │   └─ created_at: ISO 8601
   │
   └─ Errors: 400 (meeting not completed), 403 (unauthorized)

6. Get Meeting Attendees (GET)
   ├─ Path: GET /meetings/{meeting_id}/attendees
   ├─ Query params:
   │   ├─ status: all|registered|checked_in|absent (optional)
   │   ├─ limit: integer (default 100)
   │   └─ offset: integer (default 0)
   │
   ├─ Auth: Facilitator, organizer, or admin
   ├─ Response: 200 OK
   │   ├─ total: integer
   │   ├─ attendees: [
   │   │   ├─ registration_id: ObjectId
   │   │   ├─ member: {...}
   │   │   ├─ status: string
   │   │   ├─ check_in_time: ISO 8601
   │   │   └─ late: boolean
   │
   └─ Errors: 403 (forbidden), 404 (not found)

7. Cancel Meeting (POST)
   ├─ Path: POST /meetings/{meeting_id}?action=cancel
   ├─ Auth: Organizer or admin
   ├─ Request body:
   │   ├─ reason: string (optional)
   │   └─ notify_attendees: boolean (default true)
   │
   ├─ Response: 200 OK
   │   └─ status: "cancelled"
   │
   ├─ Side effects:
   │   ├─ All registrations cancelled
   │   ├─ Notifications sent
   │   ├─ Calendar invites revoked
   │   └─ Audit logged
   │
   └─ Errors: 400 (invalid state), 403 (forbidden)
```

### 2.3 Organization Management APIs

```
Resource: /api/v1/organizations

Endpoints:

1. Create Organization (POST)
   ├─ Path: POST /organizations
   ├─ Auth: National admin only
   ├─ Request body:
   │   ├─ name: string (required)
   │   ├─ type: chapter|sub_group|department|other
   │   ├─ parent_id: ObjectId (optional)
   │   ├─ location: string
   │   ├─ description: string
   │   ├─ logo_url: URL
   │   ├─ contact_email: string
   │   ├─ contact_phone: string
   │   └─ metadata: {...}
   │
   ├─ Response: 201 Created
   │   ├─ organization_id: ObjectId
   │   ├─ created_at: ISO 8601
   │   └─ admin_url: string
   │
   └─ Errors: 400 (validation), 403 (unauthorized), 409 (duplicate name)

2. Get Organization (GET)
   ├─ Path: GET /organizations/{org_id}
   ├─ Auth: Any authenticated user
   ├─ Response: 200 OK
   │   ├─ organization_id: ObjectId
   │   ├─ name: string
   │   ├─ type: string
   │   ├─ hierarchy: {...}
   │   ├─ member_count: integer
   │   ├─ active_meetings: integer
   │   ├─ metadata: {...}
   │   └─ created_at: ISO 8601
   │
   └─ Errors: 404 (not found)

3. Add Member to Organization (POST)
   ├─ Path: POST /organizations/{org_id}/members
   ├─ Auth: Org admin or higher
   ├─ Request body:
   │   ├─ user_id: ObjectId (required)
   │   ├─ role: string (default "member")
   │   ├─ status: active|inactive|suspended
   │   ├─ start_date: ISO 8601 (optional)
   │   ├─ end_date: ISO 8601 (optional)
   │   └─ notes: string
   │
   ├─ Response: 201 Created
   │   ├─ membership_id: ObjectId
   │   ├─ status: "active"
   │   └─ created_at: ISO 8601
   │
   └─ Errors: 400 (already member), 403 (unauthorized), 409 (conflict)

4. List Organization Members (GET)
   ├─ Path: GET /organizations/{org_id}/members
   ├─ Query params:
   │   ├─ status: active|inactive|all (default active)
   │   ├─ role: string (optional)
   │   ├─ limit: integer (default 100)
   │   ├─ offset: integer (default 0)
   │   └─ search: string (name/email search)
   │
   ├─ Auth: Org member or admin
   ├─ Response: 200 OK
   │   ├─ total_count: integer
   │   ├─ members: [...]
   │   └─ offset: integer
   │
   └─ Errors: 403 (forbidden), 404 (not found)

5. Remove Member (DELETE)
   ├─ Path: DELETE /organizations/{org_id}/members/{user_id}
   ├─ Auth: Org admin
   ├─ Response: 204 No Content
   ├─ Side effects:
   │   ├─ Membership deactivated
   │   ├─ Roles revoked
   │   ├─ Notifications sent
   │   └─ Audit logged
   │
   └─ Errors: 403 (forbidden), 404 (not found)
```

---

## 3. Pagination and Filtering

### 3.1 Pagination

```
Standard Pagination:

Query Parameters:
├─ limit: integer
│   ├─ Range: 1-1000
│   ├─ Default: 100
│   └─ Description: Records to return per page
│
├─ offset: integer
│   ├─ Default: 0
│   └─ Description: Number of records to skip
│
└─ cursor: string (optional)
    ├─ Opaque cursor for pagination
    ├─ Use in response for next page
    └─ Better for large datasets

Response Format:
{
  "total_count": 5000,
  "returned_count": 100,
  "offset": 0,
  "limit": 100,
  "next_cursor": "abc123...",
  "has_next": true,
  "data": [...]
}

Cursor-Based Pagination:
├─ Request: GET /endpoint?cursor=abc123&limit=100
├─ Response includes: next_cursor
├─ Advantages:
│   ├─ Efficient for large offsets
│   ├─ Handles real-time data changes
│   ├─ No N+1 query problem
│   └─ Database-independent
│
└─ Recommended for: All list endpoints
```

### 3.2 Filtering

```
Filter Syntax:

Query String Format:
├─ GET /meetings?organization_id=org_123&status=scheduled&facilitator=user_456
├─ Multiple values: ?status=scheduled&status=completed (array)
├─ Range: ?created_after=2026-01-01&created_before=2026-12-31
└─ Search: ?search=planning%20meeting

Supported Filters by Endpoint:

Meetings:
├─ organization_id: ObjectId
├─ status: draft|scheduled|active|completed|cancelled
├─ facilitator: ObjectId
├─ start_date: ISO 8601
├─ end_date: ISO 8601
├─ meeting_type: in_person|virtual|hybrid
├─ created_after: ISO 8601
├─ created_before: ISO 8601
└─ search: string (title, description)

Users:
├─ organization_id: ObjectId
├─ status: active|inactive|suspended
├─ role: string
├─ created_after: ISO 8601
├─ created_before: ISO 8601
└─ search: string (email, name)

Activities:
├─ organization_id: ObjectId
├─ category: string
├─ status: active|completed|archived
├─ start_date: ISO 8601
├─ end_date: ISO 8601
├─ coordinator: ObjectId
└─ search: string (title, description)
```

---

## 4. Error Handling

### 4.1 Error Response Format

```
Standard Error Response:

{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "User-friendly error message",
    "status": 400,
    "request_id": "req_abc123",
    "timestamp": "2026-06-23T10:30:45Z",
    "details": {
      "field": "email",
      "validation_error": "Invalid email format",
      "value": "not-an-email"
    },
    "doc_url": "https://docs.nans.org/errors/INVALID_REQUEST"
  }
}

Error Codes:

4xx - Client Errors:
├─ 400 - BAD_REQUEST: Invalid parameters
├─ 401 - UNAUTHORIZED: Authentication required
├─ 403 - FORBIDDEN: Insufficient permissions
├─ 404 - NOT_FOUND: Resource not found
├─ 409 - CONFLICT: Resource already exists
├─ 422 - UNPROCESSABLE_ENTITY: Validation failed
├─ 429 - RATE_LIMITED: Too many requests
└─ 500 - INTERNAL_ERROR: Server error

Error Categories:

Authentication Errors:
├─ INVALID_TOKEN: Token expired or invalid
├─ MFA_REQUIRED: Additional authentication needed
├─ SESSION_EXPIRED: Session timeout
└─ INSUFFICIENT_SCOPE: Token lacks required scope

Validation Errors:
├─ INVALID_EMAIL: Email format invalid
├─ INVALID_DATE: Date format invalid
├─ REQUIRED_FIELD: Missing required field
├─ INVALID_ENUM: Invalid enum value
└─ CONSTRAINT_VIOLATION: Business rule violation

Permission Errors:
├─ INSUFFICIENT_ROLE: Role too low
├─ RESOURCE_RESTRICTED: Resource access denied
├─ ORGANIZATION_NOT_FOUND: Org access denied
└─ DEPARTMENT_RESTRICTED: Department access denied
```

### 4.2 Rate Limiting

```
Rate Limit Headers:

Response Headers:
├─ X-RateLimit-Limit: 1000 (requests per window)
├─ X-RateLimit-Remaining: 950 (remaining requests)
├─ X-RateLimit-Reset: 1234567890 (Unix timestamp)
└─ Retry-After: 60 (seconds to wait)

Rate Limit Tiers:

Unauthenticated Users:
├─ Limit: 100 requests per hour per IP
└─ Scope: IP address

Authenticated Users:
├─ Limit: 1000 requests per hour per user
├─ Premium tier: 10,000 requests per hour
└─ Scope: User ID

Service Accounts:
├─ Limit: 100,000 requests per hour
├─ Burst: 10,000 requests per minute
└─ Scope: API key

Exceeding Limits:
├─ Status: 429 Too Many Requests
├─ Response: Error with retry info
├─ Action: Exponential backoff recommended
└─ Notification: Alert to user/service
```

---

## 5. Webhooks

### 5.1 Webhook Events

```
Supported Events:

User Events:
├─ user.created
├─ user.updated
├─ user.activated
├─ user.deactivated
├─ user.deleted
├─ user.password_changed
└─ user.mfa_enabled

Meeting Events:
├─ meeting.created
├─ meeting.published
├─ meeting.updated
├─ meeting.cancelled
├─ meeting.started
├─ meeting.completed
├─ registration.created
├─ registration.cancelled
├─ check_in.recorded
└─ minutes.approved

Organization Events:
├─ organization.created
├─ organization.updated
├─ member.added
├─ member.removed
├─ member.role_changed
└─ member.status_changed

Activity Events:
├─ activity.created
├─ activity.completed
├─ participation.recorded
└─ engagement.updated
```

### 5.2 Webhook Configuration

```
Webhook Payload Format:

{
  "event_id": "evt_abc123",
  "event_type": "meeting.created",
  "created_at": "2026-06-23T10:30:45Z",
  "data": {
    "meeting_id": "meeting_789",
    "title": "Q2 Planning",
    "organization_id": "org_456",
    "created_by": "user_123",
    ...
  },
  "previous_data": {...},
  "request_id": "req_xyz"
}

Webhook Delivery:

Retry Policy:
├─ Initial attempt: Immediate
├─ Retry 1: 5 seconds
├─ Retry 2: 5 minutes
├─ Retry 3: 1 hour
├─ Retry 4: 24 hours
├─ Final: Fail after 24 hours
└─ Notification: Webhook failure alert

Delivery Requirements:
├─ Timeout: 30 seconds
├─ Status codes: 200-299 accepted
├─ HTTPS: Required
├─ TLS: 1.2 minimum
└─ Signature: HMAC-SHA256

Webhook Signature Verification:

Header: X-NANS-Signature
Format: sha256=<hex_encoded_signature>

Calculation:
├─ Secret: Webhook secret from dashboard
├─ Payload: Raw request body
├─ Algorithm: HMAC-SHA256
├─ Encoding: Hex (lowercase)
└─ Example: sha256=abcdef123456...
```

---

## 6. Rate Limiting and Throttling

### 6.1 Request Throttling

```
Throttling Strategy:

By Client Type:
├─ Web app: 100 requests/second
├─ Mobile app: 50 requests/second
├─ Backend service: 1000 requests/second
├─ Batch job: 10,000 requests/second (daytime only)
└─ Third-party: 500 requests/second

Throttling Levels:

Yellow: 80% of limit
├─ Action: Log warning
└─ Response: Normal with warning header

Orange: 90% of limit
├─ Action: Increase response delay
├─ Response: Add 100ms latency
└─ Log: Throttling event

Red: 100% of limit
├─ Action: Queue requests
├─ Response: 429 with retry header
└─ Drop: After queue fills

Burst Protection:
├─ Peak allowance: 2x sustained rate
├─ Duration: 60 seconds
├─ Enforcement: Sliding window
└─ Penalty: 1-hour cooldown after abuse
```

### 6.2 Quota Management

```
Usage Tracking:

Per-API Key Quotas:
├─ Monthly API calls: 1,000,000
├─ Data export: 1 TB per month
├─ Concurrent connections: 100
├─ Request size: 10 MB max
└─ Response size: 50 MB max

Quota Enforcement:

Approaching Limit (80%):
├─ Email notification sent
├─ Dashboard alert
└─ Upgrade prompt

At Limit (100%):
├─ Requests rejected: 402 Payment Required
├─ Response: Error with upgrade link
└─ Notification: Urgent email

Grace Period:
├─ 24 hours after limit
├─ Usage: 110% of limit allowed
└─ Requests rate-limited to 50 req/sec
```

---

## 7. Integration Patterns

### 7.1 OAuth 2.0 Integration

```
Authorization Code Flow:

1. Redirect to Authorization
   ├─ URL: https://auth.nans.org/oauth/authorize
   ├─ Parameters:
   │   ├─ client_id: your_app_id
   │   ├─ redirect_uri: https://yourapp.com/callback
   │   ├─ scope: openid email profile meetings
   │   ├─ state: random_string (CSRF protection)
   │   └─ response_type: code
   │
   └─ User authorizes access

2. Receive Authorization Code
   ├─ Redirect: https://yourapp.com/callback?code=auth_code&state=...
   ├─ Verify: state parameter matches
   ├─ Extract: code
   └─ Continue

3. Exchange Code for Token
   ├─ Endpoint: POST https://api.nans.org/oauth/token
   ├─ Request:
   │   ├─ grant_type: authorization_code
   │   ├─ code: auth_code
   │   ├─ client_id: your_app_id
   │   ├─ client_secret: your_app_secret (server-side)
   │   └─ redirect_uri: https://yourapp.com/callback
   │
   ├─ Response:
   │   ├─ access_token: jwt_token
   │   ├─ token_type: Bearer
   │   ├─ expires_in: 900 (seconds)
   │   ├─ refresh_token: refresh_token
   │   └─ scope: openid email profile meetings
   │
   └─ Store tokens securely

4. Use Access Token
   ├─ Include in all API requests
   ├─ Header: Authorization: Bearer access_token
   ├─ Lifetime: 15 minutes
   └─ Refresh when expired

5. Refresh Token When Expired
   ├─ Endpoint: POST https://api.nans.org/oauth/token
   ├─ Request:
   │   ├─ grant_type: refresh_token
   │   ├─ refresh_token: refresh_token
   │   ├─ client_id: your_app_id
   │   └─ client_secret: your_app_secret
   │
   ├─ Response: New tokens issued
   └─ Repeat step 4
```

### 7.2 Common Integration Scenarios

```
Scenario 1: Calendar Sync
├─ Use case: Sync NANS meetings to user's calendar
├─ Flow:
│   ├─ User authorizes: calendar:write scope
│   ├─ Query: GET /meetings?user_id={user_id}
│   ├─ Subscribe: Webhook on meeting.created/updated/cancelled
│   ├─ Action: Create/update/delete calendar events
│   └─ Sync: Bidirectional (optional)
│
└─ Implementation: iCal feed or native integration

Scenario 2: Data Export
├─ Use case: Export meeting data for reporting
├─ Flow:
│   ├─ Authenticate: API key or OAuth
│   ├─ Query: GET /meetings?organization_id={org_id}&date_range=...
│   ├─ Format: CSV, JSON, or PDF
│   ├─ Download: Async job with download link
│   └─ Archive: Long-term storage
│
└─ Limit: 1 TB per month

Scenario 3: Member Sync
├─ Use case: Sync NANS members to external HR system
├─ Flow:
│   ├─ Authenticate: Service account with API key
│   ├─ Query: GET /organizations/{org_id}/members?status=active
│   ├─ Compare: With external system
│   ├─ Action: Create/update/deactivate users
│   └─ Log: All changes in audit trail
│
└─ Frequency: Nightly or real-time webhooks

Scenario 4: Attendance Tracking
├─ Use case: Record attendance in mobile app
├─ Flow:
│   ├─ Authenticate: User token (OAuth or session)
│   ├─ Generate QR: GET /meetings/{meeting_id}/check-in-qr
│   ├─ Display: QR code on member device
│   ├─ Scan: Facilitator scans with tablet/phone
│   └─ Record: POST /meetings/{meeting_id}/check-in
│
└─ Implementation: WebSocket for real-time updates
```

