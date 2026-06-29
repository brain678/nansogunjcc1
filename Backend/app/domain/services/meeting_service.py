# app/domain/services/meeting_service.py

from datetime import datetime, timedelta
from typing import Optional, List
from app.domain.models.meeting import Meeting, MeetingType, MeetingStatus, AttendanceStatus, ApprovalStatus
from app.common.exceptions import EntityNotFoundError, ValidationError, DuplicateResourceError
from app.common.models.value_objects import Email


class MeetingService:
    """Domain service for meeting operations"""
    
    def __init__(self, meeting_repository):
        """
        Initialize meeting service
        
        Args:
            meeting_repository: Repository for meeting persistence
        """
        self.meeting_repository = meeting_repository
    
    async def create_meeting(
        self,
        title: str,
        meeting_type: MeetingType,
        organizer_id: str,
        organizer_email: Email,
        organizer_first_name: str,
        organizer_last_name: str,
        scheduled_start_at: datetime,
        scheduled_end_at: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        location_url: Optional[str] = None,
        is_virtual: bool = False,
        requires_approval: bool = False
    ) -> Meeting:
        """
        Create a new meeting
        
        Args:
            title: Meeting title
            meeting_type: Type of meeting
            organizer_id: Organizer user ID
            organizer_email: Organizer email (Email value object)
            organizer_first_name: Organizer first name
            organizer_last_name: Organizer last name
            scheduled_start_at: Scheduled start time
            scheduled_end_at: Scheduled end time
            description: Meeting description
            location: Physical location
            location_url: Virtual meeting URL
            is_virtual: Whether meeting is virtual
            requires_approval: Whether meeting needs approval
            
        Returns:
            Created Meeting entity
            
        Raises:
            ValidationError: If validation fails
        """
        if scheduled_start_at >= scheduled_end_at:
            raise ValidationError("Start time must be before end time")
        
        if scheduled_start_at <= datetime.utcnow():
            raise ValidationError("Cannot schedule meeting in the past")
        
        meeting = Meeting(
            title=title,
            description=description,
            meeting_type=meeting_type,
            organizer_id=organizer_id,
            organizer_email=organizer_email,
            organizer_first_name=organizer_first_name,
            organizer_last_name=organizer_last_name,
            scheduled_start_at=scheduled_start_at,
            scheduled_end_at=scheduled_end_at,
            location=location,
            location_url=location_url,
            is_virtual=is_virtual,
            requires_approval=requires_approval,
            created_by=organizer_id
        )
        
        return await self.meeting_repository.create(meeting)
    
    async def get_meeting(self, meeting_id: str) -> Meeting:
        """
        Get meeting by ID
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Meeting entity
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.meeting_repository.get_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundError(f"Meeting not found: {meeting_id}")
        
        return meeting
    
    async def get_meetings_by_organizer(
        self,
        organizer_id: str,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """
        Get meetings organized by a user
        
        Args:
            organizer_id: Organizer user ID
            status: Optional status filter
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of meetings
        """
        return await self.meeting_repository.find_by_organizer(
            organizer_id=organizer_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def get_meetings_by_member(
        self,
        member_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """
        Get meetings a member is attending
        
        Args:
            member_id: Member ID
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of meetings
        """
        return await self.meeting_repository.find_by_attendee(
            member_id=member_id,
            skip=skip,
            limit=limit
        )
    
    async def get_meetings_by_type(
        self,
        meeting_type: MeetingType,
        status: Optional[MeetingStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Meeting]:
        """
        Get meetings by type
        
        Args:
            meeting_type: Type of meeting
            status: Optional status filter
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of meetings
        """
        return await self.meeting_repository.find_by_type(
            meeting_type=meeting_type,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def get_upcoming_meetings(self, days: int = 7) -> List[Meeting]:
        """
        Get upcoming meetings
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming meetings
        """
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)
        
        return await self.meeting_repository.find_upcoming(
            start_date=now,
            end_date=end_date
        )
    
    async def get_completed_meetings(self, limit: int = 10) -> List[Meeting]:
        """
        Get recently completed meetings
        
        Args:
            limit: Number of meetings to return
            
        Returns:
            List of completed meetings
        """
        return await self.meeting_repository.find_by_status(
            status=MeetingStatus.COMPLETED,
            limit=limit
        )
    
    async def get_meetings_pending_approval(self, limit: int = 10) -> List[Meeting]:
        """
        Get meetings pending approval
        
        Args:
            limit: Number of meetings to return
            
        Returns:
            List of meetings pending approval
        """
        return await self.meeting_repository.find_pending_approval(limit=limit)
    
    async def add_attendee(
        self,
        meeting_id: str,
        member_id: str,
        email: str,
        first_name: str,
        last_name: str
    ) -> Meeting:
        """
        Add attendee to meeting
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID
            email: Member email
            first_name: Member first name
            last_name: Member last name
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        meeting.add_attendee(
            member_id=member_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        return await self.meeting_repository.save(meeting)
    
    async def remove_attendee(self, meeting_id: str, member_id: str) -> Meeting:
        """
        Remove attendee from meeting
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.remove_attendee(member_id):
            raise EntityNotFoundError(f"Attendee not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def check_in_attendee(self, meeting_id: str, member_id: str) -> Meeting:
        """
        Check in an attendee
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting or attendee not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.check_in_attendee(member_id):
            raise EntityNotFoundError(f"Attendee not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def check_out_attendee(self, meeting_id: str, member_id: str) -> Meeting:
        """
        Check out an attendee
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting or attendee not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.check_out_attendee(member_id):
            raise EntityNotFoundError(f"Attendee not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def mark_attendance(
        self,
        meeting_id: str,
        member_id: str,
        status: AttendanceStatus
    ) -> Meeting:
        """
        Mark attendance for attendee
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID
            status: Attendance status
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting or attendee not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.mark_attendance(member_id, status):
            raise EntityNotFoundError(f"Attendee not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def start_meeting(self, meeting_id: str) -> Meeting:
        """
        Start a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
            ValidationError: If meeting cannot be started
        """
        meeting = await self.get_meeting(meeting_id)
        
        try:
            meeting.start_meeting()
        except ValueError as e:
            raise ValidationError(str(e))
        
        return await self.meeting_repository.save(meeting)
    
    async def end_meeting(self, meeting_id: str) -> Meeting:
        """
        End a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
            ValidationError: If meeting cannot be ended
        """
        meeting = await self.get_meeting(meeting_id)
        
        try:
            meeting.end_meeting()
        except ValueError as e:
            raise ValidationError(str(e))
        
        return await self.meeting_repository.save(meeting)
    
    async def reschedule_meeting(
        self,
        meeting_id: str,
        new_start_time: datetime,
        new_end_time: datetime
    ) -> Meeting:
        """
        Reschedule a meeting
        
        Args:
            meeting_id: Meeting ID
            new_start_time: New start time
            new_end_time: New end time
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
            ValidationError: If rescheduling fails
        """
        meeting = await self.get_meeting(meeting_id)
        
        try:
            meeting.postpone_meeting(new_start_time, new_end_time)
        except ValueError as e:
            raise ValidationError(str(e))
        
        return await self.meeting_repository.save(meeting)
    
    async def cancel_meeting(self, meeting_id: str, reason: Optional[str] = None) -> Meeting:
        """
        Cancel a meeting
        
        Args:
            meeting_id: Meeting ID
            reason: Cancellation reason
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
            ValidationError: If meeting cannot be cancelled
        """
        meeting = await self.get_meeting(meeting_id)
        
        try:
            meeting.cancel_meeting(reason)
        except ValueError as e:
            raise ValidationError(str(e))
        
        return await self.meeting_repository.save(meeting)
    
    async def add_approval_member(
        self,
        meeting_id: str,
        member_id: str,
        email: str,
        first_name: str,
        last_name: str
    ) -> Meeting:
        """
        Add approval member
        
        Args:
            meeting_id: Meeting ID
            member_id: Member ID to approve meeting
            email: Member email
            first_name: Member first name
            last_name: Member last name
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        meeting.add_approval(
            member_id=member_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        return await self.meeting_repository.save(meeting)
    
    async def approve_meeting(self, meeting_id: str, member_id: str) -> Meeting:
        """
        Approve meeting
        
        Args:
            meeting_id: Meeting ID
            member_id: Approving member ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.approve_meeting(member_id):
            raise EntityNotFoundError(f"Approval member not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def reject_meeting(
        self,
        meeting_id: str,
        member_id: str,
        reason: str
    ) -> Meeting:
        """
        Reject meeting
        
        Args:
            meeting_id: Meeting ID
            member_id: Rejecting member ID
            reason: Rejection reason
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        if not meeting.reject_meeting(member_id, reason):
            raise EntityNotFoundError(f"Approval member not found: {member_id}")
        
        return await self.meeting_repository.save(meeting)
    
    async def set_meeting_minutes(self, meeting_id: str, minutes: str) -> Meeting:
        """
        Set meeting minutes
        
        Args:
            meeting_id: Meeting ID
            minutes: Minutes content
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
            ValidationError: If meeting cannot have minutes set
        """
        meeting = await self.get_meeting(meeting_id)
        
        try:
            meeting.set_minutes(minutes)
        except ValueError as e:
            raise ValidationError(str(e))
        
        return await self.meeting_repository.save(meeting)
    
    async def add_document(self, meeting_id: str, document_id: str) -> Meeting:
        """
        Add document to meeting
        
        Args:
            meeting_id: Meeting ID
            document_id: Document ID
            
        Returns:
            Updated meeting
            
        Raises:
            EntityNotFoundError: If meeting not found
        """
        meeting = await self.get_meeting(meeting_id)
        
        meeting.add_document(document_id)
        
        return await self.meeting_repository.save(meeting)
    
    async def get_meeting_statistics(self) -> dict:
        """
        Get overall meeting statistics
        
        Returns:
            Statistics dictionary
        """
        total = await self.meeting_repository.count()
        scheduled = await self.meeting_repository.count_by_status(MeetingStatus.SCHEDULED)
        ongoing = await self.meeting_repository.count_by_status(MeetingStatus.ONGOING)
        completed = await self.meeting_repository.count_by_status(MeetingStatus.COMPLETED)
        cancelled = await self.meeting_repository.count_by_status(MeetingStatus.CANCELLED)
        
        return {
            "total_meetings": total,
            "scheduled": scheduled,
            "ongoing": ongoing,
            "completed": completed,
            "cancelled": cancelled
        }
