# FastAPI Backend - Complete Setup and Deployment Guide

**Version:** 1.0  
**Date:** June 2026  
**Status:** Production-Ready

---

## Complete Implementation Checklist

### Layer 1: Folder Structure ✅
- [x] Complete folder hierarchy with all 10+ layers
- [x] Separation of concerns (domain, application, infrastructure, presentation)
- [x] Clear module organization
- [x] Test directory structure with unit/integration/e2e

### Layer 2: Base Models ✅
- [x] Configuration management (environment variables, settings)
- [x] Security utilities (JWT, password hashing, token generation)
- [x] Database initialization (MongoDB with Beanie)
- [x] Base entity with common fields
- [x] Value objects (Email, Phone, Address, Permission)

### Layer 3: Authentication Module ✅
- [x] User domain model with MFA support
- [x] Domain auth service (login, refresh, validation)
- [x] Application auth service (API layer)
- [x] JWT token generation and verification
- [x] Password hashing with Argon2id
- [x] Login attempt tracking and account locking

### Layer 4: Permission Engine (RBAC) ✅
- [x] Role-based permission matrix (5 roles)
- [x] Resource-action-scope permission model
- [x] Permission engine with context evaluation
- [x] Permission caching for performance
- [x] Support for filtering by permissions

### Layer 5: Repository Layer ✅
- [x] Base repository interface (IRepository)
- [x] Beanie repository implementation
- [x] Generic CRUD operations
- [x] Specialized repositories (User, Meeting, Organization)
- [x] Custom query methods per entity
- [x] Unit of Work pattern for transactions

### Layer 6: Service Layer ✅
- [x] Domain services (business logic)
- [x] Application services (use cases)
- [x] Data transfer objects (DTOs)
- [x] DTO mapping/conversion
- [x] Service dependencies
- [x] Error handling and validation

### Layer 7: API Layer ✅
- [x] Dependency injection system
- [x] FastAPI dependencies
- [x] Current user extraction from JWT
- [x] Permission-based route guards
- [x] RESTful endpoints (users, auth, meetings)
- [x] Request/response models
- [x] OpenAPI documentation

### Layer 8: Middleware ✅
- [x] Authentication middleware
- [x] Audit logging middleware
- [x] Error handling middleware
- [x] Rate limiting middleware
- [x] Request/response logging
- [x] CORS configuration

### Layer 9: Exception Handling ✅
- [x] Custom exception hierarchy
- [x] Application exceptions
- [x] Exception handlers
- [x] Proper HTTP status codes
- [x] Error response formatting
- [x] Structured error details

### Layer 10: Unit Tests ✅
- [x] Test fixtures and factories
- [x] Domain logic tests
- [x] Repository tests
- [x] Service tests
- [x] Permission engine tests
- [x] API integration tests

---

## Quick Start Guide

### 1. Prerequisites

```bash
# Required versions
Python >= 3.10
MongoDB >= 4.4
Redis >= 6.0

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip
sudo apt-get install mongodb redis-server
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/nans/backend.git
cd backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your values
nano .env
```

### 3. Environment Configuration

```bash
# .env file

# Application
APP_NAME="NANS Backend"
ENVIRONMENT="development"
DEBUG=true

# Database
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DATABASE="nans"

# Redis
REDIS_URL="redis://localhost:6379"

# JWT
JWT_SECRET_KEY="your-secret-key-here-min-32-chars"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Email (SendGrid)
SENDGRID_API_KEY="your-sendgrid-api-key"

# SMS (Twilio)
TWILIO_ACCOUNT_SID="your-twilio-account-sid"
TWILIO_AUTH_TOKEN="your-twilio-auth-token"
TWILIO_PHONE_NUMBER="+1234567890"

# AWS S3
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_REGION="us-east-1"
AWS_S3_BUCKET="nans-documents"
```

### 4. Database Setup

```bash
# Start MongoDB
sudo systemctl start mongodb

# Create indices (optional - Beanie handles this)
mongo nans < scripts/create_indexes.js

# Seed test data (development only)
python -m app.scripts.seed_data
```

### 5. Run Application

```bash
# Development mode with auto-reload
python app/main.py

# Or using Uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### 6. Access API

```
API Documentation: http://localhost:8000/docs
Alternative Docs:  http://localhost:8000/redoc
Health Check:      http://localhost:8000/health
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/domain/test_user_entity.py -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html

# Run specific test
pytest tests/unit/domain/test_user_entity.py::test_user_password_verification -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Run with specific marker
pytest -m integration -v
```

### All Tests

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run with detailed output
pytest -v --tb=short

# Run and stop on first failure
pytest -x
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mongo
      - redis
    networks:
      - nans-network

  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - nans-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - nans-network

volumes:
  mongo_data:
  redis_data:

networks:
  nans-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker build -t nans-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e MONGODB_URL=mongodb://mongo:27017 \
  -e REDIS_URL=redis://redis:6379 \
  -e JWT_SECRET_KEY=your-secret \
  nans-backend:latest

# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## API Examples

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'

# Get current user
curl -X POST http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### User Management

```bash
# Create user
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!"
  }'

