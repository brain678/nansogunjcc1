# app/domain/models/meeting.py

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from pydantic import Field
from app.common.models.base_entity import BaseEntity
from app.common.models.value_objects import Email


class MeetingType(str, Enum):
    """Meeting type enumeration"""
    GENERAL_ASSEMBLY = "GENERAL_ASSEMBLY"
    EXECUTIVE = "EXECUTIVE"
    CHAPTER = "CHAPTER"
    COMMITTEE = "COMMITTEE"
    WORKSHOP = "WORKSHOP"
    TRAINING = "TRAINING"
    EMERGENCY = "EMERGENCY"


class MeetingStatus(str, Enum):
    """Meeting status enumeration"""
    SCHEDULED = "SCHEDULED"
    POSTPONED = "POSTPONED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AttendanceStatus(str, Enum):
    """Attendance status enumeration"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    EXCUSED = "EXCUSED"
    LATE = "LATE"


class ApprovalStatus(str, Enum):
    """Approval status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MeetingAttendee(BaseEntity):
    """Meeting attendee entity"""
    member_id: str
    email: Email
    first_name: str
    last_name: str
    attendance_status: AttendanceStatus = AttendanceStatus.ABSENT
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full name of attendee"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def duration_minutes(self) -> int:
        """Get attendance duration in minutes"""
        if self.check_in_time and self.check_out_time:
            return int((self.check_out_time - self.check_in_time).total_seconds() / 60)
        return 0
    
    def check_in(self) -> None:
        """Check in attendee"""
        if not self.check_in_time:
            self.check_in_time = datetime.utcnow()
            self.attendance_status = AttendanceStatus.PRESENT
    
    def check_out(self) -> None:
        """Check out attendee"""
        if self.check_in_time and not self.check_out_time:
            self.check_out_time = datetime.utcnow()


