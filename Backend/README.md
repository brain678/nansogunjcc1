# NANS Backend API - Setup & Development Guide

## Overview

The NANS Backend API is a production-grade FastAPI application implementing clean architecture with domain-driven design patterns. It provides comprehensive member management, authentication, and authorization capabilities for the National Association of Nigerian Students (NANS).

## Technology Stack

- **Framework**: FastAPI 0.104.1+
- **ORM**: Beanie 1.26.0+ (MongoDB async ODM)
- **Database**: MongoDB 5.0+
- **Authentication**: JWT (HS256) + Argon2id password hashing
- **Server**: Uvicorn 0.24.0+
- **Python**: 3.10+

## Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── common/
│   │   ├── models/
│   │   │   ├── base_entity.py          # Base entity for all domain models
│   │   │   └── value_objects.py        # Email, Phone, Address, Permission, etc.
│   │   └── exceptions.py                # Application exception hierarchy
│   ├── core/
│   │   ├── config/                     # Configuration management
│   │   ├── database/                   # Database connection & setup
│   │   └── security/
│   │       ├── password_hasher.py      # Argon2id hashing service
│   │       └── jwt_handler.py          # JWT token management
│   ├── domain/                         # Business logic layer
│   │   ├── models/
│   │   │   ├── user.py                 # User domain entity
│   │   │   └── member.py               # Member domain entity
│   │   └── services/
│   │       ├── auth_service.py         # Authentication business logic
│   │       └── member_service.py       # Member business logic
│   ├── application/                    # Application orchestration layer
│   │   ├── dtos/
│   │   │   ├── auth_dto.py            # Authentication DTOs
│   │   │   └── member_dto.py          # Member DTOs
│   │   ├── interfaces/
│   │   │   └── member_repository.py    # Repository interface
│   │   └── services/
│   │       └── member_application_service.py  # Application service
│   ├── infrastructure/                 # Data & external services layer
│   │   ├── persistence/
│   │   │   └── member_repository.py    # Repository implementation
│   │   ├── security/
│   │   │   └── permission_engine.py    # RBAC permission engine
│   │   ├── cache/                      # Caching layer
│   │   └── di_container/               # Dependency injection
│   └── presentation/                   # API layer
│       └── api/v1/
│           └── routers/
│               ├── auth/
│               │   └── routes.py       # Authentication endpoints
│               ├── members/
│               │   └── routes.py       # Member endpoints
│               ├── users/              # User management endpoints
│               └── meetings/           # Meeting endpoints
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
└── README.md                           # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip or poetry
- MongoDB 5.0+ running locally or accessible via connection string
- Git

### Step 1: Clone Repository

```bash
cd Backend
```

### Step 2: Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create `.env` file in the project root:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=nans_db

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Step 5: Run Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Architecture Overview

### Clean Architecture Layers

```
Presentation Layer (API Routers)
         ↓
Application Layer (DTOs, Services)
         ↓
Domain Layer (Entities, Services, Interfaces)
         ↓
Infrastructure Layer (Repositories, Security, Database)
```

### Key Design Patterns

1. **Repository Pattern**: Data access abstraction
2. **Dependency Injection**: Loose coupling via container
3. **Domain-Driven Design**: Rich domain models with business logic
4. **Value Objects**: Immutable objects for concepts like Email, Phone, etc.
5. **RBAC**: Role-Based Access Control with 4-role system

## Security

### Authentication Flow

1. User sends credentials (email + password) to `/api/v1/auth/login`
2. Server validates credentials and generates JWT tokens
3. Access token (15 min) sent to client, refresh token (30 days) stored securely
4. Client uses access token in `Authorization: Bearer {token}` header
5. On token expiration, client uses refresh token at `/api/v1/auth/refresh`

### Password Security

- Hashing: Argon2id with 19MB memory, 2 iterations
- Storage: Only hashes stored, never plaintext passwords
- Account Locking: 5 failed attempts → 30-minute lockout

### RBAC Roles

| Role | Permissions | Scope |
|------|-------------|-------|
| **Admin** | 22 permissions | National |
| **General Secretary** | 18 permissions | Organization |
| **Chairman** | 8 permissions | Organization |
| **Member** | 5 permissions | Own/Organization |

