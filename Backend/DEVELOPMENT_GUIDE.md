# Development Guide - NANS Backend API

## Overview

This guide provides comprehensive information for developers working on the NANS Backend API. It covers coding standards, architecture patterns, and best practices.

## Architecture Overview

### Clean Architecture Layers

The application is organized into four distinct layers, each with specific responsibilities:

```
┌─────────────────────────────────────────┐
│ Presentation Layer (API, Views)         │  Controllers, HTTP handlers
├─────────────────────────────────────────┤
│ Application Layer (Use Cases, Services) │  DTOs, Application Services
├─────────────────────────────────────────┤
│ Domain Layer (Business Logic)           │  Entities, Domain Services
├─────────────────────────────────────────┤
│ Infrastructure Layer (Data, External)   │  Repositories, DB, APIs
└─────────────────────────────────────────┘
```

### Communication Between Layers

```
Presentation → Application → Domain → Infrastructure
(inbound)     (outbound)
```

#### Layer Responsibilities

**Presentation Layer** (`app/presentation/`)
- HTTP request/response handling
- Input validation
- Route definitions
- Dependency injection
- Should NOT contain business logic

**Application Layer** (`app/application/`)
- Data Transfer Objects (DTOs)
- Application services (use case orchestration)
- Transaction management
- Maps between domain models and DTOs
- Should NOT contain core business logic

**Domain Layer** (`app/domain/`)
- Entities (domain models)
- Domain services (business logic)
- Value objects
- Domain exceptions
- No framework dependencies
- Most critical and stable layer

**Infrastructure Layer** (`app/infrastructure/`)
- Database repositories
- External service integrations
- Security implementations
- Caching mechanisms
- File storage
- Framework-specific implementations

## Design Patterns

### 1. Repository Pattern

Abstracts data access, allowing business logic to remain independent of data source.

**Interface Definition** (in `app/application/interfaces/`):
```python
class IMemberRepository(ABC):
    @abstractmethod
    async def get_by_id(self, member_id: str) -> Optional[Member]:
        pass
    
    @abstractmethod
    async def find_all(self, skip: int, limit: int) -> List[Member]:
        pass
```

**Implementation** (in `app/infrastructure/persistence/`):
```python
class MemberRepository(IMemberRepository):
    async def get_by_id(self, member_id: str) -> Optional[Member]:
        member = await Member.get(member_id)
        if member and not member.is_deleted():
            return member
        return None
```

**Usage** (in Domain/Application Services):
```python
class MemberService:
    def __init__(self, member_repository: IMemberRepository):
        self.member_repository = member_repository
    
    async def get_member(self, member_id: str) -> Member:
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        return member
```

### 2. Dependency Injection

Promotes loose coupling and testability.

**Good Example**:
```python
class MemberApplicationService:
    def __init__(self, member_service: MemberService):
        self.member_service = member_service  # Injected dependency
```

**Bad Example** (Tight Coupling):
```python
class MemberApplicationService:
    def __init__(self):
        self.member_service = MemberService()  # Hard-coded dependency
```

### 3. Value Objects

Immutable objects representing domain concepts.

**Example**:
```python
class Email(BaseModel):
    """Immutable email value object"""
    value: EmailStr
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: 'Email') -> bool:
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
```

### 4. Domain-Driven Design

Entities, Domain Services, and Value Objects encapsulate business logic.

**Domain Entity**:
```python
class Member(BaseEntity):
    """Rich domain entity with business logic"""
    
    user_id: str
    membership_number: str
    membership_type: MembershipType
    status: MembershipStatus
    
    def renew_membership(self, months: int) -> None:
        """Business logic for membership renewal"""
        if self.is_membership_expired:
            raise ValidationError("Cannot renew expired membership")
        
        self.membership_expiry_date = datetime.utcnow() + timedelta(days=months*30)
        self.status = MembershipStatus.ACTIVE
```

## Code Organization Best Practices

### 1. File Structure

- Keep files focused and manageable (< 500 lines)
- Group related functionality
- Use clear, descriptive names

```
app/domain/
├── models/
│   ├── user.py          # ~400 lines
│   ├── member.py        # ~300 lines
│   └── __init__.py
└── services/
    ├── auth_service.py  # ~200 lines
    └── member_service.py # ~300 lines
```

### 2. Naming Conventions

**Classes**:
```python
class User              # Entities
class UserRepository   # Repositories
class UserService      # Domain services
class UserApplicationService  # Application services
```

**Functions/Methods**:
```python
async def get_user_by_id()     # Get single item
async def find_users()         # Find with filters
async def create_user()        # Create new
async def update_user()        # Update existing
async def delete_user()        # Delete
async def is_user_active()     # Boolean query
```

**Constants**:
```python
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_PAGE_SIZE = 20
ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
```

