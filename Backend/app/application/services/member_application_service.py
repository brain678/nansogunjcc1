# app/application/services/member_application_service.py

from datetime import datetime
from typing import Optional, List
from app.domain.services.member_service import MemberService
from app.application.dtos.member_dto import (
    MemberRegisterRequest, MemberResubmitRequest, MemberUpdateProfileRequest, MemberRenewRequest,
    MemberUpgradeTierRequest, MemberResponse, MemberListResponse,
    MemberStatisticsResponse, MembershipExpiringResponse, MemberActivityResponse,
    MembershipActionRequest, MembershipAuditEntryResponse, AddressResponse
)
from app.domain.models.member import Member, MembershipStatus, MembershipType
from app.domain.models.digital_identity import UserRole
from app.domain.services.identity_service import IdentityService
from app.infrastructure.persistence.identity_repository import DigitalIdentityRepository
from app.common.exceptions import ValidationError, NotFoundError
from app.common.models.value_objects import Email


class MemberApplicationService:
    """Application service for member operations"""

    def _apply_member_status(self, member: Member, status: MembershipStatus) -> Member:
        """Ensure the returned member object reflects the requested status."""
        if hasattr(member, "status"):
            transition_method = {
                MembershipStatus.ACTIVE: "activate_membership",
                MembershipStatus.INACTIVE: "deactivate_membership",
                MembershipStatus.SUSPENDED: "suspend_membership",
                MembershipStatus.RESIGNED: "resign_membership",
            }.get(status)
            if transition_method and hasattr(member, transition_method):
                getattr(member, transition_method)()
            else:
                member.status = status
                if hasattr(member, "updated_at"):
                    member.updated_at = datetime.utcnow()
        return member
    
    def __init__(self, member_service: MemberService, identity_service: Optional[IdentityService] = None):
        """
        Initialize member application service
        
        Args:
            member_service: Domain member service
            identity_service: Optional identity service for issuing cards on approval
        """
        self.member_service = member_service
        self.identity_service = identity_service or IdentityService(DigitalIdentityRepository())
    
    async def register_member(
        self,
        user_id: str,
        request: MemberRegisterRequest
    ) -> MemberResponse:
        """
        Register a new member
        
        Args:
            user_id: Associated user ID
            request: Registration request
            
        Returns:
            Member response DTO
        """
        # Convert email string to Email value object
        email = Email(value=request.email)
        
        member = await self.member_service.register_member(
            user_id=user_id,
            email=email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            address=request.address,
            notes=request.notes,
            date_of_birth=request.date_of_birth,
            membership_type=request.membership_type,
            membership_tier=request.membership_tier,
            expiry_months=request.expiry_months
        )
        
        return self._member_to_response(member)
    
    async def get_member(self, member_id: str) -> MemberResponse:
        """
        Get member by ID
        
        Args:
            member_id: Member ID
            
        Returns:
            Member response DTO
        """
        member = await self.member_service.member_repository.get_by_id(member_id)
        if not member:
            raise ValidationError(f"Member not found: {member_id}")
        
        return self._member_to_response(member)
    
    async def get_member_by_user_id(self, user_id: str) -> MemberResponse:
        """
        Get member by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Member response DTO
        """
        member = await self.member_service.get_member_by_user_id(user_id)
        return self._member_to_response(member)
    
    async def get_member_by_membership_number(self, membership_number: str) -> MemberResponse:
        """
        Get member by membership number
        
        Args:
            membership_number: Membership number
            
        Returns:
            Member response DTO
        """
        member = await self.member_service.get_member_by_membership_number(membership_number)
        return self._member_to_response(member)

    async def get_pending_memberships(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> MemberListResponse:
        """
        Get pending membership requests
        """
        members = await self.member_service.get_pending_memberships(skip=skip, limit=limit)
        total = await self.member_service.member_repository.count(status=MembershipStatus.PENDING)
        return MemberListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._member_to_response(m) for m in members]
        )

    async def approve_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str],
        request: MembershipActionRequest
    ) -> MemberResponse:
        """Approve a pending membership request"""
        member = await self.member_service.approve_member(
            member_id=member_id,
            approver_id=approver_id,
            approver_role=approver_role,
            comment=request.comment
        )

        try:
            identity = await self._issue_identity_for_member(member)
            if member.audit_log:
                member.audit_log[-1].metadata.update({
                    "membership_id": identity.membership_id,
                    "qr_token": identity.qr_token,
                    "card_status": identity.card_status.value
                })
                await self.member_service.member_repository.save(member)
        except ValidationError as exc:
            if "already exists" not in str(exc).lower():
                raise

        return self._member_to_response(member)

    async def _issue_identity_for_member(self, member: Member):
        """Create digital identity for an approved member."""
        return await self.identity_service.create_identity(
            user_id=member.user_id,
            role=UserRole.MEMBER,
            first_name=member.first_name,
            last_name=member.last_name,
            email=str(member.email),
            institution=member.organization or "Not Specified",
            chapter="General",
            profile_photo_url=member.profile_photo_url
        )

    async def _ensure_identity_for_member(self, member: Member):
        """Create or refresh the member's identity so the QR token stays available after reactivation."""
        try:
            return await self.identity_service.regenerate_qr_token(member.user_id)
        except NotFoundError:
            return await self._issue_identity_for_member(member)

    async def reject_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str],
        request: MembershipActionRequest
    ) -> MemberResponse:
        """Reject a pending membership request"""
        member = await self.member_service.reject_member(
            member_id=member_id,
            approver_id=approver_id,
            approver_role=approver_role,
            comment=request.comment
        )
        return self._member_to_response(member)

    async def resubmit_member(
        self,
        member_id: str,
        request: MemberResubmitRequest
    ) -> MemberResponse:
        """Resubmit a rejected membership application"""
        email = Email(value=request.email)
        member = await self.member_service.resubmit_member(
            member_id=member_id,
            email=email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            address=request.address,
            notes=request.notes,
            date_of_birth=request.date_of_birth,
            membership_type=request.membership_type,
            membership_tier=request.membership_tier,
            expiry_months=request.expiry_months,
            comment=request.comment
        )
        return self._member_to_response(member)

    async def reactivate_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str],
        request: MembershipActionRequest
    ) -> MemberResponse:
        """Reactivate a suspended membership"""
        member = await self.member_service.reactivate_member(
            member_id=member_id,
            approver_id=approver_id,
            approver_role=approver_role,
            comment=request.comment
        )
        member = self._apply_member_status(member, MembershipStatus.ACTIVE)
        try:
            identity = await self._ensure_identity_for_member(member)
            if member.audit_log:
                member.audit_log[-1].metadata.update({
                    "membership_id": identity.membership_id,
                    "qr_token": identity.qr_token,
                    "card_status": identity.card_status.value,
                })
                await self.member_service.member_repository.save(member)
        except ValidationError as exc:
            if "already exists" not in str(exc).lower():
                raise
        return self._member_to_response(member)

    async def update_profile(
        self,
        member_id: str,
        request: MemberUpdateProfileRequest
    ) -> MemberResponse:
        """
        Update member profile
        
        Args:
            member_id: Member ID
            request: Update request
            
        Returns:
            Updated member response DTO
        """
        update_data = request.dict(exclude_unset=True)
        member = await self.member_service.update_member_profile(member_id, **update_data)
        return self._member_to_response(member)
    
    async def renew_membership(
        self,
        member_id: str,
        request: MemberRenewRequest
    ) -> MemberResponse:
        """
        Renew member's membership
        
        Args:
            member_id: Member ID
            request: Renewal request
            
        Returns:
            Renewed member response DTO
        """
        member = await self.member_service.renew_membership(
            member_id,
            months=request.months
        )
        return self._member_to_response(member)
    
    async def upgrade_tier(
        self,
        member_id: str,
        request: MemberUpgradeTierRequest
    ) -> MemberResponse:
        """
        Upgrade membership tier
        
        Args:
            member_id: Member ID
            request: Upgrade request
            
        Returns:
            Updated member response DTO
        """
        member = await self.member_service.upgrade_membership_tier(
            member_id,
            new_tier=request.new_tier
        )
        return self._member_to_response(member)
    
    async def suspend_member(self, member_id: str, approver_id: str, approver_role: Optional[str], request: MembershipActionRequest) -> MemberResponse:
        """
        Suspend member
        
        Args:
            member_id: Member ID
            approver_id: ID of user performing suspension
            approver_role: Role of the approver
            request: MembershipActionRequest (may include comment)
            
        Returns:
            Suspended member response DTO
        """
        member = await self.member_service.suspend_member(
            member_id=member_id,
            approver_id=approver_id,
            approver_role=approver_role,
            comment=request.comment
        )
        member = self._apply_member_status(member, MembershipStatus.SUSPENDED)
        return self._member_to_response(member)

    async def deactivate_member(self, member_id: str) -> MemberResponse:
        """Mark a member as inactive."""
        member = await self.member_service.deactivate_member(member_id)
        member = self._apply_member_status(member, MembershipStatus.INACTIVE)
        return self._member_to_response(member)

    async def mark_as_alumni(self, member_id: str) -> MemberResponse:
        """Mark a member as alumni/resigned."""
        member = await self.member_service.resign_member(member_id)
        member = self._apply_member_status(member, MembershipStatus.RESIGNED)
        return self._member_to_response(member)
    
    async def activate_member(self, member_id: str) -> MemberResponse:
        """
        Activate member
        
        Args:
            member_id: Member ID
            
        Returns:
            Activated member response DTO
        """
        member = await self.member_service.activate_member(member_id)
        member = self._apply_member_status(member, MembershipStatus.ACTIVE)
        try:
            identity = await self._ensure_identity_for_member(member)
            if member.audit_log:
                member.audit_log[-1].metadata.update({
                    "membership_id": identity.membership_id,
                    "qr_token": identity.qr_token,
                    "card_status": identity.card_status.value,
                })
                await self.member_service.member_repository.save(member)
        except ValidationError as exc:
            if "already exists" not in str(exc).lower():
                raise
        return self._member_to_response(member)
    
    async def list_members(
        self,
        status: Optional[str] = None,
        membership_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> MemberListResponse:
        """
        List members with pagination
        
        Args:
            status: Filter by status
            membership_type: Filter by type
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List response DTO
        """
        # Convert strings to enums if provided
        status_enum = MembershipStatus(status) if status else None
        type_enum = MembershipType(membership_type) if membership_type else None
        
        members = await self.member_service.list_members(
            status=status_enum,
            membership_type=type_enum,
            skip=skip,
            limit=limit
        )
        
        total = await self.member_service.member_repository.count(status=status_enum)
        
        return MemberListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[self._member_to_response(m) for m in members]
        )
    
    async def get_expiring_memberships(self, days: int = 30) -> List[MembershipExpiringResponse]:
        """
        Get members with expiring memberships
        
        Args:
            days: Look ahead days
            
        Returns:
            List of expiring membership responses
        """
        members = await self.member_service.get_expiring_memberships(days)
        
        return [
            MembershipExpiringResponse(
                member_id=str(m.id),
                email=str(m.email),
                full_name=m.full_name,
                membership_number=m.membership_number,
                expiry_date=m.membership_expiry_date,
                days_until_expiry=m.days_until_expiry or 0
            )
            for m in members
        ]
    
    async def get_member_activity(self, member_id: str) -> MemberActivityResponse:
        """
        Get member activity statistics
        
        Args:
            member_id: Member ID
            
        Returns:
            Member activity response DTO
        """
        member = await self.member_service.member_repository.get_by_id(member_id)
        if not member:
            raise ValidationError(f"Member not found: {member_id}")
        
        return MemberActivityResponse(
            member_id=str(member.id),
            meetings_attended=member.meetings_attended,
            activities_participated=member.activities_participated,
            documents_contributed=member.documents_contributed,
            total_contribution_hours=member.total_contribution_hours,
            last_active_at=member.last_active_at
        )
    
    async def get_statistics(self) -> MemberStatisticsResponse:
        """
        Get member statistics
        
        Returns:
            Member statistics response DTO
        """
        total = await self.member_service.member_repository.count()
        active = await self.member_service.member_repository.count(MembershipStatus.ACTIVE)
        inactive = await self.member_service.member_repository.count(MembershipStatus.INACTIVE)
        suspended = await self.member_service.member_repository.count(MembershipStatus.SUSPENDED)
        
        # Get members by type and tier
        all_members = await self.member_service.list_members(skip=0, limit=1000)
        
        members_by_type = {}
        members_by_tier = {}
        total_hours = 0.0
        total_meetings = 0
        
        for member in all_members:
            # Count by type
            type_name = member.membership_type.value
            members_by_type[type_name] = members_by_type.get(type_name, 0) + 1
            
            # Count by tier
            tier_name = member.membership_tier.value
            members_by_tier[tier_name] = members_by_tier.get(tier_name, 0) + 1
            
            # Sum statistics
            total_hours += member.total_contribution_hours
            total_meetings += member.meetings_attended
        
        avg_meetings = total_meetings / total if total > 0 else 0
        
        return MemberStatisticsResponse(
            total_members=total,
            active_members=active,
            inactive_members=inactive,
            suspended_members=suspended,
            members_by_type=members_by_type,
            members_by_tier=members_by_tier,
            total_contribution_hours=total_hours,
            average_meetings_attended=avg_meetings
        )
    
    def _get_identity_metadata(self, member) -> dict:
        """Extract identity metadata from the latest audit entry for the member."""
        if not getattr(member, "audit_log", None):
            return {}
        last_entry = member.audit_log[-1]
        metadata = getattr(last_entry, "metadata", None) or {}
        return {
            "membership_id": metadata.get("membership_id"),
            "qr_token": metadata.get("qr_token"),
            "card_status": metadata.get("card_status")
        }

    def _member_to_response(self, member) -> MemberResponse:
        """Convert member to response DTO"""
        identity_metadata = self._get_identity_metadata(member)
        audit_log = getattr(member, "audit_log", None) or []

        return MemberResponse(
            id=str(getattr(member, "id", "")),
            user_id=getattr(member, "user_id", None),
            email=str(getattr(member, "email", "")),
            phone=str(getattr(member, "phone", None)) if getattr(member, "phone", None) else None,
            first_name=getattr(member, "first_name", None),
            last_name=getattr(member, "last_name", None),
            date_of_birth=getattr(member, "date_of_birth", None),
            full_name=getattr(member, "full_name", None) or " ".join(filter(None, [getattr(member, "first_name", None), getattr(member, "last_name", None)])),
            membership_number=getattr(member, "membership_number", None),
            membership_type=getattr(member, "membership_type", None),
            membership_tier=getattr(member, "membership_tier", None),
            status=getattr(member, "status", None),
            joined_date=getattr(member, "joined_date", None),
            membership_expiry_date=getattr(member, "membership_expiry_date", None),
            requested_expiry_months=getattr(member, "requested_expiry_months", 0),
            submitted_at=getattr(member, "submitted_at", None),
            approved_at=getattr(member, "approved_at", None),
            rejected_at=getattr(member, "rejected_at", None),
            approver_id=getattr(member, "approver_id", None),
            approver_role=getattr(member, "approver_role", None),
            review_comments=getattr(member, "review_comments", None),
            audit_log=[
                MembershipAuditEntryResponse(
                    timestamp=getattr(entry, "timestamp", None),
                    action=getattr(getattr(entry, "action", None), "value", getattr(entry, "action", None)),
                    performed_by_user_id=getattr(entry, "performed_by_user_id", None),
                    performed_by_role=getattr(entry, "performed_by_role", None),
                    comment=getattr(entry, "comment", None),
                    resulting_status=getattr(entry, "resulting_status", None),
                    metadata=getattr(entry, "metadata", None) or {}
                )
                for entry in audit_log
            ],
            is_membership_expired=getattr(member, "is_membership_expired", False),
            days_until_expiry=getattr(member, "days_until_expiry", None),
            bio=getattr(member, "bio", None),
            profile_photo_url=getattr(member, "profile_photo_url", None),
            document_ids=[str(document_id) for document_id in getattr(member, "document_ids", [])],
            address=getattr(member, "address", None),
            notes=getattr(member, "notes", None),
            organization=getattr(member, "organization", None),
            position=getattr(member, "position", None),
            department=getattr(member, "department", None),
            addresses=[
                AddressResponse(
                    street=getattr(address, "street", None),
                    city=getattr(address, "city", None),
                    state=getattr(address, "state", None),
                    zip_code=getattr(address, "zip_code", None),
                    country=getattr(address, "country", None),
                )
                for address in getattr(member, "addresses", [])
            ],
            emergency_contact_name=getattr(member, "emergency_contact_name", None),
            emergency_contact_phone=str(getattr(member, "emergency_contact_phone", None)) if getattr(member, "emergency_contact_phone", None) else None,
            newsletter_subscription=getattr(member, "newsletter_subscription", True),
            event_notifications=getattr(member, "event_notifications", True),
            communication_language=getattr(member, "communication_language", "en"),
            last_active_at=getattr(member, "last_active_at", None),
            meetings_attended=getattr(member, "meetings_attended", 0),
            activities_participated=getattr(member, "activities_participated", 0),
            documents_contributed=getattr(member, "documents_contributed", 0),
            total_contribution_hours=getattr(member, "total_contribution_hours", 0.0),
            membership_id=identity_metadata.get("membership_id"),
            qr_token=identity_metadata.get("qr_token"),
            card_status=identity_metadata.get("card_status"),
            created_at=getattr(member, "created_at", None),
            updated_at=getattr(member, "updated_at", None)
        )
