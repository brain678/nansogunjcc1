# app/presentation/api/v1/routers/members/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.application.services.member_application_service import MemberApplicationService
from app.application.dtos.member_dto import (
    MemberRegisterRequest,
    MemberUpdateProfileRequest,
    MemberRenewRequest,
    MemberUpgradeTierRequest,
    MemberResponse,
    MemberListResponse,
    MemberStatisticsResponse,
    MembershipExpiringResponse,
    MemberActivityResponse,
    MembershipActionRequest,
)
from app.common.exceptions import AppException
from app.presentation.api.v1.dependencies import get_current_user_id, get_current_user, require_any_permission, require_permission


# Router for member endpoints
router = APIRouter(
    prefix="/api/v1/members",
    tags=["members"]
)


# Dependency to get member service (would be injected from DI container)
async def get_member_service() -> MemberApplicationService:
    """Get member application service"""
    from app.domain.services.member_service import MemberService
    from app.infrastructure.persistence.member_repository import MemberRepository
    
    repository = MemberRepository()
    domain_service = MemberService(repository)
    return MemberApplicationService(domain_service)


@router.post(
    "/register",
    response_model=MemberResponse,
    status_code=201,
    summary="Register new member",
    description="Register a new member in the system"
)
async def register_member(
    request: MemberRegisterRequest,
    user_id: str = Depends(get_current_user_id),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Register a new member"""
    try:
        return await member_service.register_member(
            user_id=user_id,
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{member_id}",
    status_code=204,
    summary="Delete member",
    description="Soft-delete a member from the system"
)
async def delete_member(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
):
    """Delete (soft) a member"""
    try:
        success = await member_service.member_service.member_repository.delete(member_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Member {member_id} not found")
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pending",
    response_model=MemberListResponse,
    summary="List pending membership requests",
    description="Get a paginated list of pending membership applications"
)
async def list_pending_memberships(
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberListResponse:
    """List pending membership requests"""
    require_any_permission(
        current_user,
        [
            ("members", "read", "any"),
            ("members", "approve", "any"),
            ("members", "reject", "any"),
        ]
    )
    try:
        return await member_service.get_pending_memberships(skip=skip, limit=limit)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get member by ID",
    description="Retrieve a member's details by their ID"
)
async def get_member(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Get member by ID"""
    try:
        return await member_service.get_member(member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/by-membership/{membership_number}",
    response_model=MemberResponse,
    summary="Get member by membership number",
    description="Retrieve a member's details by their membership number"
)
async def get_member_by_membership_number(
    membership_number: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Get member by membership number"""
    try:
        return await member_service.get_member_by_membership_number(membership_number)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{member_id}/profile",
    response_model=MemberResponse,
    summary="Update member profile",
    description="Update a member's profile information"
)
async def update_member_profile(
    member_id: str,
    request: MemberUpdateProfileRequest,
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Update member profile"""
    try:
        member = await member_service.member_service.member_repository.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        if str(current_user.id) != str(member.user_id):
            if "admin" not in getattr(current_user, "roles", []):
                raise HTTPException(status_code=403, detail="Forbidden")

        return await member_service.update_profile(member_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/approve",
    response_model=MemberResponse,
    summary="Approve pending membership",
    description="Approve a pending membership application"
)
async def approve_member(
    member_id: str,
    request: MembershipActionRequest,
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Approve a pending membership"""
    require_permission(current_user, "members", "approve", "any")
    approver_role = current_user.roles[0] if getattr(current_user, "roles", None) else None
    try:
        return await member_service.approve_member(
            member_id=member_id,
            approver_id=str(current_user.id),
            approver_role=approver_role,
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/reject",
    response_model=MemberResponse,
    summary="Reject pending membership",
    description="Reject a pending membership application"
)
async def reject_member(
    member_id: str,
    request: MembershipActionRequest,
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Reject a pending membership"""
    require_permission(current_user, "members", "reject", "any")
    approver_role = current_user.roles[0] if getattr(current_user, "roles", None) else None
    try:
        return await member_service.reject_member(
            member_id=member_id,
            approver_id=str(current_user.id),
            approver_role=approver_role,
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/reactivate",
    response_model=MemberResponse,
    summary="Reactivate membership",
    description="Reactivate a suspended or inactive membership"
)
async def reactivate_member(
    member_id: str,
    request: MembershipActionRequest,
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Reactivate membership"""
    require_permission(current_user, "members", "update", "any")
    approver_role = current_user.roles[0] if getattr(current_user, "roles", None) else None
    try:
        return await member_service.reactivate_member(
            member_id=member_id,
            approver_id=str(current_user.id),
            approver_role=approver_role,
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/renew",
    response_model=MemberResponse,
    summary="Renew membership",
    description="Renew a member's membership"
)
async def renew_membership(
    member_id: str,
    request: MemberRenewRequest,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Renew membership"""
    try:
        return await member_service.renew_membership(member_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/upgrade-tier",
    response_model=MemberResponse,
    summary="Upgrade membership tier",
    description="Upgrade a member's membership tier"
)
async def upgrade_membership_tier(
    member_id: str,
    request: MemberUpgradeTierRequest,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Upgrade membership tier"""
    try:
        return await member_service.upgrade_tier(member_id, request)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/suspend",
    response_model=MemberResponse,
    summary="Suspend member",
    description="Suspend a member's account"
)
async def suspend_member(
    member_id: str,
    request: MembershipActionRequest,
    current_user = Depends(get_current_user),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Suspend member"""
    require_permission(current_user, "members", "update", "any")
    approver_role = current_user.roles[0] if getattr(current_user, "roles", None) else None
    try:
        return await member_service.suspend_member(
            member_id=member_id,
            approver_id=str(current_user.id),
            approver_role=approver_role,
            request=request
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/activate",
    response_model=MemberResponse,
    summary="Activate member",
    description="Activate a suspended member's account"
)
async def activate_member(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Activate member"""
    try:
        return await member_service.activate_member(member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/deactivate",
    response_model=MemberResponse,
    summary="Deactivate membership",
    description="Mark a member as inactive"
)
async def deactivate_member(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Deactivate member"""
    try:
        return await member_service.deactivate_member(member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{member_id}/alumni",
    response_model=MemberResponse,
    summary="Move to alumni",
    description="Mark a member as alumni"
)
async def mark_member_as_alumni(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberResponse:
    """Mark member as alumni"""
    try:
        return await member_service.mark_as_alumni(member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "",
    response_model=MemberListResponse,
    summary="List members",
    description="Get a paginated list of members with optional filters"
)
async def list_members(
    status: Optional[str] = Query(None, description="Filter by membership status"),
    membership_type: Optional[str] = Query(None, description="Filter by membership type"),
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberListResponse:
    """List members"""
    try:
        return await member_service.list_members(
            status=status,
            membership_type=membership_type,
            skip=skip,
            limit=limit
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/expiring/list",
    response_model=list[MembershipExpiringResponse],
    summary="Get expiring memberships",
    description="Get a list of members whose memberships are expiring soon"
)
async def get_expiring_memberships(
    days: int = Query(30, ge=1, le=365, description="Look ahead days"),
    member_service: MemberApplicationService = Depends(get_member_service)
) -> list[MembershipExpiringResponse]:
    """Get expiring memberships"""
    try:
        return await member_service.get_expiring_memberships(days)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{member_id}/activity",
    response_model=MemberActivityResponse,
    summary="Get member activity",
    description="Get member's activity statistics and contribution details"
)
async def get_member_activity(
    member_id: str,
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberActivityResponse:
    """Get member activity"""
    try:
        return await member_service.get_member_activity(member_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/statistics/overview",
    response_model=MemberStatisticsResponse,
    summary="Get member statistics",
    description="Get overall member statistics and analytics"
)
async def get_statistics(
    member_service: MemberApplicationService = Depends(get_member_service)
) -> MemberStatisticsResponse:
    """Get member statistics"""
    try:
        return await member_service.get_statistics()
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
