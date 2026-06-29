# app/infrastructure/persistence/member_repository.py

from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.models.member import Member, MembershipStatus, MembershipType
from app.application.interfaces.member_repository import IMemberRepository
from app.common.exceptions import EntityNotFoundError


class MemberRepository(IMemberRepository):
    """Member repository using Beanie ODM"""
    
    def __init__(self):
        """Initialize member repository"""
        self.model = Member
    
    async def get_by_id(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        try:
            # This would use Beanie's get_motor_collection or similar
            # For now, implementing the interface
            member = await self.model.get(member_id)
            if member and not member.is_deleted():
                return member
            return None
        except Exception:
            return None
    
    async def find_by_user_id(self, user_id: str) -> Optional[Member]:
        """Find member by user ID"""
        try:
            member = await self.model.find_one(
                {"user_id": user_id, "deleted_at": None}
            )
            return member
        except Exception:
            return None
    
    async def find_by_membership_number(self, membership_number: str) -> Optional[Member]:
        """Find member by membership number"""
        try:
            member = await self.model.find_one(
                {"membership_number": membership_number, "deleted_at": None}
            )
            return member
        except Exception:
            return None
    
    async def find_by_email(self, email: str) -> Optional[Member]:
        """Find member by email"""
        try:
            member = await self.model.find_one(
                {"email.value": email, "deleted_at": None}
            )
            return member
        except Exception:
            return None
    
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[MembershipStatus] = None,
        membership_type: Optional[MembershipType] = None
    ) -> List[Member]:
        """Find all members with filters"""
        try:
            query = {"deleted_at": None}
            
            if status:
                query["status"] = status
            
            if membership_type:
                query["membership_type"] = membership_type
            
            members = await self.model.find(
                query
            ).skip(skip).limit(limit).to_list()
            
            return members
        except Exception:
            return []
    
    async def find_expiring(self, days: int = 30) -> List[Member]:
        """Find memberships expiring soon"""
        try:
            now = datetime.utcnow()
            cutoff_date = now + timedelta(days=days)
            
            members = await self.model.find({
                "membership_expiry_date": {
                    "$lte": cutoff_date,
                    "$gte": now
                },
                "status": MembershipStatus.ACTIVE,
                "deleted_at": None
            }).to_list()
            
            return members
        except Exception:
            return []
    
    async def create(self, member: Member) -> Member:
        """Create new member"""
        try:
            created_member = await member.save()
            return created_member
        except Exception as e:
            raise EntityNotFoundError(f"Failed to create member: {str(e)}")
    
    async def save(self, member: Member) -> Member:
        """Save member (create or update)"""
        try:
            saved_member = await member.save()
            return saved_member
        except Exception as e:
            raise EntityNotFoundError(f"Failed to save member: {str(e)}")
    
    async def delete(self, member_id: str) -> bool:
        """Soft delete member"""
        try:
            member = await self.get_by_id(member_id)
            if not member:
                return False
            
            member.soft_delete()
            await member.save()
            return True
        except Exception:
            return False
    
    async def count(self, status: Optional[MembershipStatus] = None) -> int:
        """Count members"""
        try:
            query = {"deleted_at": None}
            
            if status:
                query["status"] = status
            
            count = await self.model.find(query).count()
            return count
        except Exception:
            return 0
