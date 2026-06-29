# app/application/services/meeting_application_service.py

from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.services.meeting_service import MeetingService
from app.domain.models.meeting import MeetingStatus, MeetingType, AttendanceStatus, ApprovalStatus
from app.application.dtos.meeting_dto import (
    MeetingCreateRequest, MeetingUpdateRequest, MeetingRescheduleRequest,
    MeetingCancelRequest, AddAttendeeRequest, MarkAttendanceRequest,
    AddApprovalMemberRequest, ApprovalActionRequest, MeetingMinutesRequest,
    AddDocumentRequest, MeetingResponse, MeetingListResponse,
    MeetingStatisticsResponse, MeetingBriefResponse, AttendanceListResponse,
    MeetingApprovalResponse, UpcomingMeetingsResponse
)
from app.common.exceptions import ValidationError
from app.common.models.value_objects import Email


class MeetingApplicationService:
    """Application service for meeting operations"""
    
    def __init__(self, meeting_service: MeetingService):
        """
        Initialize meeting application service
        
        Args:
            meeting_service: Domain meeting service
        """
        self.meeting_service = meeting_service
    
    async def create_meeting(
        self,
        organizer_id: str,
        organizer_email: str,
        organizer_first_name: str,
        organizer_last_name: str,
        request: MeetingCreateRequest
    ) -> MeetingResponse:
        """Create a new meeting"""
        # Convert email string to Email value object
        email = Email(value=organizer_email)
        
        meeting = await self.meeting_service.create_meeting(
            title=request.title,
            meeting_type=request.meeting_type,
            organizer_id=organizer_id,
            organizer_email=email,
            organizer_first_name=organizer_first_name,
            organizer_last_name=organizer_last_name,
            scheduled_start_at=request.scheduled_start_at,
            scheduled_end_at=request.scheduled_end_at,
            description=request.description,
            location=request.location,
            location_url=request.location_url,
            is_virtual=request.is_virtual,
            requires_approval=request.requires_approval
        )
        
        return self._meeting_to_response(meeting)
    
    async def get_meeting(self, meeting_id: str) -> MeetingResponse:
        """Get meeting by ID"""
        meeting = await self.meeting_service.get_meeting(meeting_id)
        return self._meeting_to_response(meeting)
    
    async def list_meetings(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> MeetingListResponse:
        """List all meetings"""
        meetings = await self.meeting_service.meeting_repository.find_all(skip, limit)
        total = await self.meeting_service.meeting_repository.count()
        
        return MeetingListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._meeting_to_response(m) for m in meetings]
        )
    
    async def list_organized_meetings(
        self,
        organizer_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> MeetingListResponse:
        """List meetings organized by a user"""
        status_enum = MeetingStatus(status) if status else None
        
        meetings = await self.meeting_service.get_meetings_by_organizer(
            organizer_id, status_enum, skip, limit
        )
        
        total = await self.meeting_service.meeting_repository.count_by_status(
            status_enum
        ) if status_enum else await self.meeting_service.meeting_repository.count()
        
        return MeetingListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._meeting_to_response(m) for m in meetings]
        )
    
    async def list_attended_meetings(
        self,
        member_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> MeetingListResponse:
        """List meetings a member attends"""
        meetings = await self.meeting_service.get_meetings_by_member(
            member_id, skip, limit
        )
        
        total = len(meetings) if len(meetings) < limit else len(meetings) + 1
        
        return MeetingListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._meeting_to_response(m) for m in meetings]
        )
    
    async def list_meetings_by_type(
        self,
        meeting_type: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> MeetingListResponse:
        """List meetings by type"""
        type_enum = MeetingType(meeting_type)
        status_enum = MeetingStatus(status) if status else None
        
        meetings = await self.meeting_service.get_meetings_by_type(
            type_enum, status_enum, skip, limit
        )
        
        return MeetingListResponse(
            total=len(meetings),
            skip=skip,
            limit=limit,
            items=[self._meeting_to_response(m) for m in meetings]
        )
    
    async def get_upcoming_meetings(self, days: int = 7) -> UpcomingMeetingsResponse:
        """Get upcoming meetings"""
        meetings = await self.meeting_service.get_upcoming_meetings(days)
        
        return UpcomingMeetingsResponse(
            days_ahead=days,
            count=len(meetings),
            meetings=[self._meeting_to_brief_response(m) for m in meetings]
        )
    
    async def add_attendee(
        self,
        meeting_id: str,
        request: AddAttendeeRequest
    ) -> MeetingResponse:
        """Add attendee to meeting"""
        meeting = await self.meeting_service.add_attendee(
            meeting_id=meeting_id,
            member_id=request.member_id,
            email=str(request.email),
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        return self._meeting_to_response(meeting)
    
    async def remove_attendee(self, meeting_id: str, member_id: str) -> MeetingResponse:
        """Remove attendee from meeting"""
        meeting = await self.meeting_service.remove_attendee(meeting_id, member_id)
        return self._meeting_to_response(meeting)
    
    async def check_in_attendee(self, meeting_id: str, member_id: str) -> MeetingResponse:
        """Check in an attendee"""
        meeting = await self.meeting_service.check_in_attendee(meeting_id, member_id)
        return self._meeting_to_response(meeting)
    
    async def check_out_attendee(self, meeting_id: str, member_id: str) -> MeetingResponse:
        """Check out an attendee"""
        meeting = await self.meeting_service.check_out_attendee(meeting_id, member_id)
        return self._meeting_to_response(meeting)
    
    async def mark_attendance(
        self,
        meeting_id: str,
        member_id: str,
        request: MarkAttendanceRequest
    ) -> MeetingResponse:
        """Mark attendance for attendee"""
        meeting = await self.meeting_service.mark_attendance(
            meeting_id, member_id, request.status
        )
        
        return self._meeting_to_response(meeting)
    
    async def get_attendance_list(self, meeting_id: str) -> AttendanceListResponse:
        """Get attendance list for meeting"""
        meeting = await self.meeting_service.get_meeting(meeting_id)
        
        return AttendanceListResponse(
            meeting_id=str(meeting.id),
            meeting_title=meeting.title,
            scheduled_start_at=meeting.scheduled_start_at,
            total_attendees=meeting.attendees_count,
            present_count=meeting.present_count,
            absent_count=meeting.absent_count,
            attendance_rate=meeting.attendance_rate,
            attendees=[{
                "member_id": a.member_id,
                "full_name": a.full_name,
                "email": str(a.email),
                "attendance_status": a.attendance_status,
                "check_in_time": a.check_in_time,
                "check_out_time": a.check_out_time,
                "duration_minutes": a.duration_minutes,
                "notes": a.notes
            } for a in meeting.attendees]
        )
    
    async def start_meeting(self, meeting_id: str) -> MeetingResponse:
        """Start a meeting"""
        meeting = await self.meeting_service.start_meeting(meeting_id)
        return self._meeting_to_response(meeting)
    
    async def end_meeting(self, meeting_id: str) -> MeetingResponse:
        """End a meeting"""
        meeting = await self.meeting_service.end_meeting(meeting_id)
        return self._meeting_to_response(meeting)
    
    async def reschedule_meeting(
        self,
        meeting_id: str,
        request: MeetingRescheduleRequest
    ) -> MeetingResponse:
        """Reschedule a meeting"""
        meeting = await self.meeting_service.reschedule_meeting(
            meeting_id,
            request.scheduled_start_at,
            request.scheduled_end_at
        )
        
        return self._meeting_to_response(meeting)
    
    async def cancel_meeting(
        self,
        meeting_id: str,
        request: MeetingCancelRequest
    ) -> MeetingResponse:
        """Cancel a meeting"""
        meeting = await self.meeting_service.cancel_meeting(
            meeting_id, request.reason
        )
        
        return self._meeting_to_response(meeting)
    
    async def add_approval_member(
        self,
        meeting_id: str,
        request: AddApprovalMemberRequest
    ) -> MeetingResponse:
        """Add approval member"""
        meeting = await self.meeting_service.add_approval_member(
            meeting_id=meeting_id,
            member_id=request.member_id,
            email=str(request.email),
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        return self._meeting_to_response(meeting)
    
    async def approve_meeting(self, meeting_id: str, member_id: str) -> MeetingResponse:
        """Approve meeting"""
        meeting = await self.meeting_service.approve_meeting(meeting_id, member_id)
        return self._meeting_to_response(meeting)
    
    async def reject_meeting(
        self,
        meeting_id: str,
        member_id: str,
        request: ApprovalActionRequest
    ) -> MeetingResponse:
        """Reject meeting"""
        if not request.reason:
            raise ValidationError("Rejection reason is required")
        
        meeting = await self.meeting_service.reject_meeting(
            meeting_id, member_id, request.reason
        )
        
        return self._meeting_to_response(meeting)
    
    async def get_approval_details(self, meeting_id: str) -> MeetingApprovalResponse:
        """Get meeting approval details"""
        meeting = await self.meeting_service.get_meeting(meeting_id)
        
        return MeetingApprovalResponse(
            meeting_id=str(meeting.id),
            title=meeting.title,
            scheduled_start_at=meeting.scheduled_start_at,
            total_approvers=len(meeting.approvals),
            pending_approvals=meeting.pending_approvals,
            approved_count=meeting.approved_count,
            rejected_count=meeting.rejected_count,
            approval_rate=meeting.approval_rate,
            requires_approval=meeting.requires_approval,
            approvals=[{
                "member_id": a.member_id,
                "full_name": a.full_name,
                "email": str(a.email),
                "status": a.status,
                "approved_at": a.approved_at,
                "rejected_at": a.rejected_at,
                "rejection_reason": a.rejection_reason
            } for a in meeting.approvals]
        )
    
    async def set_meeting_minutes(
        self,
        meeting_id: str,
        request: MeetingMinutesRequest
    ) -> MeetingResponse:
        """Set meeting minutes"""
        meeting = await self.meeting_service.set_meeting_minutes(
            meeting_id, request.minutes
        )
        
        return self._meeting_to_response(meeting)
    
    async def add_document(
        self,
        meeting_id: str,
        request: AddDocumentRequest
    ) -> MeetingResponse:
        """Add document to meeting"""
        meeting = await self.meeting_service.add_document(
            meeting_id, request.document_id
        )
        
        return self._meeting_to_response(meeting)
    
    async def get_statistics(self) -> MeetingStatisticsResponse:
        """Get meeting statistics"""
        stats = await self.meeting_service.get_meeting_statistics()
        
        return MeetingStatisticsResponse(
            total_meetings=stats["total_meetings"],
            scheduled=stats["scheduled"],
            ongoing=stats["ongoing"],
            completed=stats["completed"],
            cancelled=stats["cancelled"],
            total_attendees_count=0,  # Can be calculated from completed meetings
            average_attendance_rate=0.0,
            most_recent_meeting=datetime.utcnow(),
            upcoming_meetings_count=stats["scheduled"]
        )
    
    def _meeting_to_response(self, meeting) -> MeetingResponse:
        """Convert meeting to response DTO"""
        return MeetingResponse(
            id=str(meeting.id),
            title=meeting.title,
            description=meeting.description,
            meeting_type=meeting.meeting_type,
            status=meeting.status,
            organizer_full_name=meeting.organizer_full_name,
            organizer_email=str(meeting.organizer_email),
            scheduled_start_at=meeting.scheduled_start_at,
            scheduled_end_at=meeting.scheduled_end_at,
            actual_start_at=meeting.actual_start_at,
            actual_end_at=meeting.actual_end_at,
            location=meeting.location,
            location_url=meeting.location_url,
            is_virtual=meeting.is_virtual,
            agenda=meeting.agenda,
            minutes=meeting.minutes,
            documents=meeting.documents,
            attendees=[{
                "member_id": a.member_id,
                "full_name": a.full_name,
                "email": str(a.email),
                "attendance_status": a.attendance_status,
                "check_in_time": a.check_in_time,
                "check_out_time": a.check_out_time,
                "duration_minutes": a.duration_minutes,
                "notes": a.notes
            } for a in meeting.attendees],
            attendees_count=meeting.attendees_count,
            present_count=meeting.present_count,
            absent_count=meeting.absent_count,
            excused_count=meeting.excused_count,
            late_count=meeting.late_count,
            attendance_rate=meeting.attendance_rate,
            expected_attendees_count=meeting.expected_attendees_count,
            approvals=[{
                "member_id": a.member_id,
                "full_name": a.full_name,
                "email": str(a.email),
                "status": a.status,
                "approved_at": a.approved_at,
                "rejected_at": a.rejected_at,
                "rejection_reason": a.rejection_reason
            } for a in meeting.approvals],
            pending_approvals=meeting.pending_approvals,
            approved_count=meeting.approved_count,
            rejected_count=meeting.rejected_count,
            approval_rate=meeting.approval_rate,
            requires_approval=meeting.requires_approval,
            duration_minutes=meeting.duration_minutes,
            minutes_until_start=meeting.minutes_until_start,
            is_scheduled=meeting.is_scheduled,
            is_active=meeting.is_active,
            is_completed=meeting.is_completed,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
    
    def _meeting_to_brief_response(self, meeting) -> MeetingBriefResponse:
        """Convert meeting to brief response DTO"""
        return MeetingBriefResponse(
            id=str(meeting.id),
            title=meeting.title,
            meeting_type=meeting.meeting_type,
            status=meeting.status,
            organizer_full_name=meeting.organizer_full_name,
            scheduled_start_at=meeting.scheduled_start_at,
            scheduled_end_at=meeting.scheduled_end_at,
            location=meeting.location,
            is_virtual=meeting.is_virtual,
            attendees_count=meeting.attendees_count,
            is_active=meeting.is_active
        )
