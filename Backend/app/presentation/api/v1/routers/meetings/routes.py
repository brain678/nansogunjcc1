# app/presentation/api/v1/routers/meetings/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from app.application.services.meeting_application_service import MeetingApplicationService
from app.application.dtos.meeting_dto import (
    MeetingCreateRequest, MeetingUpdateRequest, MeetingRescheduleRequest,
    MeetingCancelRequest, AddAttendeeRequest, MarkAttendanceRequest,
    AddApprovalMemberRequest, ApprovalActionRequest, MeetingMinutesRequest,
    AddDocumentRequest, MeetingResponse, MeetingListResponse,
    MeetingStatisticsResponse, AttendanceListResponse,
    MeetingApprovalResponse, UpcomingMeetingsResponse
)
from app.common.exceptions import AppException
from app.presentation.api.v1.dependencies import get_current_user_id


# Router for meeting endpoints
router = APIRouter(
    prefix="/api/v1/meetings",
    tags=["meetings"]
)


# Dependency to get meeting service (would be injected from DI container)
async def get_meeting_service() -> MeetingApplicationService:
    """Get meeting application service"""
    from app.domain.services.meeting_service import MeetingService
    from app.infrastructure.persistence.meeting_repository import MeetingRepository
    
    repository = MeetingRepository()
    domain_service = MeetingService(repository)
    return MeetingApplicationService(domain_service)


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=201,
    summary="Create meeting",
    description="Create a new meeting"
)
async def create_meeting(
    request: MeetingCreateRequest,
    organizer_id: str = Depends(get_current_user_id),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Create a new meeting"""
    try:
        # For now, using default values for organizer details
        # In production, these would be fetched from the authenticated user
        return await meeting_service.create_meeting(
            organizer_id=organizer_id,
            organizer_email="organizer@example.com",
            organizer_first_name="Organizer",
            organizer_last_name="User",
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Get meeting",
    description="Retrieve meeting details by ID"
)
async def get_meeting(
    meeting_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Get meeting by ID"""
    try:
        return await meeting_service.get_meeting(meeting_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "",
    response_model=MeetingListResponse,
    summary="List meetings",
    description="Get a paginated list of meetings"
)
async def list_meetings(
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingListResponse:
    """List all meetings"""
    try:
        return await meeting_service.list_meetings(skip=skip, limit=limit)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/organized/by-user",
    response_model=MeetingListResponse,
    summary="List organized meetings",
    description="Get meetings organized by current user"
)
async def list_organized_meetings(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingListResponse:
    """List meetings organized by current user"""
    try:
        # TODO: Get actual organizer_id from auth
        return await meeting_service.list_organized_meetings(
            organizer_id="temp_organizer_id",
            status=status,
            skip=skip,
            limit=limit
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/attended/by-member",
    response_model=MeetingListResponse,
    summary="List attended meetings",
    description="Get meetings attended by current user"
)
async def list_attended_meetings(
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingListResponse:
    """List meetings attended by current user"""
    try:
        # TODO: Get actual member_id from auth
        return await meeting_service.list_attended_meetings(
            member_id="temp_member_id",
            skip=skip,
            limit=limit
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/type/{meeting_type}",
    response_model=MeetingListResponse,
    summary="List meetings by type",
    description="Get meetings filtered by type"
)
async def list_meetings_by_type(
    meeting_type: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingListResponse:
    """List meetings by type"""
    try:
        return await meeting_service.list_meetings_by_type(
            meeting_type=meeting_type,
            status=status,
            skip=skip,
            limit=limit
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/upcoming/list",
    response_model=UpcomingMeetingsResponse,
    summary="Get upcoming meetings",
    description="Get upcoming meetings within specified days"
)
async def get_upcoming_meetings(
    days: int = Query(7, ge=1, le=365, description="Look ahead days"),
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> UpcomingMeetingsResponse:
    """Get upcoming meetings"""
    try:
        return await meeting_service.get_upcoming_meetings(days)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/start",
    response_model=MeetingResponse,
    summary="Start meeting",
    description="Start an active meeting"
)
async def start_meeting(
    meeting_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Start meeting"""
    try:
        return await meeting_service.start_meeting(meeting_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/end",
    response_model=MeetingResponse,
    summary="End meeting",
    description="End a meeting"
)
async def end_meeting(
    meeting_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """End meeting"""
    try:
        return await meeting_service.end_meeting(meeting_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/reschedule",
    response_model=MeetingResponse,
    summary="Reschedule meeting",
    description="Reschedule a meeting to a new date/time"
)
async def reschedule_meeting(
    meeting_id: str,
    request: MeetingRescheduleRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Reschedule meeting"""
    try:
        return await meeting_service.reschedule_meeting(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/cancel",
    response_model=MeetingResponse,
    summary="Cancel meeting",
    description="Cancel a meeting"
)
async def cancel_meeting(
    meeting_id: str,
    request: MeetingCancelRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Cancel meeting"""
    try:
        return await meeting_service.cancel_meeting(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Attendee Management

@router.post(
    "/{meeting_id}/attendees",
    response_model=MeetingResponse,
    status_code=201,
    summary="Add attendee",
    description="Add an attendee to the meeting"
)
async def add_attendee(
    meeting_id: str,
    request: AddAttendeeRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Add attendee to meeting"""
    try:
        return await meeting_service.add_attendee(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{meeting_id}/attendees/{member_id}",
    response_model=MeetingResponse,
    summary="Remove attendee",
    description="Remove an attendee from the meeting"
)
async def remove_attendee(
    meeting_id: str,
    member_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Remove attendee from meeting"""
    try:
        return await meeting_service.remove_attendee(meeting_id, member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/attendees/{member_id}/check-in",
    response_model=MeetingResponse,
    summary="Check in attendee",
    description="Check in an attendee to the meeting"
)
async def check_in_attendee(
    meeting_id: str,
    member_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Check in attendee"""
    try:
        return await meeting_service.check_in_attendee(meeting_id, member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/attendees/{member_id}/check-out",
    response_model=MeetingResponse,
    summary="Check out attendee",
    description="Check out an attendee from the meeting"
)
async def check_out_attendee(
    meeting_id: str,
    member_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Check out attendee"""
    try:
        return await meeting_service.check_out_attendee(meeting_id, member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/attendees/{member_id}/mark-attendance",
    response_model=MeetingResponse,
    summary="Mark attendance",
    description="Mark attendance status for an attendee"
)
async def mark_attendance(
    meeting_id: str,
    member_id: str,
    request: MarkAttendanceRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Mark attendance"""
    try:
        return await meeting_service.mark_attendance(meeting_id, member_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{meeting_id}/attendees/list",
    response_model=AttendanceListResponse,
    summary="Get attendance list",
    description="Get attendance list for a meeting"
)
async def get_attendance_list(
    meeting_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> AttendanceListResponse:
    """Get attendance list"""
    try:
        return await meeting_service.get_attendance_list(meeting_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Approval Management

@router.post(
    "/{meeting_id}/approvers",
    response_model=MeetingResponse,
    status_code=201,
    summary="Add approval member",
    description="Add a member who needs to approve the meeting"
)
async def add_approval_member(
    meeting_id: str,
    request: AddApprovalMemberRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Add approval member"""
    try:
        return await meeting_service.add_approval_member(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/approve/{member_id}",
    response_model=MeetingResponse,
    summary="Approve meeting",
    description="Approve the meeting"
)
async def approve_meeting(
    meeting_id: str,
    member_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Approve meeting"""
    try:
        return await meeting_service.approve_meeting(meeting_id, member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/reject/{member_id}",
    response_model=MeetingResponse,
    summary="Reject meeting",
    description="Reject the meeting with reason"
)
async def reject_meeting(
    meeting_id: str,
    member_id: str,
    request: ApprovalActionRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Reject meeting"""
    try:
        return await meeting_service.reject_meeting(meeting_id, member_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{meeting_id}/approvals",
    response_model=MeetingApprovalResponse,
    summary="Get approval details",
    description="Get meeting approval details"
)
async def get_approval_details(
    meeting_id: str,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingApprovalResponse:
    """Get approval details"""
    try:
        return await meeting_service.get_approval_details(meeting_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Meeting Details

@router.post(
    "/{meeting_id}/minutes",
    response_model=MeetingResponse,
    summary="Set meeting minutes",
    description="Set minutes for a completed meeting"
)
async def set_meeting_minutes(
    meeting_id: str,
    request: MeetingMinutesRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Set meeting minutes"""
    try:
        return await meeting_service.set_meeting_minutes(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{meeting_id}/documents",
    response_model=MeetingResponse,
    status_code=201,
    summary="Add document",
    description="Add a document to the meeting"
)
async def add_document(
    meeting_id: str,
    request: AddDocumentRequest,
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingResponse:
    """Add document to meeting"""
    try:
        return await meeting_service.add_document(meeting_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Statistics

@router.get(
    "/statistics/overview",
    response_model=MeetingStatisticsResponse,
    summary="Get statistics",
    description="Get overall meeting statistics"
)
async def get_statistics(
    meeting_service: MeetingApplicationService = Depends(get_meeting_service)
) -> MeetingStatisticsResponse:
    """Get meeting statistics"""
    try:
        return await meeting_service.get_statistics()
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
