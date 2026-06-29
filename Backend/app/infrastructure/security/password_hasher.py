"""
Password hashing utility using argon2
"""

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import logging

logger = logging.getLogger(__name__)


class PasswordHasher:
    """Password hasher using Argon2"""
    
    def __init__(self):
        """Initialize password hasher"""
        self.hasher = Argon2PasswordHasher()
    
    def hash(self, password: str) -> str:
        """
        Hash password using Argon2
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        try:
            return self.hasher.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise
    
    def verify(self, password: str, hash_value: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hash_value: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(hash_value, password)
            return True
        except VerifyMismatchError:
            return False
        except InvalidHash:
            logger.error("Invalid hash format")
            return False
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
