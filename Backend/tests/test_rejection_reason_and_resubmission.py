from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.dtos.member_dto import MembershipActionRequest
from app.application.services.member_application_service import MemberApplicationService
from app.domain.models.member import MembershipStatus, MembershipType, MembershipTier


@pytest.mark.asyncio
async def test_reject_member_stores_review_comment_and_rejection_metadata():
    member = SimpleNamespace(
        id="member-1",
        user_id="user-1",
        email="member@example.com",
        first_name="Ada",
        last_name="Lovelace",
        full_name="Ada Lovelace",
        phone=None,
        membership_number="NANS-000001",
        membership_type=MembershipType.FULL,
        membership_tier=MembershipTier.STANDARD,
        status=MembershipStatus.PENDING,
        joined_date=datetime.utcnow(),
        membership_expiry_date=None,
        requested_expiry_months=12,
        submitted_at=None,
        approved_at=None,
        rejected_at=None,
        approver_id=None,
        approver_role=None,
        review_comments=None,
        audit_log=[],
        is_membership_expired=False,
        days_until_expiry=None,
        bio=None,
        profile_photo_url=None,
        document_ids=[],
        address=None,
        notes=None,
        organization=None,
        position=None,
        department=None,
        addresses=[],
        emergency_contact_name=None,
        emergency_contact_phone=None,
        newsletter_subscription=True,
        event_notifications=True,
        communication_language="en",
        last_active_at=None,
        meetings_attended=0,
        activities_participated=0,
        documents_contributed=0,
        total_contribution_hours=0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    member_service = Mock()

    async def reject_member(*args, **kwargs):
        member.status = MembershipStatus.REJECTED
        member.rejected_at = datetime.utcnow()
        member.approver_id = kwargs.get("approver_id")
        member.approver_role = kwargs.get("approver_role")
        member.review_comments = kwargs.get("comment")
        member.audit_log.append(
            SimpleNamespace(
                timestamp=datetime.utcnow(),
                action="rejected",
                performed_by_user_id=kwargs.get("approver_id"),
                performed_by_role=kwargs.get("approver_role"),
                comment=kwargs.get("comment"),
                resulting_status=MembershipStatus.REJECTED,
                metadata={},
            )
        )
        return member

    member_service.reject_member = AsyncMock(side_effect=reject_member)
    member_service.member_repository = SimpleNamespace(save=AsyncMock(return_value=member))

    service = MemberApplicationService(member_service=member_service, identity_service=Mock())

    response = await service.reject_member(
        member_id="member-1",
        approver_id="admin-1",
        approver_role="admin",
        request=MembershipActionRequest(comment="Documents were incomplete")
    )

    assert response.status == MembershipStatus.REJECTED
    assert response.review_comments == "Documents were incomplete"
    assert response.rejected_at is not None
    assert response.audit_log[-1].comment == "Documents were incomplete"


@pytest.mark.asyncio
async def test_resubmit_member_returns_to_pending_status():
    member = SimpleNamespace(
        id="member-1",
        user_id="user-1",
        email="member@example.com",
        first_name="Ada",
        last_name="Lovelace",
        full_name="Ada Lovelace",
        phone=None,
        membership_number="NANS-000001",
        membership_type=MembershipType.FULL,
        membership_tier=MembershipTier.STANDARD,
        status=MembershipStatus.REJECTED,
        joined_date=datetime.utcnow(),
        membership_expiry_date=None,
        requested_expiry_months=12,
        submitted_at=None,
        approved_at=None,
        rejected_at=datetime.utcnow(),
        approver_id="admin-1",
        approver_role="admin",
        review_comments="Documents were incomplete",
        audit_log=[],
        is_membership_expired=False,
        days_until_expiry=None,
        bio=None,
        profile_photo_url=None,
        document_ids=[],
        address=None,
        notes=None,
        organization=None,
        position=None,
        department=None,
        addresses=[],
        emergency_contact_name=None,
        emergency_contact_phone=None,
        newsletter_subscription=True,
        event_notifications=True,
        communication_language="en",
        last_active_at=None,
        meetings_attended=0,
        activities_participated=0,
        documents_contributed=0,
        total_contribution_hours=0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    member_service = Mock()

    async def resubmit_member(*args, **kwargs):
        member.status = MembershipStatus.PENDING
        member.approved_at = None
        member.rejected_at = None
        member.approver_id = None
        member.approver_role = None
        member.review_comments = None
        member.audit_log.append(
            SimpleNamespace(
                timestamp=datetime.utcnow(),
                action="resubmitted",
                performed_by_user_id=member.user_id,
                performed_by_role=None,
                comment="Resubmitted application",
                resulting_status=MembershipStatus.PENDING,
                metadata={},
            )
        )
        return member

    member_service.resubmit_member = AsyncMock(side_effect=resubmit_member)
    member_service.member_repository = SimpleNamespace(save=AsyncMock(return_value=member))

    service = MemberApplicationService(member_service=member_service, identity_service=Mock())

    response = await service.resubmit_member(member_id="member-1", request=MembershipActionRequest())

    assert response.status == MembershipStatus.PENDING
    assert response.review_comments is None
    assert response.approver_id is None
    assert response.approver_role is None