### 3. Import Organization

```python
# 1. Standard library
from typing import Optional, List
from datetime import datetime

# 2. Third-party
from pydantic import BaseModel, EmailStr

# 3. Local imports
from app.common.exceptions import ValidationError
from app.domain.models import Member
```

## Testing Best Practices

### Unit Tests

Test individual units in isolation:

```python
@pytest.mark.asyncio
async def test_member_service_renew_membership():
    """Test membership renewal business logic"""
    # Arrange
    member_repo = MagicMock(spec=IMemberRepository)
    service = MemberService(member_repo)
    member = Member(...)
    member_repo.get_by_id.return_value = member
    
    # Act
    result = await service.renew_membership(member_id="123", months=12)
    
    # Assert
    assert result.status == MembershipStatus.ACTIVE
    member_repo.save.assert_called_once()
```

### Integration Tests

Test interactions between components:

```python
@pytest.mark.asyncio
async def test_member_registration_flow(db):
    """Test complete member registration"""
    # Create repository with real DB
    repo = MemberRepository()
    service = MemberService(repo)
    
    # Register member
    member = await service.register_member(...)
    
    # Verify in database
    retrieved = await repo.get_by_id(member.id)
    assert retrieved.membership_number == member.membership_number
```

### Test Naming

```python
def test_<unit>_<scenario>_<expected_result>():
    pass

# Examples:
def test_member_service_renew_membership_extends_expiry_date():
    pass

def test_auth_service_authenticate_locks_account_after_5_attempts():
    pass

def test_password_hasher_verify_password_returns_false_for_wrong_password():
    pass
```

## Error Handling

### Exception Hierarchy

```python
AppException (base)
├── ValidationError (400)
├── AuthenticationError (401)
├── ForbiddenError (403)
├── UserLockedError (423)
├── EntityNotFoundError (404)
├── DuplicateResourceError (409)
├── DatabaseError (500)
└── ServiceError (500)
```

### Usage Examples

```python
# Validation errors
if not email.is_valid():
    raise ValidationError("Invalid email format")

# Authentication errors
if not password_valid:
    raise AuthenticationError("Invalid credentials")

# Authorization errors
if not user_has_permission:
    raise ForbiddenError("Insufficient permissions")

# Resource not found
member = await repo.get_by_id(member_id)
if not member:
    raise EntityNotFoundError(f"Member not found: {member_id}")

# Duplicate resources
existing = await repo.find_by_email(email)
if existing:
    raise DuplicateResourceError(f"Member already exists: {email}")
```

## Database Best Practices

### MongoDB with Beanie

**Index Definition**:
```python
class Member(BaseEntity):
    user_id: str
    membership_number: str
    email: Email
    
    class Settings:
        indexes = [
            [("user_id", 1)],
            [("membership_number", 1)],
            [("email.value", 1)],
            [("created_at", -1)],
            [("deleted_at", 1)],
        ]
```

**Query Best Practices**:
```python
# Good: Use indexed fields
members = await Member.find({"user_id": user_id}).to_list()

# Good: Use projection to limit fields
members = await Member.find(
    {"status": "ACTIVE"}
).project(["id", "email", "membership_number"]).to_list()

# Avoid: Complex calculations in queries
# Instead, do post-processing in application

# Avoid: N+1 queries
# Use batch operations when possible
```

### Soft Deletes

All domain entities support soft deletes:

```python
# Delete
member.soft_delete()
await member_repo.save(member)

# Query excludes soft-deleted items by default
active_members = await repo.find_all()  # Automatically filters deleted_at=None

# Restore
member.restore()
await member_repo.save(member)
```

## Security Best Practices

### Password Handling

```python
# Good: Use password_hasher service
password_hash = await password_hasher.hash_password(password)
is_valid = await password_hasher.verify_password(password, password_hash)

# Bad: Store plaintext passwords
user.password = request.password  # NEVER DO THIS
```

### JWT Tokens

```python
# Create tokens with appropriate expiry
access_token = jwt_handler.create_access_token(
    subject=user.id,
    expires_delta=timedelta(minutes=15)
)

refresh_token = jwt_handler.create_refresh_token(
    subject=user.id,
    expires_delta=timedelta(days=30)
)

# Verify tokens
try:
    payload = jwt_handler.verify_token(token)
except AuthenticationError:
    raise ForbiddenError("Invalid or expired token")
```

### Account Locking

```python
# Track failed attempts
user.increment_login_attempts()

# Lock on max attempts
if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
    raise UserLockedError("Account locked due to failed login attempts")

# Reset on success
user.reset_login_attempts()
```

## Async/Await Best Practices

### Always Use Async for I/O

