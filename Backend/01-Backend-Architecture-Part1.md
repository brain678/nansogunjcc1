# Production-Grade FastAPI Backend Architecture
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  
**Technology:** FastAPI, Beanie ODM, Clean Architecture, DDD

---

## 1. Folder Structure

```
nans-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py                  # MongoDB connection & initialization
│   │   ├── security.py                  # Security utilities (hashing, JWT)
│   │   ├── constants.py                 # System constants
│   │   └── settings.py                  # Environment settings
│   │
│   ├── domain/                          # Domain Layer (DDD)
│   │   ├── __init__.py
│   │   ├── models/                      # Domain models (business logic)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                  # User domain model
│   │   │   ├── organization.py          # Organization domain model
│   │   │   ├── meeting.py               # Meeting domain model
│   │   │   ├── activity.py              # Activity domain model
│   │   │   └── value_objects.py         # Value objects (Email, Phone, etc.)
│   │   │
│   │   ├── entities/                    # Entity definitions
│   │   │   ├── __init__.py
│   │   │   ├── user_entity.py
│   │   │   ├── organization_entity.py
│   │   │   └── meeting_entity.py
│   │   │
│   │   ├── events/                      # Domain events
│   │   │   ├── __init__.py
│   │   │   ├── user_events.py           # UserCreated, UserDeleted, etc.
│   │   │   ├── meeting_events.py        # MeetingScheduled, etc.
│   │   │   └── event_bus.py             # Event dispatcher
│   │   │
│   │   └── services/                    # Domain services
│   │       ├── __init__.py
│   │       ├── auth_service.py          # Authentication logic
│   │       └── permission_service.py    # Authorization/RBAC logic
│   │
│   ├── application/                     # Application Layer
│   │   ├── __init__.py
│   │   ├── dto/                         # Data Transfer Objects
│   │   │   ├── __init__.py
│   │   │   ├── request_dto.py           # Request DTOs
│   │   │   ├── response_dto.py          # Response DTOs
│   │   │   └── mapper.py                # DTO <-> Entity mapping
│   │   │
│   │   ├── use_cases/                   # Use cases/Application services
│   │   │   ├── __init__.py
│   │   │   ├── user/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_user.py
│   │   │   │   ├── get_user.py
│   │   │   │   ├── list_users.py
│   │   │   │   ├── update_user.py
│   │   │   │   └── delete_user.py
│   │   │   │
│   │   │   ├── meeting/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_meeting.py
│   │   │   │   ├── schedule_meeting.py
│   │   │   │   ├── register_attendee.py
│   │   │   │   └── record_attendance.py
│   │   │   │
│   │   │   ├── organization/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_organization.py
│   │   │   │   ├── add_member.py
│   │   │   │   └── assign_role.py
│   │   │   │
│   │   │   └── activity/
│   │   │       ├── __init__.py
│   │   │       ├── create_activity.py
│   │   │       ├── record_participation.py
│   │   │       └── calculate_engagement.py
│   │   │
│   │   ├── services/                    # Application services
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   ├── meeting_service.py
│   │   │   ├── organization_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── audit_service.py
│   │   │   └── notification_service.py
│   │   │
│   │   └── interfaces/                  # Interfaces/abstractions
│   │       ├── __init__.py
│   │       ├── repository.py            # Repository interface
│   │       ├── unit_of_work.py          # Unit of Work pattern
│   │       └── event_handler.py         # Event handler interface
│   │
│   ├── infrastructure/                  # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── persistence/                 # Persistence implementations
│   │   │   ├── __init__.py
│   │   │   ├── repository_base.py       # Base repository (Beanie)
│   │   │   ├── user_repository.py
│   │   │   ├── organization_repository.py
│   │   │   ├── meeting_repository.py
│   │   │   ├── activity_repository.py
│   │   │   ├── audit_repository.py
│   │   │   └── unit_of_work.py
│   │   │
│   │   ├── cache/                       # Caching layer (Redis)
│   │   │   ├── __init__.py
│   │   │   ├── cache_base.py
│   │   │   ├── user_cache.py
│   │   │   ├── permission_cache.py
│   │   │   └── cache_manager.py
│   │   │
│   │   ├── security/                    # Security implementations
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py           # JWT token handling
│   │   │   ├── password_hasher.py       # Argon2id password hashing
│   │   │   ├── permission_engine.py     # RBAC engine
│   │   │   └── audit_logger.py          # Audit logging
│   │   │
│   │   ├── external/                    # External services
│   │   │   ├── __init__.py
│   │   │   ├── email_service.py         # SendGrid integration
│   │   │   ├── sms_service.py           # Twilio integration
│   │   │   └── storage_service.py       # S3 integration
│   │   │
│   │   └── events/
│   │       ├── __init__.py
│   │       └── event_handler.py         # Event handler implementations
│   │
│   ├── presentation/                    # Presentation Layer (API)
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py          # Auth endpoints
│   │   │   │   │   ├── users.py         # User endpoints
│   │   │   │   │   ├── organizations.py # Org endpoints
│   │   │   │   │   ├── meetings.py      # Meeting endpoints
│   │   │   │   │   ├── activities.py    # Activity endpoints
│   │   │   │   │   └── health.py        # Health check
│   │   │   │   │
│   │   │   │   └── endpoints.py         # API router aggregator
│   │   │   │
│   │   │   └── dependencies.py          # FastAPI dependencies
│   │   │
│   │   ├── middleware/                  # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py       # JWT verification
│   │   │   ├── audit_middleware.py      # Request/response audit
│   │   │   ├── error_middleware.py      # Error handling
│   │   │   ├── cors_middleware.py       # CORS configuration
│   │   │   ├── rate_limit_middleware.py # Rate limiting
│   │   │   └── logging_middleware.py    # Request logging
│   │   │
│   │   ├── exceptions/                  # Exception handling
│   │   │   ├── __init__.py
│   │   │   ├── app_exceptions.py        # Application exceptions
│   │   │   └── exception_handlers.py    # Exception handlers
│   │   │
│   │   └── schemas/                     # Request/Response schemas
│   │       ├── __init__.py
│   │       ├── user_schemas.py
│   │       ├── organization_schemas.py
│   │       ├── meeting_schemas.py
│   │       ├── activity_schemas.py
│   │       ├── auth_schemas.py
│   │       └── error_schemas.py
│   │
│   └── common/                          # Cross-cutting concerns
│       ├── __init__.py
│       ├── logger.py                    # Logging configuration
│       ├── enums.py                     # Enumerations
│       ├── constants.py                 # Global constants
│       ├── decorators.py                # Custom decorators
│       └── utils.py                     # Utility functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── test_user_entity.py
│   │   │   ├── test_meeting_entity.py
│   │   │   └── test_permission_service.py
│   │   │
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── test_user_service.py
│   │   │   ├── test_meeting_service.py
│   │   │   └── test_auth_service.py
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── test_user_repository.py
│   │   │   ├── test_permission_engine.py
│   │   │   └── test_audit_logger.py
│   │   │
│   │   └── presentation/
│   │       ├── __init__.py
│   │       ├── test_auth_endpoints.py
│   │       ├── test_user_endpoints.py
│   │       └── test_meeting_endpoints.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_user_workflow.py
│   │   ├── test_meeting_workflow.py
│   │   └── test_auth_workflow.py
│   │
│   └── e2e/
│       ├── __init__.py
│       ├── test_user_api.py
│       ├── test_meeting_api.py
│       └── test_auth_api.py
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── scripts/
│   ├── __init__.py
│   ├── create_admin.py                  # Create admin user
│   ├── seed_data.py                     # Seed test data
│   ├── migrate_db.py                    # Database migrations
│   └── health_check.py                  # Health check script
│
├── .env.example                         # Environment template
├── .env.test                            # Test environment
├── .env.production                      # Production environment
├── requirements.txt                     # Dependencies
├── pytest.ini                           # Pytest configuration
├── pyproject.toml                       # Project configuration
└── README.md                            # Documentation
```

