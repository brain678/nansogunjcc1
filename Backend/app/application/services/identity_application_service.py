"""
Application Services for Digital Identity and QR System
Orchestrates domain services with DTOs and business workflows
"""

from typing import Optional, List
from datetime import datetime
from app.domain.services.identity_service import IdentityService, QRService
from app.domain.models.digital_identity import UserRole, IDCardStatus, VerificationMethod, AttendanceRecord
from app.domain.models.member import MembershipStatus
from app.infrastructure.persistence.member_repository import MemberRepository
from app.common.models.identity_value_objects import VerificationResponse, IDCardData, QRCodeData
from app.common.exceptions import ValidationError, NotFoundError


class IdentityApplicationService:
    """Application service for identity operations"""
    
    def __init__(self, identity_service: IdentityService, member_repository: Optional[MemberRepository] = None):
        self.identity_service = identity_service
        self.member_repository = member_repository or MemberRepository()
    
    async def create_identity_for_user(
        self,
        user_id: str,
        role: str,
        first_name: str,
        last_name: str,
        email: str,
        institution: str = "Not Specified",
        chapter: str = "General",
        profile_photo_url: Optional[str] = None
    ) -> dict:
        """
        Create digital identity for a user
        This is typically called during user registration
        """
        try:
            # Convert role string to UserRole enum
            role_enum = UserRole[role.upper()]
        except KeyError:
            raise ValidationError(f"Invalid role: {role}. Must be one of: {[r.value for r in UserRole]}")

        member = None
        try:
            member = await self.member_repository.find_by_user_id(user_id)
        except Exception:
            member = None

        if member and member.status != MembershipStatus.ACTIVE:
            raise ValidationError("Digital identity creation is only permitted for approved active members")
        
        identity = await self.identity_service.create_identity(
            user_id=user_id,
            role=role_enum,
            first_name=first_name,
            last_name=last_name,
            email=email,
            institution=institution,
            chapter=chapter,
            profile_photo_url=profile_photo_url
        )
        
        return {
            "user_id": identity.user_id,
            "membership_id": identity.membership_id,
            "qr_token": identity.qr_token,
            "card_status": identity.card_status.value,
            "role": identity.role.value,
            "created_at": identity.created_at.isoformat()
        }
    
    async def get_digital_card(self, user_id: str) -> dict:
        """Get user's digital ID card"""
        identity = await self.identity_service.get_identity(user_id)
        
        profile = identity.profile_data
        return {
            "membership_id": identity.membership_id,
            "full_name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
            "role": identity.role.value,
            "email": profile.get('email', ''),
            "phone": profile.get('phone', ''),
            "institution": profile.get('institution', 'Not Specified'),
            "chapter": profile.get('chapter', 'General'),
            "profile_photo_url": profile.get('profile_photo_url'),
            "member_since": profile.get('created_date', identity.created_at.isoformat()),
            "card_issue_date": identity.card_issue_date.isoformat(),
            "card_expiry_date": identity.card_expiry_date.isoformat() if identity.card_expiry_date else None,
            "card_status": identity.card_status.value,
            "qr_token": identity.qr_token,
            "verification_count": identity.verification_count
        }
    
    async def regenerate_qr_code(self, user_id: str) -> dict:
        """Regenerate QR code for user"""
        identity = await self.identity_service.regenerate_qr_token(user_id)
        
        return {
            "membership_id": identity.membership_id,
            "qr_token": identity.qr_token,
            "last_rotated_at": identity.qr_token_last_rotated_at.isoformat() if identity.qr_token_last_rotated_at else None,
            "message": "QR code regenerated successfully"
        }
    
    async def disable_card(self, user_id: str) -> dict:
        """Disable user's ID card"""
        identity = await self.identity_service.disable_card(user_id)
        
        return {
            "membership_id": identity.membership_id,
            "card_status": identity.card_status.value,
            "message": "ID card disabled successfully"
        }
    
    async def activate_card(self, user_id: str) -> dict:
        """Activate user's ID card"""
        identity = await self.identity_service.activate_card(user_id)
        
        return {
            "membership_id": identity.membership_id,
            "card_status": identity.card_status.value,
            "message": "ID card activated successfully"
        }
    
    async def get_card_status(self, user_id: str) -> dict:
        """Get current status of user's ID card"""
        identity = await self.identity_service.get_identity(user_id)
        
        return {
            "membership_id": identity.membership_id,
            "card_status": identity.card_status.value,
            "is_active": identity.is_active,
            "verification_count": identity.verification_count,
            "last_verified_at": identity.last_verified_at.isoformat() if identity.last_verified_at else None,
            "created_at": identity.created_at.isoformat()
        }


