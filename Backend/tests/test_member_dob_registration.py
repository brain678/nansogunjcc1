import asyncio
from unittest.mock import patch

from app.application.dtos.member_dto import MemberRegisterRequest
from app.common.models.value_objects import Email
from app.domain.models.member import MembershipTier, MembershipType
from app.domain.services.member_service import MemberService


class DummyRepository:
    def __init__(self):
        self.saved_member = None

    async def find_by_user_id(self, user_id):
        return None

    async def save(self, member):
        self.saved_member = member
        return member


def test_member_register_request_accepts_date_of_birth():
    request = MemberRegisterRequest(
        email="demo@example.com",
        first_name="Ada",
        last_name="Lovelace",
        date_of_birth="08-12",
        membership_type=MembershipType.FULL,
        membership_tier=MembershipTier.STANDARD,
    )

    assert request.date_of_birth == "08-12"


def test_member_service_persists_date_of_birth():
    repo = DummyRepository()
    service = MemberService(repo)

    with patch("app.domain.models.member.Member.get_pymongo_collection", return_value=None):
        member = asyncio.run(
            service.register_member(
                user_id="user-1",
                email=Email(value="demo@example.com"),
                first_name="Ada",
                last_name="Lovelace",
                date_of_birth="08-12",
            )
        )

    assert member.date_of_birth == "08-12"
    assert repo.saved_member is member
