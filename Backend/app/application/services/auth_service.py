"""
Application Authentication Service - Orchestrates authentication use cases
Coordinates between domain service, repositories, and DTOs
"""

import logging
from typing import Optional, Tuple
from datetime import datetime
from app.application.dtos.auth_dto import (
    LoginRequest, RegisterRequest, RefreshTokenRequest,
    ChangePasswordRequest, AuthSuccessResponse, UserResponse,
    TokenResponse, AccessTokenResponse
)
from app.infrastructure.persistence.member_repository import MemberRepository

logger = logging.getLogger(__name__)


class AuthServiceImpl:
    """Simplified Authentication Service Implementation"""
    
    def __init__(self, password_hasher, jwt_handler, user_repository, member_repository: Optional[MemberRepository] = None):
        """
        Initialize auth service
        
        Args:
            password_hasher: Password hashing utility
            jwt_handler: JWT token handler
            user_repository: User repository for data access
            member_repository: Optional member repository for membership state
        """
        self.password_hasher = password_hasher
        self.jwt_handler = jwt_handler
        self.user_repository = user_repository
        self.member_repository = member_repository or MemberRepository()
    
    async def authenticate(
        self, 
        email: str, 
        password: str
    ) -> Optional[Tuple]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (user, access_token, refresh_token, membership_status, membership_number)
            or None if auth fails
        """
        try:
            # Find user by email
            user = await self.user_repository.find_by_email(email)
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return None
            
            # Verify password
            is_valid = self.password_hasher.verify(password, user.password_hash)
            
            if not is_valid:
                logger.warning(f"Failed login attempt for user: {email}")
                return None

            # Only active user accounts may authenticate
            if user.status != user.status.__class__.ACTIVE:
                logger.warning(f"Authentication blocked for user account status: {user.status}")
                return None

            # Fetch membership status if available
            membership_status = None
            membership_number = None
            try:
                member = await self.member_repository.find_by_user_id(str(user.id))
                if member:
                    membership_status = member.status.value
                    membership_number = member.membership_number
            except Exception:
                membership_status = None
                membership_number = None
            
            # Generate tokens
            access_token = self.jwt_handler.generate_access_token(
                user_id=str(user.id),
                additional_claims={
                    "membership_status": membership_status,
                    "membership_number": membership_number
                }
            )
            refresh_token = self.jwt_handler.generate_refresh_token(user_id=str(user.id))
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            await self.user_repository.update(user)
            
            logger.info(f"User authenticated successfully: {email}")
            return user, access_token, refresh_token, membership_status, membership_number
            
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """
        Generate a password reset token for the given email
        """
        try:
            user = await self.user_repository.find_by_email(email)
            if not user:
                return None
            token = self.jwt_handler.generate_password_reset_token(
                user_id=str(user.id)
            )
            logger.info(f"Password reset token generated for user: {email}")
            return token
        except Exception as e:
            logger.error(f"Error generating password reset token: {str(e)}")
            return None

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using a password reset token
        """
        try:
            payload = self.jwt_handler.verify_password_reset_token(token)
            if not payload:
                return False
            user_id = payload.get("sub")
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False
            user.password_hash = self.password_hasher.hash(new_password)
            user.password_changed_at = datetime.utcnow()
            user.login_attempts = 0
            user.locked_until = None
            await self.user_repository.update(user)
            logger.info(f"Password reset successfully for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return False
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change password for the current user
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False
            if not self.password_hasher.verify(current_password, user.password_hash):
                return False
            user.password_hash = self.password_hasher.hash(new_password)
            user.password_changed_at = datetime.utcnow()
            user.login_attempts = 0
            user.locked_until = None
            await self.user_repository.update(user)
            logger.info(f"Password changed successfully for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New access token or None if refresh fails
        """
        try:
            # Verify and decode refresh token
            payload = self.jwt_handler.verify_refresh_token(refresh_token)
            
            if not payload:
                return None
            
            user_id = payload.get("sub")
            
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return None

            # Fetch membership info for refreshed token
            membership_status = None
            membership_number = None
            try:
                member = await self.member_repository.find_by_user_id(str(user.id))
                if member:
                    membership_status = member.status.value
                    membership_number = member.membership_number
            except Exception:
                membership_status = None
                membership_number = None
            
            # Generate new access token
            new_access_token = self.jwt_handler.generate_access_token(
                user_id=user_id,
                additional_claims={
                    "membership_status": membership_status,
                    "membership_number": membership_number
                }
            )
            
            logger.info(f"Access token refreshed for user: {user_id}")
            return new_access_token
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None
    
    async def get_current_user(self, token: str):
        """
        Get current user from token
        
        Args:
            token: Access token
            
        Returns:
            User object or None
        """
        try:
            # Verify and decode token
            payload = self.jwt_handler.verify_access_token(token)
            
            if not payload:
                return None
            
            user_id = payload.get("sub")
            
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None


class AuthMapper:
    """Map between domain models and DTOs"""
    
    @staticmethod
    def user_to_response(user) -> UserResponse:
        """Map User domain model to UserResponse DTO"""
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            roles=user.roles,
            organization_id=user.organization_id,
            last_login_at=user.last_login_at,
            created_at=user.created_at
        )
    
    @staticmethod
    def tokens_to_response(tokens) -> TokenResponse:
        """Map TokenPair to TokenResponse DTO"""
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in
        )


# ApplicationAuthService kept for backward compatibility
ApplicationAuthService = AuthServiceImpl

