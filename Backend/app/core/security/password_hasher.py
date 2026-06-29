# app/core/security/password_hasher.py

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from app.common.exceptions import AuthenticationError


class PasswordHasherService:
    """Password hashing service using Argon2id"""
    
    def __init__(self):
        # Argon2id configuration for production
        # Memory: 19 MB, Time: 2 iterations, Parallelism: 1
        self.hasher = PasswordHasher(
            time_cost=2,           # iterations
            memory_cost=19456,     # 19 MB
            parallelism=1,
            hash_len=32,
            salt_len=16,
            encoding='utf-8'
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using Argon2id
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            return self.hasher.hash(password)
        except Exception as e:
            raise AuthenticationError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, password: str, hash_value: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password to verify
            hash_value: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(hash_value, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
        except Exception as e:
            raise AuthenticationError(f"Password verification failed: {str(e)}")
    
    def needs_rehash(self, hash_value: str) -> bool:
        """
        Check if hash needs to be rehashed (e.g., after security update)
        
        Args:
            hash_value: Hashed password
            
        Returns:
            True if needs rehashing
        """
        try:
            return self.hasher.check_needs_rehash(hash_value)
        except Exception:
            return True


# Global instance
password_hasher = PasswordHasherService()
