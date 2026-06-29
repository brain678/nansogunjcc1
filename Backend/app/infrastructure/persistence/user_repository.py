# app/infrastructure/persistence/user_repository.py

"""
User Repository Implementation
Beanie ODM implementation for user persistence
"""

import re
from typing import Optional, List
from datetime import datetime
from app.domain.models.user import User
from app.application.interfaces.user_repository import IUserRepository
from app.common.exceptions import EntityNotFoundError


class UserRepository(IUserRepository):
    """User repository - MongoDB implementation"""
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        try:
            user = await User.get(user_id)
            return user if not user.deleted_at else None
        except Exception:
            return None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        normalized_email = email.strip().lower()
        try:
            user = await User.find_one(
                {
                    "email.value": {
                        "$regex": f"^{re.escape(normalized_email)}$",
                        "$options": "i"
                    },
                    "deleted_at": None
                }
            )
            return user
        except Exception:
            return None
    
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """
        Find user by phone
        
        Args:
            phone: User phone
            
        Returns:
            User or None
        """
        try:
            user = await User.find_one(
                {
                    "phone.value": phone,
                    "deleted_at": None
                }
            )
            return user
        except Exception:
            return None
    
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
        try:
            users = await User.find(
                {
                    "organizations": organization_id,
                    "deleted_at": None
                }
            ).skip(skip).limit(limit).to_list()
            return users or []
        except Exception:
            return []
    
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
        try:
            users = await User.find(
                {
                    "roles": role,
                    "deleted_at": None
                }
            ).skip(skip).limit(limit).to_list()
            return users or []
        except Exception:
            return []
    
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
        try:
            users = await User.find(
                {
                    "status": status,
                    "deleted_at": None
                }
            ).skip(skip).limit(limit).to_list()
            return users or []
        except Exception:
            return []
    
    async def find_all(self, skip: int = 0, limit: int = 50) -> List[User]:
        """
        Find all users
        
        Args:
            skip: Number to skip
            limit: Limit results
            
        Returns:
            List of users
        """
        try:
            users = await User.find(
                {"deleted_at": None}
            ).skip(skip).limit(limit).to_list()
            return users or []
        except Exception:
            return []
    
    async def create(self, user: User) -> User:
        """
        Create user
        
        Args:
            user: User to create
            
        Returns:
            Created user
        """
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
    
    async def update(self, user: User) -> User:
        """
        Update user
        
        Args:
            user: User to update
            
        Returns:
            Updated user
        """
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete user (soft delete)
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            user.deleted_at = datetime.utcnow()
            await user.save()
            return True
        except Exception:
            return False
    
    async def count(self) -> int:
        """
        Count total users
        
        Returns:
            Total count
        """
        try:
            count = await User.find({"deleted_at": None}).count()
            return count
        except Exception:
            return 0
    
    async def count_by_organization(self, organization_id: str) -> int:
        """
        Count users in organization
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Count
        """
        try:
            count = await User.find(
                {
                    "organizations": organization_id,
                    "deleted_at": None
                }
            ).count()
            return count
        except Exception:
            return 0
