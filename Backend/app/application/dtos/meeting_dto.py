# app/application/dtos/meeting_dto.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.domain.models.meeting import MeetingType, MeetingStatus, AttendanceStatus, ApprovalStatus


# Request DTOs

class MeetingCreateRequest(BaseModel):
    """Create meeting request"""
    title: str
    meeting_type: MeetingType
    description: Optional[str] = None
    location: Optional[str] = None
    location_url: Optional[str] = None
    is_virtual: bool = False
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    requires_approval: bool = False


class MeetingUpdateRequest(BaseModel):
    """Update meeting request"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    location_url: Optional[str] = None
    is_virtual: Optional[bool] = None
    scheduled_start_at: Optional[datetime] = None
    scheduled_end_at: Optional[datetime] = None


class MeetingRescheduleRequest(BaseModel):
    """Reschedule meeting request"""
    scheduled_start_at: datetime
    scheduled_end_at: datetime


class MeetingCancelRequest(BaseModel):
    """Cancel meeting request"""
    reason: Optional[str] = None


class AddAttendeeRequest(BaseModel):
    """Add attendee request"""
    member_id: str
    email: EmailStr
    first_name: str
    last_name: str


class MarkAttendanceRequest(BaseModel):
    """Mark attendance request"""
    status: AttendanceStatus


class AddApprovalMemberRequest(BaseModel):
    """Add approval member request"""
    member_id: str
    email: EmailStr
    first_name: str
    last_name: str


class ApprovalActionRequest(BaseModel):
    """Approval action request"""
    reason: Optional[str] = Field(None, description="Required for rejection")


class MeetingMinutesRequest(BaseModel):
    """Set meeting minutes request"""
    minutes: str


class AddDocumentRequest(BaseModel):
    """Add document to meeting request"""
    document_id: str


# Response DTOs

class AttendeeResponse(BaseModel):
    """Attendee response"""
    member_id: str
    full_name: str
    email: str
    attendance_status: AttendanceStatus
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    duration_minutes: int
    notes: Optional[str]


class ApprovalResponse(BaseModel):
    """Approval response"""
    member_id: str
    full_name: str
    email: str
    status: ApprovalStatus
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]


class MeetingResponse(BaseModel):
    """Meeting response"""
    id: str
    title: str
    description: Optional[str]
    meeting_type: MeetingType
    status: MeetingStatus
    
    organizer_full_name: str
    organizer_email: str
    
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    actual_start_at: Optional[datetime]
    actual_end_at: Optional[datetime]
    
    location: Optional[str]
    location_url: Optional[str]
    is_virtual: bool
    
    agenda: Optional[str]
    minutes: Optional[str]
    documents: List[str]
    
    attendees: List[AttendeeResponse]
    attendees_count: int
    present_count: int
    absent_count: int
    excused_count: int
    late_count: int
    attendance_rate: float
    expected_attendees_count: int
    
    approvals: List[ApprovalResponse]
    pending_approvals: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    requires_approval: bool
    
    duration_minutes: int
    minutes_until_start: int
    is_scheduled: bool
    is_active: bool
    is_completed: bool
    
    created_at: datetime
    updated_at: datetime


class MeetingListResponse(BaseModel):
    """Meeting list response"""
    total: int
    skip: int
    limit: int
    items: List[MeetingResponse]


class MeetingBriefResponse(BaseModel):
    """Brief meeting response"""
    id: str
    title: str
    meeting_type: MeetingType
    status: MeetingStatus
    organizer_full_name: str
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    location: Optional[str]
    is_virtual: bool
    attendees_count: int
    is_active: bool


class MeetingStatisticsResponse(BaseModel):
    """Meeting statistics response"""
    total_meetings: int
    scheduled: int
    ongoing: int
    completed: int
    cancelled: int
    total_attendees_count: int
    average_attendance_rate: float
    most_recent_meeting: Optional[datetime]
    upcoming_meetings_count: int


class AttendanceListResponse(BaseModel):
    """Attendance list response"""
    meeting_id: str
    meeting_title: str
    scheduled_start_at: datetime
    total_attendees: int
    present_count: int
    absent_count: int
    attendance_rate: float
    attendees: List[AttendeeResponse]


class MeetingApprovalResponse(BaseModel):
    """Meeting approval response"""
    meeting_id: str
    title: str
    scheduled_start_at: datetime
    total_approvers: int
    pending_approvals: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    requires_approval: bool
    approvals: List[ApprovalResponse]


class MeetingCalendarResponse(BaseModel):
    """Meeting calendar response"""
    date: str  # YYYY-MM-DD
    meetings: List[MeetingBriefResponse]


class UpcomingMeetingsResponse(BaseModel):
    """Upcoming meetings response"""
    days_ahead: int
    count: int
    meetings: List[MeetingBriefResponse]


class MeetingHistoryResponse(BaseModel):
    """Meeting history response"""
    completed_count: int
    cancelled_count: int
    average_attendance_rate: float
    total_attendees_count: int
    meetings: List[MeetingBriefResponse]