```python
# Good: Async I/O operations
async def get_member(self, member_id: str) -> Member:
    return await self.member_repository.get_by_id(member_id)

# Bad: Sync I/O in async function
def get_member(self, member_id: str) -> Member:
    return self.member_repository.get_by_id(member_id)  # Will block!
```

### Concurrent Operations

```python
# Good: Run operations concurrently
members = await asyncio.gather(
    repo.get_by_id("id1"),
    repo.get_by_id("id2"),
    repo.get_by_id("id3")
)

# Bad: Sequential operations
member1 = await repo.get_by_id("id1")
member2 = await repo.get_by_id("id2")
member3 = await repo.get_by_id("id3")
```

## Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Info level for important events
logger.info(f"User {user_id} logged in successfully")

# Warning level for recoverable issues
logger.warning(f"Failed login attempt for user {email}")

# Error level for recoverable errors
logger.error(f"Database connection failed", exc_info=True)

# Debug level for detailed information
logger.debug(f"Processing member registration: {member_data}")
```

## Documentation

### Docstrings

```python
async def register_member(
    self,
    user_id: str,
    email: str,
    first_name: str,
    last_name: str,
    membership_type: MembershipType = MembershipType.FULL
) -> Member:
    """
    Register a new member in the system.
    
    Args:
        user_id: ID of the associated user
        email: Member's email address
        first_name: Member's first name
        last_name: Member's last name
        membership_type: Type of membership (default: FULL)
    
    Returns:
        Newly created Member entity
    
    Raises:
        DuplicateResourceError: If member already exists
        ValidationError: If input validation fails
    """
    pass
```

### Type Hints

```python
# Good: Explicit type hints
async def get_member(self, member_id: str) -> Optional[Member]:
    pass

async def list_members(self, skip: int = 0, limit: int = 10) -> List[Member]:
    pass

# Avoid: Unclear types
def process_data(data):  # What is data?
    pass
```

## Performance Optimization

### Database Query Optimization

```python
# Good: Single query with projection
members = await Member.find(
    {"status": "ACTIVE"}
).project(["id", "email", "status"]).skip(0).limit(10).to_list()

# Avoid: Load all data then filter
all_members = await Member.find({}).to_list()
active = [m for m in all_members if m.status == "ACTIVE"][:10]
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_permission_matrix() -> dict:
    """Cache permission matrix for performance"""
    return PermissionMatrix.PERMISSIONS
```

### Batch Operations

```python
# Good: Batch multiple operations
results = await asyncio.gather(
    *[repo.get_by_id(id) for id in member_ids]
)

# Avoid: Sequential operations in loop
for member_id in member_ids:
    member = await repo.get_by_id(member_id)
    # Process member
```

## Debugging Tips

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

### Use IDE Debugger

Set breakpoints in PyCharm or VS Code and use the debugger to inspect variables.

### Print Debugging

```python
import pprint

# For complex objects
pprint.pprint(member.dict())

# For debugging async flow
logger.debug(f"Before database call: {datetime.utcnow()}")
result = await repo.get_by_id(id)
logger.debug(f"After database call: {datetime.utcnow()}")
```

## Contributing Checklist

Before committing code:

- [ ] Code follows naming conventions
- [ ] Type hints are present
- [ ] Docstrings are complete
- [ ] Error handling is appropriate
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] No hardcoded values (use constants or config)
- [ ] Logging is appropriate
- [ ] No unused imports or variables
- [ ] Code is formatted with Black
- [ ] No breaking changes to public APIs
- [ ] Documentation is updated

## Common Pitfalls

### 1. Mixing Concerns Across Layers

```python
# Bad: API logic in domain service
class MemberService:
    async def register_member(self, request: MemberRegisterRequest):
        # Validation belongs in application layer
        if not request.email:
            raise ValidationError("Email required")

# Good: Separation of concerns
class MemberApplicationService:
    async def register_member(self, request: MemberRegisterRequest):
        # Validation in application layer
        if not request.email:
            raise ValidationError("Email required")
        
        # Domain service called with validated data
        member = await self.member_service.register_member(
            user_id=user.id,
            email=request.email
        )
```

### 2. Blocking Operations in Async Functions

```python
# Bad: Blocking operation in async function
async def get_members(self) -> List[Member]:
    time.sleep(1)  # This blocks the event loop!
    return await repo.find_all()

# Good: Use async sleep if needed
async def get_members(self) -> List[Member]:
    await asyncio.sleep(1)  # Non-blocking
    return await repo.find_all()
```

### 3. Storing Secrets in Code

```python
# Bad: Secret in source code
JWT_SECRET = "my-secret-key"

# Good: Use environment variables
JWT_SECRET = os.getenv("SECRET_KEY")
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Beanie ODM Documentation](https://beanie-odm.readthedocs.io/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Python Best Practices](https://pep8.org/)

---

Last Updated: January 2024