---

## 2. Base Models and Core Configuration

### 2.1 Configuration Management

```python
# app/config.py

from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NANS Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    API_DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_HEADERS: List[str] = ["*"]
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DATABASE: str = "nans"
    MONGODB_MIN_POOL_SIZE: int = 5
    MONGODB_MAX_POOL_SIZE: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # Security
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # MFA
    MFA_TOTP_WINDOW: int = 1
    BACKUP_CODES_COUNT: int = 10
    
    # Email
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str = "noreply@nans.org"
    
    # SMS
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "nans-documents"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Audit
    AUDIT_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.2 Core Security Module

```python
# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import secrets
from app.config import settings

class JWTHandler:
    """JWT token generation and verification"""
    
    @staticmethod
    def create_access_token(
        subject: str,
        user_id: str,
        organization_id: str,
        roles: list[str],
        permissions: list[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                hours=settings.JWT_EXPIRATION_HOURS
            )
        
        to_encode = {
            "sub": subject,
            "user_id": user_id,
            "org_id": organization_id,
            "roles": roles,
            "permissions": permissions,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(subject: str, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_EXPIRATION_DAYS
        )
        
        to_encode = {
            "sub": subject,
            "user_id": user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")

class PasswordHasher:
    """Password hashing with Argon2id"""
    
    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=2,
            memory_cost=19 * 1024,  # 19 MB
            parallelism=1,
            hash_len=32,
            salt_len=16
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password with Argon2id"""
        return self.hasher.hash(password)
    
    def verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash"""
        try:
            self.hasher.verify(hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
    
    def check_needs_rehash(self, hash: str) -> bool:
        """Check if hash needs updating"""
        return self.hasher.check_needs_rehash(hash)

class TokenGenerator:
    """Generate secure tokens"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate random secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """Generate MFA backup codes"""
        return [
            f"{secrets.randbits(16):04x}-{secrets.randbits(16):04x}"
            for _ in range(count)
        ]

password_hasher = PasswordHasher()
jwt_handler = JWTHandler()
token_generator = TokenGenerator()
```

### 2.3 Database Initialization

```python
# app/core/database.py

from beanie import init_beanie
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB database connection manager"""
    
    client: Optional[AsyncClient] = None
    db: Optional[AsyncDatabase] = None
    
    @classmethod
    async def connect(cls, db_url: str, db_name: str):
        """Initialize database connection"""
        cls.client = AsyncClient(db_url)
        cls.db = cls.client[db_name]
        
        # Import models
        from app.infrastructure.persistence.models import (
            User, Organization, OrganizationMember,
            Meeting, MeetingRegistration, MeetingMinutes,
            Activity, ActivityParticipant, EngagementScore,
            Document, DocumentVersion,
            Notification, EmailTemplate,
            AuditLog, DataAccessRequest, Role, Session
        )
        
        # Initialize Beanie
        await init_beanie(
            database=cls.db,
            models=[
                User, Organization, OrganizationMember, Role,
                Meeting, MeetingRegistration, MeetingMinutes,
                Activity, ActivityParticipant, EngagementScore,
                Document, DocumentVersion,
                Notification, EmailTemplate,
                AuditLog, DataAccessRequest, Session
            ]
        )
        
        logger.info(f"Connected to MongoDB: {db_name}")
    
    @classmethod
    async def disconnect(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")

# Global instance
db_manager = DatabaseManager()
```

---

## 3. Base Model and Common Abstractions

### 3.1 Base Entity

```python
# app/domain/entities/base_entity.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BaseEntity(BaseModel):
    """Base entity with common fields"""
    
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    version: int = 1
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
    
    def is_deleted(self) -> bool:
        """Check if entity is soft-deleted"""
        return self.deleted_at is not None
    
    def mark_as_deleted(self) -> None:
        """Mark entity as deleted"""
        self.deleted_at = datetime.utcnow()
```

### 3.2 Value Objects

```python
# app/domain/models/value_objects.py

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum

class Email(BaseModel):
    """Value object for email"""
    value: EmailStr
    verified: bool = False
    verified_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        return False

class Phone(BaseModel):
    """Value object for phone number"""
    value: str
    verified: bool = False
    
    @field_validator('value')
    @classmethod
    def validate_e164(cls, v: str) -> str:
        if not v.startswith('+'):
            raise ValueError('Phone must be in E.164 format')
        return v
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        return False

class Permission(BaseModel):
    """Value object for permission"""
    resource: str  # "users", "meetings", "organizations"
    action: str    # "read", "create", "update", "delete"
    scope: str     # "own", "organization", "all"
    
    def __str__(self) -> str:
        return f"{self.resource}:{self.action}:{self.scope}"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Permission):
            return (
                self.resource == other.resource and
                self.action == other.action and
                self.scope == other.scope
            )
        return False

class Address(BaseModel):
    """Value object for address"""
    street: str
    city: str
    state: Optional[str]
    postal_code: str
    country: str
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"
```

---

## 4. Dependency Injection Container

### 4.1 DI Container

```python
# app/infrastructure/di_container.py

from typing import Callable, Dict, Any, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register singleton instance"""
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """Register factory function"""
        self._factories[name] = factory
    
    def resolve(self, name: str) -> Any:
        """Resolve dependency"""
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._factories:
            return self._factories[name]()
        
        raise ValueError(f"Dependency '{name}' not registered")
    
    def resolve_all(self, pattern: str) -> Dict[str, Any]:
        """Resolve all dependencies matching pattern"""
        result = {}
        for key in self._singletons:
            if pattern in key:
                result[key] = self._singletons[key]
        for key in self._factories:
            if pattern in key:
                result[key] = self._factories[key]()
        return result

# Global container
container = DIContainer()

# Bootstrap container
async def bootstrap_container():
    """Initialize DI container with services"""
    from app.infrastructure.persistence.user_repository import UserRepository
    from app.infrastructure.persistence.meeting_repository import MeetingRepository
    from app.infrastructure.security.permission_engine import PermissionEngine
    from app.application.services.user_service import UserService
    from app.application.services.auth_service import AuthService
    
    # Register repositories
    container.register_singleton("user_repo", UserRepository())
    container.register_singleton("meeting_repo", MeetingRepository())
    
    # Register security services
    container.register_singleton("permission_engine", PermissionEngine())
    
    # Register application services
    container.register_singleton("user_service", UserService(
        user_repo=container.resolve("user_repo"),
        permission_engine=container.resolve("permission_engine")
    ))
    
    container.register_singleton("auth_service", AuthService(
        user_repo=container.resolve("user_repo")
    ))
```

---

## 5. Main FastAPI Application

### 5.1 Application Factory

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.core.database import db_manager
from app.infrastructure.di_container import bootstrap_container
from app.presentation.api.v1.endpoints import router as api_v1_router
from app.presentation.middleware import (
    ErrorHandlingMiddleware,
    AuditMiddleware,
    AuthMiddleware,
    LoggingMiddleware
)
from app.common.logger import setup_logging

# Setup logging
setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting up NANS Backend...")
    await db_manager.connect(
        settings.MONGODB_URL,
        settings.MONGODB_DATABASE
    )
    await bootstrap_container()
    logger.info("NANS Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NANS Backend...")
    await db_manager.disconnect()
    logger.info("NANS Backend shutdown complete")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade backend for NANS",
        docs_url=settings.API_DOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # Custom middleware (order matters - reverse)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Include routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
```

This is the foundation. Let me continue with the remaining layers...
