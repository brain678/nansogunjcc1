# app/application/interfaces/user_repository.py

"""
User Repository Interface
Defines contract for user data access
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.models.user import User


class IUserRepository(ABC):
    """User repository interface"""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        pass
    
    @abstractmethod
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """
        Find user by phone
        
        Args:
            phone: User phone
            
        Returns:
            User or None
        """
        pass
    
    @abstractmethod
    async def find_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Find users by organization
        
        Args:
            organization_id: Organization ID
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    async def find_by_role(
        self,
        role: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Find users by role
        
        Args:
            role: Role name
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    async def find_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """
        Find users by status
        
        Args:
            status: User status
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 50) -> List[User]:
        """
        Find all users
        
        Args:
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create user
        
        Args:
            user: User to create
            
        Returns:
            Created user
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update user
        
        Args:
            user: User to update
            
        Returns:
            Updated user
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Delete user (soft delete)
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Count total users
        
        Returns:
            Total count
        """
        pass
    
    @abstractmethod
    async def count_by_organization(self, organization_id: str) -> int:
        """
        Count users in organization
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Count
        """
        pass
