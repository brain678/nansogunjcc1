# app/domain/services/member_service.py

from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.models.member import (
    Member,
    MembershipStatus,
    MembershipType,
    MembershipTier,
    MembershipAuditAction,
    MembershipAuditEntry
)
from app.common.exceptions import (
    EntityNotFoundError, ValidationError, DuplicateResourceError
)
from app.common.models.value_objects import Email, Phone


class MemberService:
    """Domain service for member business logic"""
    
    def __init__(self, member_repository):
        """
        Initialize member service
        
        Args:
            member_repository: Member repository for data access
        """
        self.member_repository = member_repository
    
    async def register_member(
        self,
        user_id: str,
        email: Email,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        membership_type: MembershipType = MembershipType.FULL,
        membership_tier: MembershipTier = MembershipTier.STANDARD,
        expiry_months: int = 12
    ) -> Member:
        """
        Register a new member
        
        Args:
            user_id: Associated user ID
            email: Member email (Email value object)
            first_name: First name
            last_name: Last name
            membership_type: Type of membership
            membership_tier: Membership tier
            expiry_months: Months until membership expires
            
        Returns:
            Created Member
        """
        # Check if member already exists
        existing = await self.member_repository.find_by_user_id(user_id)
        if existing:
            raise DuplicateResourceError(f"Member already exists for user {user_id}")
        
        # Generate membership number
        membership_number = await self._generate_membership_number()
        
        # Create member request in pending status
        member = Member(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=Phone(value=phone) if phone else None,
            address=address,
            notes=notes,
            date_of_birth=date_of_birth,
            membership_number=membership_number,
            membership_type=membership_type,
            membership_tier=membership_tier,
            joined_date=datetime.utcnow(),
            membership_expiry_date=None,
            requested_expiry_months=expiry_months,
            status=MembershipStatus.PENDING,
            submitted_at=datetime.utcnow()
        )

        audit_entry = MembershipAuditEntry(
            action=MembershipAuditAction.REQUESTED,
            performed_by_user_id=user_id,
            performed_by_role=None,
            comment="Membership registration requested",
            resulting_status=MembershipStatus.PENDING
        )
        member.audit_log.append(audit_entry)
        
        return await self.member_repository.save(member)
    
    async def _append_audit_entry(
        self,
        member: Member,
        action: MembershipAuditAction,
        performed_by_user_id: Optional[str],
        performed_by_role: Optional[str],
        comment: Optional[str],
        resulting_status: MembershipStatus,
        metadata: Optional[dict] = None
    ) -> None:
        entry = MembershipAuditEntry(
            action=action,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            comment=comment,
            resulting_status=resulting_status,
            metadata=metadata or {}
        )
        member.audit_log.append(entry)

    async def approve_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Member:
        """Approve a pending membership request"""
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        if member.status != MembershipStatus.PENDING:
            raise ValidationError("Only pending memberships can be approved")

        member.status = MembershipStatus.ACTIVE
        member.approved_at = datetime.utcnow()
        member.approver_id = approver_id
        member.approver_role = approver_role
        member.review_comments = comment
        member.updated_at = datetime.utcnow()

        if not member.membership_expiry_date or member.is_membership_expired:
            member.membership_expiry_date = datetime.utcnow() + timedelta(days=30 * member.requested_expiry_months)

        await self._append_audit_entry(
            member,
            MembershipAuditAction.APPROVED,
            approver_id,
            approver_role,
            comment,
            MembershipStatus.ACTIVE
        )
        return await self.member_repository.save(member)

    async def reject_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Member:
        """Reject a pending membership request"""
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        if member.status != MembershipStatus.PENDING:
            raise ValidationError("Only pending memberships can be rejected")
        if not comment or not comment.strip():
            raise ValidationError("A rejection reason is required")

        member.status = MembershipStatus.REJECTED
        member.rejected_at = datetime.utcnow()
        member.approver_id = approver_id
        member.approver_role = approver_role
        member.review_comments = comment.strip()
        member.updated_at = datetime.utcnow()

        await self._append_audit_entry(
            member,
            MembershipAuditAction.REJECTED,
            approver_id,
            approver_role,
            comment.strip(),
            MembershipStatus.REJECTED
        )
        return await self.member_repository.save(member)

    async def resubmit_member(
        self,
        member_id: str,
        email: Email,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        membership_type: MembershipType = MembershipType.FULL,
        membership_tier: MembershipTier = MembershipTier.STANDARD,
        expiry_months: int = 12,
        comment: Optional[str] = None
    ) -> Member:
        """Resubmit a rejected membership application"""
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        if member.status != MembershipStatus.REJECTED:
            raise ValidationError("Only rejected memberships can be resubmitted")

        member.email = email
        member.first_name = first_name
        member.last_name = last_name
        member.phone = Phone(value=phone) if phone else None
        member.address = address
        member.notes = notes
        member.date_of_birth = date_of_birth
        member.membership_type = membership_type
        member.membership_tier = membership_tier
        member.requested_expiry_months = expiry_months

        member.status = MembershipStatus.PENDING
        member.approved_at = None
        member.rejected_at = None
        member.approver_id = None
        member.approver_role = None
        member.review_comments = None
        member.updated_at = datetime.utcnow()
        member.submitted_at = datetime.utcnow()

        await self._append_audit_entry(
            member,
            MembershipAuditAction.RESUBMITTED,
            member.user_id,
            None,
            comment.strip() if comment and comment.strip() else "Resubmitted application",
            MembershipStatus.PENDING
        )
        return await self.member_repository.save(member)

    async def reactivate_member(
        self,
        member_id: str,
        approver_id: str,
        approver_role: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Member:
        """Reactivate a suspended or inactive membership"""
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        if member.status == MembershipStatus.ACTIVE:
            raise ValidationError("Member is already active")

        member.status = MembershipStatus.ACTIVE
        member.updated_at = datetime.utcnow()
        if not member.membership_expiry_date or member.is_membership_expired:
            member.membership_expiry_date = datetime.utcnow() + timedelta(days=365)
        member.approver_id = approver_id
        member.approver_role = approver_role
        member.review_comments = comment

        await self._append_audit_entry(
            member,
            MembershipAuditAction.REACTIVATED,
            approver_id,
            approver_role,
            comment,
            MembershipStatus.ACTIVE
        )
        return await self.member_repository.save(member)

    async def get_pending_memberships(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Member]:
        """Get pending membership requests"""
        return await self.member_repository.find_all(
            skip=skip,
            limit=limit,
            status=MembershipStatus.PENDING
        )

    async def get_member_by_user_id(self, user_id: str) -> Member:
        """
        Get member by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Member
        """
        member = await self.member_repository.find_by_user_id(user_id)
        if not member:
            raise EntityNotFoundError(f"Member not found for user {user_id}")
        return member
    
    async def get_member_by_membership_number(self, membership_number: str) -> Member:
        """
        Get member by membership number
        
        Args:
            membership_number: Membership number
            
        Returns:
            Member
        """
        member = await self.member_repository.find_by_membership_number(membership_number)
        if not member:
            raise EntityNotFoundError(f"Member not found: {membership_number}")
        return member
    
    async def attach_document_to_member(
        self,
        user_id: str,
        document_id: str
    ) -> Member:
        """
        Attach a document reference to a member by user ID.

        Args:
            user_id: Member's user ID
            document_id: Document ID to attach

        Returns:
            Updated Member
        """
        member = await self.member_repository.find_by_user_id(user_id)
        if not member:
            raise EntityNotFoundError(f"Member not found for user {user_id}")
        if str(document_id) not in member.document_ids:
            member.document_ids.append(str(document_id))
            member.updated_at = datetime.utcnow()
        return await self.member_repository.save(member)

    async def update_member_profile(
        self,
        member_id: str,
        **kwargs
    ) -> Member:
        """
        Update member profile
        
        Args:
            member_id: Member ID
            **kwargs: Fields to update
            
        Returns:
            Updated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        # Update allowed fields
        allowed_fields = {
            'bio', 'profile_photo_url', 'organization', 'position', 
            'department', 'newsletter_subscription', 'event_notifications',
            'communication_language'
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(member, field, value)
        
        member.updated_at = datetime.utcnow()
        return await self.member_repository.save(member)
    
    async def renew_membership(
        self,
        member_id: str,
        months: int = 12
    ) -> Member:
        """
        Renew member's membership
        
        Args:
            member_id: Member ID
            months: Renewal duration in months
            
        Returns:
            Renewed Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.renew_membership(months)
        return await self.member_repository.save(member)
    
    async def upgrade_membership_tier(
        self,
        member_id: str,
        new_tier: MembershipTier
    ) -> Member:
        """
        Upgrade member's tier
        
        Args:
            member_id: Member ID
            new_tier: New tier level
            
        Returns:
            Updated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.upgrade_tier(new_tier)
        return await self.member_repository.save(member)
    
    async def suspend_member(self, member_id: str, approver_id: Optional[str] = None, approver_role: Optional[str] = None, comment: Optional[str] = None) -> Member:
        """
        Suspend member account
        
        Args:
            member_id: Member ID
            approver_id: ID of the user performing the suspension
            approver_role: Role of the approver performing the suspension
            comment: Optional suspension reason/comment
            
        Returns:
            Suspended Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.suspend_membership()
        # Record approver info and review comment if provided
        if approver_id:
            member.approver_id = approver_id
        if approver_role:
            member.approver_role = approver_role
        if comment:
            member.review_comments = comment

        await self._append_audit_entry(
            member,
            MembershipAuditAction.SUSPENDED,
            approver_id,
            approver_role,
            comment,
            MembershipStatus.SUSPENDED
        )

        return await self.member_repository.save(member)
    
    async def activate_member(self, member_id: str) -> Member:
        """
        Activate member account
        
        Args:
            member_id: Member ID
            
        Returns:
            Activated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.activate_membership()
        return await self.member_repository.save(member)

    async def deactivate_member(self, member_id: str) -> Member:
        """
        Deactivate member account

        Args:
            member_id: Member ID

        Returns:
            Deactivated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")

        member.deactivate_membership()
        return await self.member_repository.save(member)

    async def resign_member(self, member_id: str) -> Member:
        """
        Mark member as resigned/alumni

        Args:
            member_id: Member ID

        Returns:
            Resigned Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")

        member.resign_membership()
        return await self.member_repository.save(member)
    
    async def record_meeting_attendance(self, member_id: str) -> Member:
        """
        Record meeting attendance
        
        Args:
            member_id: Member ID
            
        Returns:
            Updated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.record_meeting_attendance()
        return await self.member_repository.save(member)
    
    async def record_activity_participation(
        self,
        member_id: str,
        hours: float = 0.0
    ) -> Member:
        """
        Record activity participation
        
        Args:
            member_id: Member ID
            hours: Contribution hours
            
        Returns:
            Updated Member
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise EntityNotFoundError(f"Member not found: {member_id}")
        
        member.record_activity_participation(hours)
        return await self.member_repository.save(member)
    
    async def list_members(
        self,
        status: Optional[MembershipStatus] = None,
        membership_type: Optional[MembershipType] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Member]:
        """
        List members with filters
        
        Args:
            status: Filter by status
            membership_type: Filter by type
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of Members
        """
        filters = {}
        if status:
            filters['status'] = status
        if membership_type:
            filters['membership_type'] = membership_type
        
        return await self.member_repository.find_all(
            skip=skip,
            limit=limit,
            **filters
        )
    
    async def get_expiring_memberships(self, days: int = 30) -> List[Member]:
        """
        Get memberships expiring soon
        
        Args:
            days: Look ahead days
            
        Returns:
            List of Members with expiring memberships
        """
        return await self.member_repository.find_expiring(days)
    
    async def _generate_membership_number(self) -> str:
        """
        Generate unique membership number
        
        Returns:
            Membership number
        """
        import uuid
        from datetime import datetime
        
        year = datetime.utcnow().year
        random_suffix = str(uuid.uuid4()).split('-')[0].upper()
        return f"MEM-{year}-{random_suffix}"
