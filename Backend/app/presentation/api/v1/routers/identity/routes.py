"""
API Routes for Digital Identity and QR System
Endpoints for ID card generation, verification, and check-in
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from app.presentation.api.v1.dependencies import get_current_user_id
from app.application.services.identity_application_service import (
    IdentityApplicationService, QRApplicationService
)
from app.domain.services.identity_service import IdentityService, QRService
from app.infrastructure.persistence.identity_repository import (
    DigitalIdentityRepository, QRVerificationRecordRepository,
    MeetingQRTokenRepository, ActivityQRTokenRepository, AttendanceRecordRepository
)
from app.infrastructure.persistence.user_repository import UserRepository
from app.infrastructure.persistence.member_repository import MemberRepository
from app.application.dtos.identity_dto import (
    CreateIdentityRequest, IdentityResponse, DigitalCardResponse,
    CardStatusResponse, RegenerateQRResponse, DisableCardResponse,
    ActivateCardResponse, VerifyQRRequest, VerifyQRResponse,
    CreateMeetingQRRequest, MeetingQRResponse, CheckInMeetingRequest,
    CheckInMeetingResponse, CreateActivityQRRequest, ActivityQRResponse,
    CheckInActivityRequest, CheckInActivityResponse
)
from app.common.exceptions import AppException


# Router for identity endpoints
router = APIRouter(
    prefix="/api/v1/identity",
    tags=["identity"]
)

# Router for QR endpoints
qr_router = APIRouter(
    prefix="/api/v1/qr",
    tags=["qr"]
)


# Dependency to get identity application service
async def get_identity_app_service() -> IdentityApplicationService:
    """Get identity application service"""
    identity_repo = DigitalIdentityRepository()
    identity_service = IdentityService(identity_repo)
    return IdentityApplicationService(identity_service)


# Dependency to get QR application service
async def get_qr_app_service() -> QRApplicationService:
    """Get QR application service"""
    identity_repo = DigitalIdentityRepository()
    verification_repo = QRVerificationRecordRepository()
    meeting_qr_repo = MeetingQRTokenRepository()
    activity_qr_repo = ActivityQRTokenRepository()
    attendance_repo = AttendanceRecordRepository()
    
    qr_service = QRService(
        identity_repo,
        verification_repo,
        meeting_qr_repo,
        activity_qr_repo,
        attendance_repo
    )
    return QRApplicationService(qr_service)


# ==================== IDENTITY ENDPOINTS ====================

@router.post(
    "/initialize",
    response_model=IdentityResponse,
    summary="Initialize digital identity",
    description="Create a digital identity for the current user",
    status_code=201
)
async def initialize_identity(
    request: CreateIdentityRequest,
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> IdentityResponse:
    """Initialize digital identity for user"""
    try:
        user = await UserRepository().get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        member = await MemberRepository().find_by_user_id(user_id)
        institution = member.organization if member and member.organization else request.institution
        profile_photo_url = user.profile_photo_url or request.profile_photo_url

        identity_data = await service.create_identity_for_user(
            user_id=user_id,
            role=request.role,
            first_name=user.first_name,
            last_name=user.last_name,
            email=str(user.email),
            institution=institution,
            chapter=request.chapter,
            profile_photo_url=profile_photo_url
        )
        return IdentityResponse(**identity_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/card",
    response_model=DigitalCardResponse,
    summary="Get digital ID card",
    description="Get the user's digital identity card"
)
async def get_digital_card(
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> DigitalCardResponse:
    """Get user's digital ID card"""
    try:
        card_data = await service.get_digital_card(user_id)
        return DigitalCardResponse(**card_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/card/status",
    response_model=CardStatusResponse,
    summary="Get card status",
    description="Get current status of the user's ID card"
)
async def get_card_status(
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> CardStatusResponse:
    """Get card status"""
    try:
        status_data = await service.get_card_status(user_id)
        return CardStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/qr/regenerate",
    response_model=RegenerateQRResponse,
    summary="Regenerate QR code",
    description="Generate a new QR code for the user"
)
async def regenerate_qr(
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> RegenerateQRResponse:
    """Regenerate QR code"""
    try:
        qr_data = await service.regenerate_qr_code(user_id)
        return RegenerateQRResponse(**qr_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/card/disable",
    response_model=DisableCardResponse,
    summary="Disable ID card",
    description="Disable the user's digital ID card"
)
async def disable_card(
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> DisableCardResponse:
    """Disable ID card"""
    try:
        disable_data = await service.disable_card(user_id)
        return DisableCardResponse(**disable_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/card/activate",
    response_model=ActivateCardResponse,
    summary="Activate ID card",
    description="Activate the user's digital ID card"
)
async def activate_card(
    user_id: str = Depends(get_current_user_id),
    service: IdentityApplicationService = Depends(get_identity_app_service)
) -> ActivateCardResponse:
    """Activate ID card"""
    try:
        activate_data = await service.activate_card(user_id)
        return ActivateCardResponse(**activate_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== QR VERIFICATION ENDPOINTS ====================

@qr_router.post(
    "/verify",
    response_model=VerifyQRResponse,
    summary="Verify QR token",
    description="Verify a member via their QR token",
    status_code=200
)
async def verify_qr(
    request: VerifyQRRequest,
    http_request: Request,
    service: QRApplicationService = Depends(get_qr_app_service)
) -> VerifyQRResponse:
    """Verify member via QR token"""
    try:
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        
        verification_data = await service.verify_member_qr(
            qr_token=request.qr_token,
            ip_address=ip_address
        )
        return VerifyQRResponse(**verification_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== MEETING QR ENDPOINTS ====================

@qr_router.post(
    "/meeting/create",
    response_model=MeetingQRResponse,
    summary="Create meeting QR code",
    description="Create a QR code for meeting attendance",
    status_code=201
)
async def create_meeting_qr(
    request: CreateMeetingQRRequest,
    user_id: str = Depends(get_current_user_id),
    service: QRApplicationService = Depends(get_qr_app_service)
) -> MeetingQRResponse:
    """Create QR code for meeting"""
    try:
        qr_data = await service.create_meeting_qr(request.meeting_id)
        return MeetingQRResponse(**qr_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@qr_router.post(
    "/meeting/check-in",
    response_model=CheckInMeetingResponse,
    summary="Check-in to meeting via QR",
    description="Check-in a member to a meeting using QR code",
    status_code=200
)
async def check_in_meeting(
    request: CheckInMeetingRequest,
    user_id: str = Depends(get_current_user_id),
    service: QRApplicationService = Depends(get_qr_app_service)
) -> CheckInMeetingResponse:
    """Check-in to meeting"""
    try:
        checkin_data = await service.check_in_meeting(
            qr_token=request.qr_token,
            event_id=request.event_id,
            user_id=user_id
        )
        return CheckInMeetingResponse(**checkin_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ACTIVITY QR ENDPOINTS ====================

@qr_router.post(
    "/activity/create",
    response_model=ActivityQRResponse,
    summary="Create activity QR code",
    description="Create a QR code for activity/event check-in",
    status_code=201
)
async def create_activity_qr(
    request: CreateActivityQRRequest,
    user_id: str = Depends(get_current_user_id),
    service: QRApplicationService = Depends(get_qr_app_service)
) -> ActivityQRResponse:
    """Create QR code for activity"""
    try:
        qr_data = await service.create_activity_qr(
            activity_id=request.activity_id,
            activity_name=request.activity_name
        )
        return ActivityQRResponse(**qr_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@qr_router.post(
    "/activity/check-in",
    response_model=CheckInActivityResponse,
    summary="Check-in to activity via QR",
    description="Check-in a member to an activity using QR code",
    status_code=200
)
async def check_in_activity(
    request: CheckInActivityRequest,
    user_id: str = Depends(get_current_user_id),
    service: QRApplicationService = Depends(get_qr_app_service)
) -> CheckInActivityResponse:
    """Check-in to activity"""
    try:
        checkin_data = await service.check_in_activity(
            qr_token=request.qr_token,
            event_id=request.event_id,
            user_id=user_id
        )
        return CheckInActivityResponse(**checkin_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
