# app/core/security/jwt_handler.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.common.exceptions import AuthenticationError


class JWTHandler:
    """JWT token handler for access and refresh tokens"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 30
    ):
        """
        Initialize JWT handler
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default HS256)
            access_token_expire_minutes: Access token expiration (default 15 minutes)
            refresh_token_expire_days: Refresh token expiration (default 30 days)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create access token
        
        Args:
            subject: Token subject (usually user ID)
            expires_delta: Token expiration time
            additional_claims: Additional claims to include
            
        Returns:
            Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": subject,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            encoded_jwt = jwt.encode(
                payload,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise AuthenticationError(f"Token creation failed: {str(e)}")
    
    def create_refresh_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create refresh token
        
        Args:
            subject: Token subject (usually user ID)
            expires_delta: Token expiration time
            additional_claims: Additional claims to include
            
        Returns:
            Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": subject,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            encoded_jwt = jwt.encode(
                payload,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise AuthenticationError(f"Refresh token creation failed: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging)
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": False}
            )
            return payload
        except Exception:
            return None


# Global instance (will be initialized with config)
jwt_handler: Optional[JWTHandler] = None


def init_jwt_handler(secret_key: str, algorithm: str = "HS256") -> JWTHandler:
    """Initialize global JWT handler"""
    global jwt_handler
    jwt_handler = JWTHandler(secret_key, algorithm)
    return jwt_handler


def get_jwt_handler() -> JWTHandler:
    """Get global JWT handler"""
    if jwt_handler is None:
        raise RuntimeError("JWT handler not initialized")
    return jwt_handler
