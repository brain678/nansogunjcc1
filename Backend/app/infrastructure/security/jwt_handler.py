"""
JWT token handler for generating and verifying JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """JWT token handler"""
    
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int):
        """
        Initialize JWT handler
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: Algorithm to use for signing (e.g., HS256)
            access_token_expire_minutes: Access token expiration in minutes
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def generate_access_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate access token
        
        Args:
            user_id: User ID to encode in token
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT access token
        """
        try:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            }
            if additional_claims:
                payload.update(additional_claims)
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise
    
    def generate_refresh_token(self, user_id: str, expires_days: int = 30) -> str:
        """
        Generate refresh token
        
        Args:
            user_id: User ID to encode in token
            expires_days: Refresh token expiration in days
            
        Returns:
            JWT refresh token
        """
        try:
            expire = datetime.utcnow() + timedelta(days=expires_days)
            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh"
            }
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating refresh token: {str(e)}")
            raise
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode access token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                logger.warning("Token is not an access token")
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying access token: {str(e)}")
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode refresh token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                logger.warning("Token is not a refresh token")
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid refresh token")
            return None
        except Exception as e:
            logger.error(f"Error verifying refresh token: {str(e)}")
            return None

    def generate_password_reset_token(self, user_id: str, expires_minutes: int = 15) -> str:
        """
        Generate password reset token
        """
        try:
            expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "password_reset"
            }
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            logger.error(f"Error generating password reset token: {str(e)}")
            raise

    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode password reset token
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                logger.warning("Token is not a password reset token")
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Password reset token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid password reset token")
            return None
        except Exception as e:
            logger.error(f"Error verifying password reset token: {str(e)}")
            return None
