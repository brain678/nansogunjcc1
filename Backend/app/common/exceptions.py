# app/common/exceptions.py

"""
Custom exception hierarchy for the application
"""


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation failed"""
    
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code, 400)


class AuthenticationError(AppException):
    """Authentication failed"""
    
    def __init__(self, message: str, code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, code, 401)


class UserNotFoundError(AppException):
    """User not found"""
    
    def __init__(self, message: str, code: str = "USER_NOT_FOUND"):
        super().__init__(message, code, 404)


class NotFoundError(AppException):
    """Resource not found"""
    
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, code, 404)


class ForbiddenError(AppException):
    """Access forbidden"""
    
    def __init__(self, message: str, code: str = "FORBIDDEN"):
        super().__init__(message, code, 403)


class UserLockedError(AppException):
    """User account is locked"""
    
    def __init__(self, message: str, code: str = "USER_LOCKED"):
        super().__init__(message, code, 423)


class DuplicateResourceError(AppException):
    """Resource already exists"""
    
    def __init__(self, message: str, code: str = "DUPLICATE_RESOURCE"):
        super().__init__(message, code, 409)


class EntityNotFoundError(AppException):
    """Entity not found"""
    
    def __init__(self, message: str, code: str = "ENTITY_NOT_FOUND"):
        super().__init__(message, code, 404)


class DatabaseError(AppException):
    """Database operation failed"""
    
    def __init__(self, message: str, code: str = "DATABASE_ERROR"):
        super().__init__(message, code, 500)


class ServiceError(AppException):
    """Service operation failed"""
    
    def __init__(self, message: str, code: str = "SERVICE_ERROR"):
        super().__init__(message, code, 500)
