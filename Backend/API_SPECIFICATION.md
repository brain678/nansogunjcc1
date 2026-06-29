# NANS Backend API Specification

## Table of Contents

1. [Authentication API](#authentication-api)
2. [Members API](#members-api)
3. [Error Handling](#error-handling)
4. [Status Codes](#status-codes)
5. [Examples](#examples)

---

## Authentication API

Base URL: `/api/v1/auth`

### 1. Login

**Endpoint**: `POST /login`

**Description**: Authenticate user with email and password, returns access and refresh tokens

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+234801234567",
    "roles": ["member", "general_secretary"],
    "mfa_enabled": true,
    "status": "active",
    "last_login_at": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T08:00:00Z"
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials or account locked
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation error

---

### 2. Refresh Token

**Endpoint**: `POST /refresh`

**Description**: Get a new access token using a valid refresh token

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

---

### 3. Get Current User

**Endpoint**: `GET /me`

**Description**: Get profile of currently authenticated user

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+234801234567",
  "roles": ["member"],
  "mfa_enabled": true,
  "status": "active",
  "last_login_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T08:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

---

### 4. Logout

**Endpoint**: `POST /logout`

**Description**: Logout user and invalidate tokens

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## Members API

Base URL: `/api/v1/members`

### 1. Register Member

**Endpoint**: `POST /register`

**Description**: Register a new member in the system

**Request Body**:
```json
{
  "email": "member@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+234802345678",
  "membership_type": "FULL",
  "membership_tier": "STANDARD",
  "expiry_months": 12
}
```

**Response** (201 Created):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "email": "member@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "membership_number": "MEM-2024-A1B2C3D4",
  "membership_type": "FULL",
  "membership_tier": "STANDARD",
  "status": "ACTIVE",
  "joined_date": "2024-01-15T10:30:00Z",
  "membership_expiry_date": "2025-01-15T10:30:00Z",
  "is_membership_expired": false,
  "days_until_expiry": 365,
  "bio": null,
  "profile_photo_url": null,
  "organization": null,
  "position": null,
  "meetings_attended": 0,
  "activities_participated": 0,
  "documents_contributed": 0,
  "total_contribution_hours": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 2. Get Member by ID

**Endpoint**: `GET /{member_id}`

**Description**: Retrieve member details by member ID

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "email": "member@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "membership_number": "MEM-2024-A1B2C3D4",
  "membership_type": "FULL",
  "membership_tier": "STANDARD",
  "status": "ACTIVE",
  "joined_date": "2024-01-15T10:30:00Z",
  "membership_expiry_date": "2025-01-15T10:30:00Z",
  "is_membership_expired": false,
  "days_until_expiry": 365,
  "bio": "Student member",
  "profile_photo_url": "https://example.com/photo.jpg",
  "organization": "Lagos Chapter",
  "position": "Secretary",
  "meetings_attended": 5,
  "activities_participated": 3,
  "documents_contributed": 2,
  "total_contribution_hours": 12.5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. Get Member by Membership Number

**Endpoint**: `GET /by-membership/{membership_number}`

**Description**: Retrieve member details by membership number

**Path Parameters**:
- `membership_number` (string): Member's membership number (e.g., "MEM-2024-A1B2C3D4")

**Response** (200 OK): Same as Get Member by ID

---

### 4. Update Member Profile

**Endpoint**: `PUT /{member_id}/profile`

**Description**: Update member's profile information

**Request Body**:
```json
{
  "bio": "Updated bio",
  "profile_photo_url": "https://example.com/new-photo.jpg",
  "organization": "Abuja Chapter",
  "position": "President",
  "department": "Student Affairs",
  "newsletter_subscription": true,
  "event_notifications": true,
  "communication_language": "en"
}
```

**Response** (200 OK): Updated member object

---

### 5. Renew Membership

**Endpoint**: `POST /{member_id}/renew`

**Description**: Renew member's membership for additional months

**Request Body**:
```json
{
  "months": 12
}
```

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "membership_expiry_date": "2026-01-15T10:30:00Z",
  "is_membership_expired": false,
  "days_until_expiry": 730,
  ...
}
```

---

### 6. Upgrade Membership Tier

**Endpoint**: `POST /{member_id}/upgrade-tier`

**Description**: Upgrade member's membership tier

**Request Body**:
```json
{
  "new_tier": "PREMIUM"
}
```

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "membership_tier": "PREMIUM",
  ...
}
```

---

### 7. Suspend Member

**Endpoint**: `POST /{member_id}/suspend`

**Description**: Suspend a member's account

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "status": "SUSPENDED",
  ...
}
```

---

### 8. Activate Member

**Endpoint**: `POST /{member_id}/activate`

**Description**: Activate a suspended member's account

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439012",
  "status": "ACTIVE",
  ...
}
```

---

### 9. List Members

**Endpoint**: `GET /`

**Description**: Get paginated list of members with optional filters

**Query Parameters**:
- `status` (string, optional): Filter by membership status (ACTIVE, INACTIVE, SUSPENDED, RESIGNED)
- `membership_type` (string, optional): Filter by type (FULL, ASSOCIATE, STUDENT, HONORARY)
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 10, max: 100): Number of records to return

**Example**: `GET /?status=ACTIVE&membership_type=FULL&skip=0&limit=10`

**Response** (200 OK):
```json
{
  "total": 150,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": "507f1f77bcf86cd799439012",
      "email": "member1@example.com",
      ...
    },
    {
      "id": "507f1f77bcf86cd799439013",
      "email": "member2@example.com",
      ...
    }
  ]
}
```

---

### 10. Get Expiring Memberships

**Endpoint**: `GET /expiring/list`

**Description**: Get list of members whose memberships are expiring soon

**Query Parameters**:
- `days` (integer, default: 30, range: 1-365): Look ahead period in days

**Response** (200 OK):
```json
[
  {
    "member_id": "507f1f77bcf86cd799439012",
    "email": "member@example.com",
    "full_name": "Jane Smith",
    "membership_number": "MEM-2024-A1B2C3D4",
    "expiry_date": "2024-02-15T10:30:00Z",
    "days_until_expiry": 31
  },
  {
    "member_id": "507f1f77bcf86cd799439013",
    "email": "member2@example.com",
    "full_name": "John Doe",
    "membership_number": "MEM-2024-X9Y8Z7W6",
    "expiry_date": "2024-02-20T10:30:00Z",
    "days_until_expiry": 36
  }
]
```

---

### 11. Get Member Activity

**Endpoint**: `GET /{member_id}/activity`

**Description**: Get member's activity statistics and contribution details

**Response** (200 OK):
```json
{
  "member_id": "507f1f77bcf86cd799439012",
  "meetings_attended": 5,
  "activities_participated": 3,
  "documents_contributed": 2,
  "total_contribution_hours": 12.5,
  "last_active_at": "2024-01-15T15:45:00Z"
}
```

---

### 12. Get Member Statistics

**Endpoint**: `GET /statistics/overview`

**Description**: Get overall member statistics and analytics

**Response** (200 OK):
```json
{
  "total_members": 500,
  "active_members": 450,
  "inactive_members": 30,
  "suspended_members": 20,
  "members_by_type": {
    "FULL": 300,
    "ASSOCIATE": 150,
    "STUDENT": 40,
    "HONORARY": 10
  },
  "members_by_tier": {
    "STANDARD": 400,
    "PREMIUM": 80,
    "LIFETIME": 20
  },
  "total_contribution_hours": 5250.5,
  "average_meetings_attended": 8.5
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent JSON format:

```json
{
  "error": {
    "message": "Descriptive error message",
    "code": "ERROR_CODE",
    "status_code": 400
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `FORBIDDEN_ERROR` | Insufficient permissions |
| `USER_LOCKED_ERROR` | Account locked due to failed login attempts |
| `USER_NOT_FOUND_ERROR` | User not found |
| `ENTITY_NOT_FOUND_ERROR` | Resource not found |
| `DUPLICATE_RESOURCE_ERROR` | Resource already exists |
| `DATABASE_ERROR` | Database operation failed |
| `SERVICE_ERROR` | Service operation failed |

---

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | OK - Request successful |
| `201` | Created - Resource created successfully |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Authentication required/failed |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource not found |
| `409` | Conflict - Resource already exists |
| `422` | Unprocessable Entity - Validation error |
| `423` | Locked - Account locked (too many login attempts) |
| `500` | Internal Server Error - Server error |

---

## Examples

### Complete Login Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Response includes access_token and refresh_token

# 2. Use access token to get user profile
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# 3. When token expires, refresh it
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'

# 4. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

### Member Management Flow

```bash
# 1. Register new member
curl -X POST http://localhost:8000/api/v1/members/register \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "member@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+234802345678",
    "membership_type": "FULL",
    "membership_tier": "STANDARD",
    "expiry_months": 12
  }'

# 2. Get member details
curl -X GET http://localhost:8000/api/v1/members/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer <access_token>"

# 3. Update member profile
curl -X PUT http://localhost:8000/api/v1/members/507f1f77bcf86cd799439012/profile \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Updated bio",
    "organization": "Lagos Chapter",
    "position": "Secretary"
  }'

# 4. Renew membership
curl -X POST http://localhost:8000/api/v1/members/507f1f77bcf86cd799439012/renew \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "months": 12
  }'

# 5. List all active members
curl -X GET "http://localhost:8000/api/v1/members/?status=ACTIVE&skip=0&limit=20" \
  -H "Authorization: Bearer <access_token>"

# 6. Get members with expiring memberships
curl -X GET "http://localhost:8000/api/v1/members/expiring/list?days=30" \
  -H "Authorization: Bearer <access_token>"
```

---

## Rate Limiting

By default, the API enforces rate limiting:

- **Standard**: 100 requests per minute per IP
- **Authenticated**: 500 requests per minute per user

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705329000
```

---

## Pagination

For list endpoints, pagination is supported with:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 10, max: 100)

---

Last Updated: January 2024
