from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.dtos.member_dto import MembershipActionRequest
from app.application.services.member_application_service import MemberApplicationService
from app.domain.models.member import MembershipStatus, MembershipType, MembershipTier
from app.domain.models.digital_identity import IDCardStatus


@pytest.mark.asyncio
async def test_approve_member_returns_identity_metadata_for_profile_display():
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

    async def approve_member(*args, **kwargs):
        member.status = MembershipStatus.ACTIVE
        member.approved_at = datetime.utcnow()
        member.approver_id = "admin-1"
        member.approver_role = "admin"
        member.review_comments = "Approved"
        member.audit_log.append(
            SimpleNamespace(
                timestamp=datetime.utcnow(),
                action=SimpleNamespace(value="approved"),
                performed_by_user_id="admin-1",
                performed_by_role="admin",
                comment="Approved",
                resulting_status=MembershipStatus.ACTIVE,
                metadata={},
            )
        )
        return member

    member_service.approve_member = AsyncMock(side_effect=approve_member)
    member_service.member_repository = SimpleNamespace(save=AsyncMock(return_value=member))

    identity_service = Mock()
    identity_service.create_identity = AsyncMock(
        return_value=SimpleNamespace(
            membership_id="NANS-2026-000001",
            qr_token="qr-token-123",
            card_status=IDCardStatus.ACTIVE,
        )
    )

    service = MemberApplicationService(member_service=member_service, identity_service=identity_service)

    response = await service.approve_member(
        member_id="member-1",
        approver_id="admin-1",
        approver_role="admin",
        request=MembershipActionRequest(comment="Approved")
    )

    assert response.status == MembershipStatus.ACTIVE
    assert response.membership_id == "NANS-2026-000001"
    assert response.qr_token == "qr-token-123"
    assert response.card_status == IDCardStatus.ACTIVE.value
    assert member.audit_log[-1].metadata["qr_token"] == "qr-token-123"


@pytest.mark.asyncio
async def test_deactivate_member_returns_inactive_status():
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
        status=MembershipStatus.ACTIVE,
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
    member_service.deactivate_member = AsyncMock(return_value=member)
    member_service.member_repository = SimpleNamespace(save=AsyncMock(return_value=member))

    service = MemberApplicationService(member_service=member_service, identity_service=Mock())

    response = await service.deactivate_member("member-1")

    assert response.status == MembershipStatus.INACTIVE


@pytest.mark.asyncio
async def test_suspend_member_records_comment_and_status():
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
        status=MembershipStatus.ACTIVE,
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

    async def suspend_member(*args, **kwargs):
        member.status = MembershipStatus.SUSPENDED
        member.approver_id = kwargs.get("approver_id")
        member.approver_role = kwargs.get("approver_role")
        member.review_comments = kwargs.get("comment")
        member.audit_log.append(
            SimpleNamespace(
                timestamp=datetime.utcnow(),
                action=SimpleNamespace(value="suspended"),
                performed_by_user_id=kwargs.get("approver_id"),
                performed_by_role=kwargs.get("approver_role"),
                comment=kwargs.get("comment"),
                resulting_status=MembershipStatus.SUSPENDED,
                metadata={},
            )
        )
        return member

    member_service.suspend_member = AsyncMock(side_effect=suspend_member)
    member_service.member_repository = SimpleNamespace(save=AsyncMock(return_value=member))

    service = MemberApplicationService(member_service=member_service, identity_service=Mock())

    response = await service.suspend_member(
        member_id="member-1",
        approver_id="admin-1",
        approver_role="admin",
        request=MembershipActionRequest(comment="Violation of code of conduct")
    )

    assert response.status == MembershipStatus.SUSPENDED
    assert response.review_comments == "Violation of code of conduct"
    assert response.approver_id == "admin-1"
    assert response.approver_role == "admin"
    assert response.audit_log[-1].comment == "Violation of code of conduct"
    assert response.audit_log[-1].action == "suspended"