class QRApplicationService:
    """Application service for QR verification and check-in"""
    
    def __init__(self, qr_service: QRService):
        self.qr_service = qr_service
    
    async def verify_member_qr(
        self,
        qr_token: str,
        verified_by_id: Optional[str] = None,
        verified_by_role: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """
        Verify member via QR token
        Returns member information if valid
        """
        verification_response = await self.qr_service.verify_member_qr(
            qr_token=qr_token,
            verified_by_id=verified_by_id,
            verified_by_role=verified_by_role,
            ip_address=ip_address
        )
        
        return {
            "is_valid": verification_response.is_valid,
            "user_id": verification_response.user_id,
            "membership_id": verification_response.membership_id,
            "full_name": verification_response.full_name,
            "role": verification_response.role,
            "email": verification_response.email,
            "institution": verification_response.institution,
            "chapter": verification_response.chapter,
            "membership_status": verification_response.membership_status,
            "member_since": verification_response.member_since,
            "profile_photo_url": verification_response.profile_photo_url,
            "verified_at": verification_response.verified_at,
            "verification_method": verification_response.verification_method
        }
    
    async def create_meeting_qr(self, meeting_id: str) -> dict:
        """Create QR token for meeting attendance"""
        meeting_qr = await self.qr_service.create_meeting_qr(meeting_id)
        
        return {
            "meeting_id": meeting_qr.meeting_id,
            "qr_token": meeting_qr.qr_token,
            "is_enabled": meeting_qr.is_enabled,
            "status": meeting_qr.status,
            "created_at": meeting_qr.created_at.isoformat(),
            "verification_url": f"https://nans.org/verify/meeting/{meeting_qr.qr_token}"
        }
    
    async def create_activity_qr(self, activity_id: str, activity_name: str) -> dict:
        """Create QR token for activity check-in"""
        activity_qr = await self.qr_service.create_activity_qr(activity_id, activity_name)
        
        return {
            "activity_id": activity_qr.activity_id,
            "activity_name": activity_qr.activity_name,
            "qr_token": activity_qr.qr_token,
            "is_enabled": activity_qr.is_enabled,
            "status": activity_qr.status,
            "created_at": activity_qr.created_at.isoformat(),
            "verification_url": f"https://nans.org/verify/activity/{activity_qr.qr_token}"
        }
    
    async def check_in_meeting(self, qr_token: str, event_id: str, user_id: str) -> dict:
        """Check-in member to meeting"""
        attendance = await self.qr_service.check_in_meeting_qr(qr_token, event_id, user_id)
        
        return {
            "attendance_id": str(attendance.id),
            "user_id": attendance.user_id,
            "membership_id": attendance.membership_id,
            "event_type": attendance.event_type,
            "event_id": attendance.event_id,
            "check_in_time": attendance.check_in_time.isoformat(),
            "message": "Check-in successful"
        }
    
    async def check_in_activity(self, qr_token: str, event_id: str, user_id: str) -> dict:
        """Check-in member to activity"""
        attendance = await self.qr_service.check_in_activity_qr(qr_token, event_id, user_id)
        
        return {
            "attendance_id": str(attendance.id),
            "user_id": attendance.user_id,
            "membership_id": attendance.membership_id,
            "event_type": attendance.event_type,
            "event_id": attendance.event_id,
            "event_name": attendance.event_name,
            "check_in_time": attendance.check_in_time.isoformat(),
            "message": "Check-in successful"
        }