class MeetingApproval(BaseEntity):
    """Meeting approval record"""
    member_id: str
    email: Email
    first_name: str
    last_name: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full name of approver"""
        return f"{self.first_name} {self.last_name}"


class Meeting(BaseEntity):
    """Meeting domain entity"""
    
    # Basic Information
    title: str
    description: Optional[str] = None
    meeting_type: MeetingType
    status: MeetingStatus = MeetingStatus.SCHEDULED
    
    # Organizer Information
    organizer_id: str
    organizer_email: Email
    organizer_first_name: str
    organizer_last_name: str
    
    # Scheduling
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    
    # Location
    location: Optional[str] = None
    location_url: Optional[str] = None  # For virtual meetings
    is_virtual: bool = False
    
    # Content
    agenda: Optional[str] = None
    minutes: Optional[str] = None
    documents: List[str] = Field(default_factory=list)  # Document IDs or URLs
    
    # Attendance & Approvals
    attendees: List[MeetingAttendee] = Field(default_factory=list)
    expected_attendees_count: int = 0
    approvals: List[MeetingApproval] = Field(default_factory=list)
    
    # Meeting Details
    quorum_required: bool = True
    min_attendees_required: int = 0
    requires_approval: bool = False
    
    # Tracking
    created_by: str
    last_modified_by: Optional[str] = None
    
    @property
    def organizer_full_name(self) -> str:
        """Get organizer full name"""
        return f"{self.organizer_first_name} {self.organizer_last_name}"
    
    @property
    def attendees_count(self) -> int:
        """Get total number of attendees"""
        return len(self.attendees)
    
    @property
    def present_count(self) -> int:
        """Get count of present attendees"""
        return sum(1 for a in self.attendees if a.attendance_status == AttendanceStatus.PRESENT)
    
    @property
    def absent_count(self) -> int:
        """Get count of absent attendees"""
        return sum(1 for a in self.attendees if a.attendance_status == AttendanceStatus.ABSENT)
    
    @property
    def excused_count(self) -> int:
        """Get count of excused attendees"""
        return sum(1 for a in self.attendees if a.attendance_status == AttendanceStatus.EXCUSED)
    
    @property
    def late_count(self) -> int:
        """Get count of late attendees"""
        return sum(1 for a in self.attendees if a.attendance_status == AttendanceStatus.LATE)
    
    @property
    def attendance_rate(self) -> float:
        """Get attendance rate percentage"""
        if self.expected_attendees_count == 0:
            return 0.0
        return (self.present_count / self.expected_attendees_count) * 100
    
    @property
    def pending_approvals(self) -> int:
        """Get count of pending approvals"""
        return sum(1 for a in self.approvals if a.status == ApprovalStatus.PENDING)
    
    @property
    def approved_count(self) -> int:
        """Get count of approved"""
        return sum(1 for a in self.approvals if a.status == ApprovalStatus.APPROVED)
    
    @property
    def rejected_count(self) -> int:
        """Get count of rejected"""
        return sum(1 for a in self.approvals if a.status == ApprovalStatus.REJECTED)
    
    @property
    def approval_rate(self) -> float:
        """Get approval rate percentage"""
        total = len(self.approvals)
        if total == 0:
            return 0.0
        return (self.approved_count / total) * 100
    
    @property
    def is_scheduled(self) -> bool:
        """Check if meeting is in future"""
        return self.status == MeetingStatus.SCHEDULED and self.scheduled_start_at > datetime.utcnow()
    
    @property
    def is_active(self) -> bool:
        """Check if meeting is currently active"""
        return self.status == MeetingStatus.ONGOING
    
    @property
    def is_completed(self) -> bool:
        """Check if meeting is completed"""
        return self.status == MeetingStatus.COMPLETED
    
    @property
    def duration_minutes(self) -> int:
        """Get meeting duration in minutes"""
        end_time = self.actual_end_at or self.scheduled_end_at
        start_time = self.actual_start_at or self.scheduled_start_at
        return int((end_time - start_time).total_seconds() / 60)
    
    @property
    def minutes_until_start(self) -> int:
        """Get minutes until meeting starts"""
        if self.is_scheduled:
            now = datetime.utcnow()
            delta = self.scheduled_start_at - now
            return int(delta.total_seconds() / 60)
        return 0
    
    def add_attendee(
        self,
        member_id: str,
        email: str,
        first_name: str,
        last_name: str
    ) -> None:
        """Add attendee to meeting"""
        # Check if attendee already exists
        existing = next((a for a in self.attendees if a.member_id == member_id), None)
        if existing:
            return
        
        attendee = MeetingAttendee(
            member_id=member_id,
            email=Email(value=email),
            first_name=first_name,
            last_name=last_name
        )
        self.attendees.append(attendee)
    
    def remove_attendee(self, member_id: str) -> bool:
        """Remove attendee from meeting"""
        original_count = len(self.attendees)
        self.attendees = [a for a in self.attendees if a.member_id != member_id]
        return len(self.attendees) < original_count
    
    def get_attendee(self, member_id: str) -> Optional[MeetingAttendee]:
        """Get attendee by member ID"""
        return next((a for a in self.attendees if a.member_id == member_id), None)
    
    def mark_attendance(self, member_id: str, status: AttendanceStatus) -> bool:
        """Mark attendance status for attendee"""
        attendee = self.get_attendee(member_id)
        if not attendee:
            return False
        
        attendee.attendance_status = status
        if status == AttendanceStatus.PRESENT:
            attendee.check_in()
        return True
    
    def check_in_attendee(self, member_id: str) -> bool:
        """Check in an attendee"""
        attendee = self.get_attendee(member_id)
        if not attendee:
            return False
        
        attendee.check_in()
        return True
    
    def check_out_attendee(self, member_id: str) -> bool:
        """Check out an attendee"""
        attendee = self.get_attendee(member_id)
        if not attendee:
            return False
        
        attendee.check_out()
        return True
    
    def schedule_meeting(self, start_time: datetime, end_time: datetime) -> None:
        """Schedule meeting"""
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        self.scheduled_start_at = start_time
        self.scheduled_end_at = end_time
        self.status = MeetingStatus.SCHEDULED
    
    def postpone_meeting(self, new_start_time: datetime, new_end_time: datetime) -> None:
        """Postpone meeting to new time"""
        if new_start_time >= new_end_time:
            raise ValueError("Start time must be before end time")
        
        if new_start_time <= datetime.utcnow():
            raise ValueError("Cannot schedule meeting in the past")
        
        self.scheduled_start_at = new_start_time
        self.scheduled_end_at = new_end_time
        self.status = MeetingStatus.POSTPONED
    
    def start_meeting(self) -> None:
        """Start meeting"""
        if self.status not in [MeetingStatus.SCHEDULED, MeetingStatus.POSTPONED]:
            raise ValueError("Cannot start meeting in current status")
        
        self.actual_start_at = datetime.utcnow()
        self.status = MeetingStatus.ONGOING
    
    def end_meeting(self) -> None:
        """End meeting"""
        if self.status != MeetingStatus.ONGOING:
            raise ValueError("Meeting is not currently ongoing")
        
        self.actual_end_at = datetime.utcnow()
        self.status = MeetingStatus.COMPLETED
    
    def cancel_meeting(self, reason: Optional[str] = None) -> None:
        """Cancel meeting"""
        if self.status == MeetingStatus.COMPLETED:
            raise ValueError("Cannot cancel completed meeting")
        
        self.status = MeetingStatus.CANCELLED
        if reason:
            self.description = f"{self.description}\n[CANCELLED: {reason}]"
    
    def add_approval(
        self,
        member_id: str,
        email: str,
        first_name: str,
        last_name: str
    ) -> None:
        """Add approval record"""
        # Check if approval already exists
        existing = next((a for a in self.approvals if a.member_id == member_id), None)
        if existing:
            return
        
        approval = MeetingApproval(
            member_id=member_id,
            email=Email(value=email),
            first_name=first_name,
            last_name=last_name
        )
        self.approvals.append(approval)
    
    def approve_meeting(self, member_id: str) -> bool:
        """Approve meeting"""
        approval = next((a for a in self.approvals if a.member_id == member_id), None)
        if not approval:
            return False
        
        approval.status = ApprovalStatus.APPROVED
        approval.approved_at = datetime.utcnow()
        return True
    
    def reject_meeting(self, member_id: str, reason: str) -> bool:
        """Reject meeting"""
        approval = next((a for a in self.approvals if a.member_id == member_id), None)
        if not approval:
            return False
        
        approval.status = ApprovalStatus.REJECTED
        approval.rejected_at = datetime.utcnow()
        approval.rejection_reason = reason
        return True
    
    def set_minutes(self, minutes_content: str) -> None:
        """Set meeting minutes"""
        if self.status != MeetingStatus.COMPLETED:
            raise ValueError("Can only set minutes for completed meetings")
        
        self.minutes = minutes_content
    
    def add_document(self, document_id: str) -> None:
        """Add document to meeting"""
        if document_id not in self.documents:
            self.documents.append(document_id)
