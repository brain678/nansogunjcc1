# app/application/interfaces/meeting_repository.py

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from app.domain.models.meeting import Meeting, MeetingStatus, MeetingType


class IMeetingRepository(ABC):
    """Meeting repository interface"""
    
    @abstractmethod
    async def get_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """Get meeting by ID"""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Find all meetings"""
        pass
    
    @abstractmethod
    async def find_by_organizer(
        self,
        organizer_id: str,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by organizer"""
        pass
    
    @abstractmethod
    async def find_by_attendee(
        self,
        member_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by attendee"""
        pass
    
    @abstractmethod
    async def find_by_type(
        self,
        meeting_type: MeetingType,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by type"""
        pass
    
    @abstractmethod
    async def find_by_status(
        self,
        status: MeetingStatus,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find meetings by status"""
        pass
    
    @abstractmethod
    async def find_upcoming(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """Find upcoming meetings within date range"""
        pass
    
    @abstractmethod
    async def find_pending_approval(self, limit: int = 10) -> List[Meeting]:
        """Find meetings pending approval"""
        pass
    
    @abstractmethod
    async def create(self, meeting: Meeting) -> Meeting:
        """Create new meeting"""
        pass
    
    @abstractmethod
    async def save(self, meeting: Meeting) -> Meeting:
        """Save meeting (create or update)"""
        pass
    
    @abstractmethod
    async def delete(self, meeting_id: str) -> bool:
        """Delete meeting"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total meetings"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: MeetingStatus) -> int:
        """Count meetings by status"""
        pass
