# app/domain/services/auth_service.py

from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.domain.models.user import User, UserStatus
from app.core.security.password_hasher import password_hasher
from app.core.security.jwt_handler import get_jwt_handler
from app.common.exceptions import (
    AuthenticationError, UserNotFoundError, UserLockedError
)


class AuthService:
    """Domain service for authentication logic"""
    
    def __init__(self, user_repository):
        """
        Initialize auth service
        
        Args:
            user_repository: User repository for data access
        """
        self.user_repository = user_repository
    
    async def authenticate(
        self,
        email: str,
        password: str
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and return user + tokens
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        # Get user by email
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise UserNotFoundError(f"User {email} not found")
        
        # Check if user is locked
        if user.is_locked:
            raise UserLockedError(
                f"User account is locked until {user.locked_until}"
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError(
                f"User account is {user.status}"
            )
        
        # Verify password
        if not user.verify_password(password):
            user.increment_login_attempts()
            await self.user_repository.save(user)
            raise AuthenticationError("Invalid credentials")
        
        # Reset login attempts
        user.reset_login_attempts()
        await self.user_repository.save(user)
        
        # Generate tokens
        jwt_handler = get_jwt_handler()
        access_token = jwt_handler.create_access_token(
            subject=str(user.email),
            additional_claims={
                "user_id": str(user.id),
                "organization_id": user.primary_organization_id,
                "roles": user.roles,
                "permissions": [str(p) for p in user.permissions]
            }
        )
        
        refresh_token = jwt_handler.create_refresh_token(
            subject=str(user.email),
            additional_claims={"user_id": str(user.id)}
        )
        
        return user, access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            jwt_handler = get_jwt_handler()
            payload = jwt_handler.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("sub")
            user = await self.user_repository.get_by_id(user_id)
            
            if not user or user.status != UserStatus.ACTIVE:
                raise AuthenticationError("User not active")
            
            # Generate new access token
            access_token = jwt_handler.create_access_token(
                subject=str(user.email),
                additional_claims={
                    "user_id": str(user.id),
                    "organization_id": user.primary_organization_id,
                    "roles": user.roles,
                    "permissions": [str(p) for p in user.permissions]
                }
            )
            
            return access_token
        
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def validate_token(self, token: str) -> dict:
        """Validate and decode token"""
        jwt_handler = get_jwt_handler()
        return jwt_handler.verify_token(token)
    
    def extract_user_id(self, payload: dict) -> Optional[str]:
        """Extract user ID from token payload"""
        return payload.get("sub")
    
    def verify_mfa_requirement(self, user: User) -> bool:
        """Check if MFA is required for user"""
        return user.mfa_config.enabled and user.mfa_config.verified