# Get user
curl -X GET http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer {token}"

# List users
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer {token}"

# Update user
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'

# Delete user
curl -X DELETE http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer {token}"
```

---

## Monitoring and Logging

### Logging Configuration

```python
# app/common/logger.py

import logging
import json
from logging.handlers import RotatingFileHandler

def setup_logging(level: str = "INFO", format: str = "json"):
    """Configure logging"""
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename="logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    if format == "json":
        # JSON formatter
        formatter = logging.Formatter(
            json.dumps({
                'timestamp': '%(asctime)s',
                'level': '%(levelname)s',
                'logger': '%(name)s',
                'message': '%(message)s'
            })
        )
    else:
        # Text formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

# Usage
from app.common.logger import setup_logging
setup_logging(level="INFO", format="json")
```

### Health Checks

```bash
# Kubernetes health check
curl http://localhost:8000/health

# Check all dependencies
curl http://localhost:8000/health/full
```

---

## Performance Tuning

### Database Optimization

```python
# Create indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ status: 1 })

# Monitor slow queries
db.setProfilingLevel(1, { slowms: 100 })

# Query optimization
db.users.find({status: "active"}).explain("executionStats")
```

### Caching Strategy

```python
# Redis caching levels
L1: App instance cache (<1 second)
L2: Redis (5-60 minutes)
L3: CDN (1 hour - 1 day)
L4: Database (persistent)

# Implement in service
from functools import wraps
from app.infrastructure.cache import redis_client

def cache_key(duration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = await redis_client.get(key)
            if result:
                return result
            result = await func(*args, **kwargs)
            await redis_client.set(key, result, duration)
            return result
        return wrapper
    return decorator
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 100 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health

# Using locust
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## Security Hardening

### HTTPS Configuration

```python
# Production settings
HTTPS_ONLY = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTPS headers
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

### Input Validation

```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserRequest(BaseModel):
    email: EmailStr  # Email validation
    password: str = Field(..., min_length=12, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### Rate Limiting

```python
# Configuration
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = {
    "unauthenticated": 100,  # per hour
    "authenticated": 1000,    # per hour
    "service_account": 100000  # per hour
}
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed
- [ ] Security scan completed (Bandit, Snyk)
- [ ] Performance tested (load tests)
- [ ] Database migrations verified
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Backups configured

### Deployment

- [ ] Database backups taken
- [ ] Blue-green deployment setup
- [ ] Health checks passing
- [ ] Logs monitored
- [ ] Error rates checked
- [ ] Performance metrics baseline

### Post-Deployment

- [ ] Monitor error rates (expect <0.1%)
- [ ] Check response times (P95 <300ms)
- [ ] Verify all features functional
- [ ] Update documentation
- [ ] Notify stakeholders

---

## Architecture Decision Records (ADRs)

### ADR-1: Use FastAPI + Beanie

**Decision:** Use FastAPI with Beanie ODM for MongoDB

**Rationale:**
- FastAPI: Modern async framework, automatic OpenAPI docs
- Beanie: Pydantic integration, type-safe queries, async support

**Consequences:**
- Requires Python 3.7+
- Learning curve for async programming
- Must manage MongoDB connection pooling

### ADR-2: Clean Architecture + DDD

**Decision:** Implement Clean Architecture with Domain-Driven Design

**Rationale:**
- Separates concerns into independent layers
- Business logic in domain layer
- Easier to test and maintain
- Dependency inversion principle

**Consequences:**
- More files and directories
- Higher initial development cost
- Better long-term maintainability

### ADR-3: Role-Based Access Control

**Decision:** Implement RBAC with resource-action-scope model

**Rationale:**
- Flexible permission system
- Easy to extend roles
- Audit trail support
- Performance with caching

**Consequences:**
- Permission matrix must be maintained
- More complex queries
- Need migration path for existing users

---

## Troubleshooting

### Common Issues

**Issue: JWT token invalid**
```
Solution: Check JWT_SECRET_KEY matches between services
         Verify token expiration time
         Check token format (Bearer prefix)
```

**Issue: Database connection timeout**
```
Solution: Check MongoDB is running
         Verify connection string
         Check network connectivity
         Increase connection timeout
```

**Issue: Permission denied errors**
```
Solution: Check user roles are assigned
         Verify role permissions configured
         Check permission cache invalidation
         Review audit logs for permission changes
```

**Issue: Slow query performance**
```
Solution: Check indexes are created
         Review query explain plan
         Implement caching layer
         Consider query optimization
```

---

## Support and Maintenance

### Bug Reporting

```
GitHub Issues: https://github.com/nans/backend/issues
- Include error message
- Include stack trace
- Include reproduction steps
- Include environment details
```

### Feature Requests

```
GitHub Discussions: https://github.com/nans/backend/discussions
- Describe use case
- Include acceptance criteria
- Link to related issues
```

### Documentation

- [API Documentation](http://localhost:8000/docs)
- [Architecture Guide](../Architecture/)
- [Database Schema](../Database/)
- [Setup Guide](./README.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | June 2026 | Initial release - Full backend implementation |

