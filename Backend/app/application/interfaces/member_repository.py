# app/application/interfaces/member_repository.py

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.models.member import Member, MembershipStatus, MembershipType


class IMemberRepository(ABC):
    """Member repository interface"""
    
    @abstractmethod
    async def get_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> Optional[Member]:
        """Find member by user ID"""
        pass
    
    @abstractmethod
    async def find_by_membership_number(self, membership_number: str) -> Optional[Member]:
        """Find member by membership number"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Member]:
        """Find member by email"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[MembershipStatus] = None,
        membership_type: Optional[MembershipType] = None
    ) -> List[Member]:
        """Find all members with filters"""
        pass
    
    @abstractmethod
    async def find_expiring(self, days: int = 30) -> List[Member]:
        """Find memberships expiring soon"""
        pass
    
    @abstractmethod
    async def create(self, member: Member) -> Member:
        """Create new member"""
        pass
    
    @abstractmethod
    async def save(self, member: Member) -> Member:
        """Save member (create or update)"""
        pass
    
    @abstractmethod
    async def delete(self, member_id: str) -> bool:
        """Delete member"""
        pass
    
    @abstractmethod
    async def count(self, status: Optional[MembershipStatus] = None) -> int:
        """Count members"""
        pass