## API Endpoints

### Authentication (`/api/v1/auth`)

```bash
POST   /login              # Login with email/password
POST   /refresh            # Refresh access token
GET    /me                 # Get current user profile
POST   /logout             # Logout user
```

### Members (`/api/v1/members`)

```bash
POST   /register           # Register new member
GET    /{member_id}        # Get member by ID
GET    /by-membership/{num} # Get member by membership number
PUT    /{member_id}/profile # Update member profile
POST   /{member_id}/renew  # Renew membership
POST   /{member_id}/upgrade-tier  # Upgrade tier
POST   /{member_id}/suspend # Suspend member
POST   /{member_id}/activate # Activate member
GET    /?status=&type=     # List members with filters
GET    /expiring/list      # Get expiring memberships
GET    /{member_id}/activity # Get member activity
GET    /statistics/overview # Get member statistics
```

## Development Guidelines

### Code Organization

- Place business logic in **Domain Layer** services
- Use **DTOs** for API contracts (request/response)
- Implement **Repository interface** for data access
- Keep **Presentation Layer** thin (routing + validation)

### Adding New Features

1. **Create Domain Model** (if needed)
   - In `app/domain/models/`
   - Extend `BaseEntity`
   - Use Value Objects for concepts

2. **Implement Domain Service**
   - In `app/domain/services/`
   - Core business logic
   - Independent of framework

3. **Create DTOs**
   - In `app/application/dtos/`
   - Request and response contracts

4. **Implement Repository**
   - In `app/infrastructure/persistence/`
   - Implement interface from `app/application/interfaces/`

5. **Create Application Service**
   - In `app/application/services/`
   - Orchestrate domain service + repository

6. **Add API Router**
   - In `app/presentation/api/v1/routers/`
   - Define HTTP endpoints
   - Use dependency injection for services

### Testing

```bash
# Run tests (pytest)
pytest tests/

# With coverage
pytest tests/ --cov=app/

# Run specific test file
pytest tests/test_auth.py
```

## Common Tasks

### Creating a New User

```python
from app.domain.services.auth_service import AuthService

auth_service = AuthService(user_repository)
user = await auth_service.create_user(
    email="user@example.com",
    password="SecurePassword123!",
    first_name="John",
    last_name="Doe"
)
```

### Authenticating a User

```python
user, access_token, refresh_token = await auth_service.authenticate(
    email="user@example.com",
    password="SecurePassword123!"
)
```

### Registering a Member

```python
from app.domain.services.member_service import MemberService

member_service = MemberService(member_repository)
member = await member_service.register_member(
    user_id=user.id,
    email="member@example.com",
    first_name="Jane",
    last_name="Smith",
    membership_type=MembershipType.FULL
)
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `nans_db` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `30` |
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `False` |

## Troubleshooting

### MongoDB Connection Error
```
Error: Cannot connect to MongoDB
Solution: Ensure MongoDB is running and MONGODB_URL is correct
```

### JWT Token Expired
```
Error: 401 Unauthorized - Token expired
Solution: Use refresh token endpoint to get new access token
```

### Database Initialization Issues
```
Error: Beanie initialization failed
Solution: Check DATABASE_NAME matches MongoDB database name
```

## Performance Considerations

- **Connection Pooling**: MongoDB connection pool configured for 10-100 connections
- **Indexing**: Indexes on frequently queried fields (email, user_id, membership_number)
- **Caching**: Redis caching layer for permission checks and user profiles
- **Async/Await**: All I/O operations are non-blocking

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Configure CORS origins properly
- [ ] Use strong SECRET_KEY (32+ random characters)
- [ ] Enable HTTPS
- [ ] Set up MongoDB authentication
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerting
- [ ] Use production-grade server (Gunicorn + Uvicorn)
- [ ] Configure rate limiting
- [ ] Set up backup strategy

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support & Contributing

For issues, feature requests, or contributions, please follow the CONTRIBUTING.md guidelines.

## License

Copyright © 2024 National Association of Nigerian Students (NANS)
