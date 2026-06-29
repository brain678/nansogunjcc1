# app/infrastructure/persistence/meeting_repository.py

from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.models.meeting import Meeting, MeetingStatus, MeetingType, ApprovalStatus
from app.application.interfaces.meeting_repository import IMeetingRepository
from app.common.exceptions import EntityNotFoundError


class MeetingRepository(IMeetingRepository):
    """Meeting repository using Beanie ODM"""
    
    def __init__(self):
        """Initialize meeting repository"""
        self.model = Meeting
    
    async def get_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """Get meeting by ID"""
        try:
            meeting = await self.model.get(meeting_id)
            if meeting and not meeting.is_deleted():
                return meeting
            return None
        except Exception:
            return None
    
    async def find_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Find all meetings"""
        try:
            meetings = await self.model.find(
                {"deleted_at": None}
            ).skip(skip).limit(limit).to_list()
            return meetings
        except Exception:
            return []
    
    async def find_by_organizer(
        self,
        organizer_id: str,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by organizer"""
        try:
            query = {"organizer_id": organizer_id, "deleted_at": None}
            
            if status:
                query["status"] = status
            
            meetings = await self.model.find(
                query
            ).skip(skip).limit(limit).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def find_by_attendee(
        self,
        member_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by attendee"""
        try:
            meetings = await self.model.find(
                {
                    "attendees.member_id": member_id,
                    "deleted_at": None
                }
            ).skip(skip).limit(limit).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def find_by_type(
        self,
        meeting_type: MeetingType,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by type"""
        try:
            query = {"meeting_type": meeting_type, "deleted_at": None}
            
            if status:
                query["status"] = status
            
            meetings = await self.model.find(
                query
            ).skip(skip).limit(limit).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def find_by_status(
        self,
        status: MeetingStatus,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by status"""
        try:
            meetings = await self.model.find(
                {"status": status, "deleted_at": None}
            ).skip(skip).limit(limit).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def find_upcoming(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find upcoming meetings within date range"""
        try:
            meetings = await self.model.find(
                {
                    "scheduled_start_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    },
                    "status": {"$in": [MeetingStatus.SCHEDULED, MeetingStatus.POSTPONED]},
                    "deleted_at": None
                }
            ).skip(skip).limit(limit).sort("scheduled_start_at", 1).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def find_pending_approval(self, limit: int = 10) -> List[Meeting]:
        """Find meetings pending approval"""
        try:
            meetings = await self.model.find(
                {
                    "requires_approval": True,
                    "approvals": {
                        "$elemMatch": {"status": ApprovalStatus.PENDING}
                    },
                    "deleted_at": None
                }
            ).limit(limit).sort("created_at", -1).to_list()
            
            return meetings
        except Exception:
            return []
    
    async def create(self, meeting: Meeting) -> Meeting:
        """Create new meeting"""
        try:
            created_meeting = await meeting.save()
            return created_meeting
        except Exception as e:
            raise EntityNotFoundError(f"Failed to create meeting: {str(e)}")
    
    async def save(self, meeting: Meeting) -> Meeting:
        """Save meeting (create or update)"""
        try:
            saved_meeting = await meeting.save()
            return saved_meeting
        except Exception as e:
            raise EntityNotFoundError(f"Failed to save meeting: {str(e)}")
    
    async def delete(self, meeting_id: str) -> bool:
        """Soft delete meeting"""
        try:
            meeting = await self.get_by_id(meeting_id)
            if not meeting:
                return False
            
            meeting.soft_delete()
            await meeting.save()
            return True
        except Exception:
            return False
    
    async def count(self) -> int:
        """Count total meetings"""
        try:
            count = await self.model.find({"deleted_at": None}).count()
            return count
        except Exception:
            return 0
    
    async def count_by_status(self, status: MeetingStatus) -> int:
        """Count meetings by status"""
        try:
            count = await self.model.find(
                {"status": status, "deleted_at": None}
            ).count()
            return count
        except Exception:
            return 0
