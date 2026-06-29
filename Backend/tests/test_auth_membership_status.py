from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.presentation.api.v1.routers.auth.routes as auth_routes


class _FakeUser:
    def __init__(self):
        self.id = "user-1"
        self.email = "member@example.com"
        self.first_name = "Ada"
        self.last_name = "Lovelace"
        self.phone = None
        self.profile_photo_url = None
        self.roles = []
        self.mfa_enabled = False
        self.status = type("Status", (), {"value": "active"})()
        self.last_login_at = None
        self.created_at = "2024-01-01T00:00:00"


class _FakeMemberRepository:
    async def find_by_user_id(self, user_id: str):
        return type(
            "Member",
            (),
            {
                "status": type("Status", (), {"value": "pending"})(),
                "membership_number": "NANS-001",
                "audit_log": [
                    type(
                        "AuditEntry",
                        (),
                        {"metadata": {"qr_token": "qr-token-123"}},
                    )()
                ],
            },
        )()


class _FakeJWTHandler:
    def verify_access_token(self, token: str):
        return {"sub": "user-1", "membership_status": None, "membership_number": None}


class _FakeAuthService:
    def __init__(self):
        self.jwt_handler = _FakeJWTHandler()
        self.member_repository = _FakeMemberRepository()

    async def get_current_user(self, token: str):
        return _FakeUser()


def test_current_user_profile_reflects_membership_status_from_member_repository(monkeypatch):
    fake_auth_service = _FakeAuthService()

    async def override_get_auth_service():
        return fake_auth_service

    app = FastAPI()
    app.include_router(auth_routes.router)
    app.dependency_overrides[auth_routes.get_auth_service] = override_get_auth_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload.get("membershipStatus") == "pending" or payload.get("membership_status") == "pending"
    assert payload.get("membershipNumber") == "NANS-001" or payload.get("membership_number") == "NANS-001"
    assert payload.get("qrToken") == "qr-token-123" or payload.get("qr_token") == "qr-token-123"
