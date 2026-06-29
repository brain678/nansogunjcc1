"""
Domain Services for Digital Identity and QR System
Encapsulates core business logic for identity and QR operations
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
import re
from app.domain.models.digital_identity import (
    DigitalIdentity, QRVerificationRecord, MeetingQRToken, 
    ActivityQRToken, AttendanceRecord, IDCardStatus, MembershipStatus,
    VerificationMethod, UserRole, QRTokenType
)
from app.common.models.identity_value_objects import MembershipID, QRToken, VerificationResponse
from app.infrastructure.persistence.identity_repository import (
    DigitalIdentityRepository, QRVerificationRecordRepository,
    MeetingQRTokenRepository, ActivityQRTokenRepository, AttendanceRecordRepository
)
from app.common.exceptions import ValidationError, NotFoundError


class IdentityService:
    """Domain service for digital identity operations"""
    
    def __init__(self, identity_repo: DigitalIdentityRepository):
        self.identity_repo = identity_repo
    
    async def create_identity(
        self,
        user_id: str,
        role: UserRole,
        first_name: str,
        last_name: str,
        email: str,
        institution: str = "Not Specified",
        chapter: str = "General",
        profile_photo_url: Optional[str] = None
    ) -> DigitalIdentity:
        """Create new digital identity for a user"""
        
        # Check if identity already exists
        existing = await self.identity_repo.get_by_user_id(user_id)
        if existing:
            raise ValidationError(f"Digital identity already exists for user {user_id}")
        
        # Generate membership ID
        membership_id = await self._generate_membership_id()
        
        # Generate QR token
        qr_token = QRToken.generate()
        
        # Create identity
        identity = DigitalIdentity(
            user_id=user_id,
            membership_id=membership_id.value,
            role=role,
            card_status=IDCardStatus.ACTIVE,
            qr_token=qr_token.value,
            profile_data={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "institution": institution,
                "chapter": chapter,
                "profile_photo_url": profile_photo_url,
                "created_date": datetime.utcnow().isoformat()
            }
        )
        
        return await self.identity_repo.create(identity)
    
    async def _generate_membership_id(self) -> MembershipID:
        """Generate unique membership ID"""
        current_year = datetime.utcnow().year
        total_count = await self.identity_repo.count() + 1
        
        # Format: NANS-YYYY-XXXXXX
        membership_id_str = f"NANS-{current_year}-{total_count:06d}"
        return MembershipID(value=membership_id_str)
    
    async def get_identity(self, user_id: str) -> DigitalIdentity:
        """Get user's digital identity"""
        identity = await self.identity_repo.get_by_user_id(user_id)
        if not identity:
            raise NotFoundError(f"Digital identity not found for user {user_id}")
        return identity
    
    async def disable_card(self, user_id: str, reason: str = "Disabled by user") -> DigitalIdentity:
        """Disable digital identity card"""
        identity = await self.get_identity(user_id)
        identity.card_status = IDCardStatus.DISABLED
        identity.updated_at = datetime.utcnow()
        return await self.identity_repo.update(identity)
    
    async def activate_card(self, user_id: str) -> DigitalIdentity:
        """Activate digital identity card"""
        identity = await self.get_identity(user_id)
        if identity.card_status == IDCardStatus.DISABLED:
            identity.card_status = IDCardStatus.ACTIVE
            identity.updated_at = datetime.utcnow()
        return await self.identity_repo.update(identity)
    
    async def regenerate_qr_token(self, user_id: str) -> DigitalIdentity:
        """Regenerate QR token for a user"""
        identity = await self.get_identity(user_id)
        
        # Generate new QR token
        new_qr_token = QRToken.generate()
        identity.qr_token = new_qr_token.value
        identity.qr_token_last_rotated_at = datetime.utcnow()
        identity.updated_at = datetime.utcnow()
        
        return await self.identity_repo.update(identity)
    
    async def update_profile_data(self, user_id: str, profile_data: dict) -> DigitalIdentity:
        """Update cached profile data"""
        identity = await self.get_identity(user_id)
        identity.profile_data.update(profile_data)
        identity.updated_at = datetime.utcnow()
        return await self.identity_repo.update(identity)
    
    async def expire_card(self, user_id: str) -> DigitalIdentity:
        """Mark card as expired"""
        identity = await self.get_identity(user_id)
        identity.card_status = IDCardStatus.EXPIRED
        identity.card_expiry_date = datetime.utcnow()
        identity.updated_at = datetime.utcnow()
        return await self.identity_repo.update(identity)
    
    def is_card_valid(self, identity: DigitalIdentity) -> bool:
        """Check if card is currently valid"""
        if not identity.is_active:
            return False
        if identity.card_status != IDCardStatus.ACTIVE:
            return False
        if identity.card_expiry_date and identity.card_expiry_date < datetime.utcnow():
            return False
        return True


class QRService:
    """Domain service for QR verification and check-in"""
    
    def __init__(
        self,
        identity_repo: DigitalIdentityRepository,
        verification_repo: QRVerificationRecordRepository,
        meeting_qr_repo: MeetingQRTokenRepository,
        activity_qr_repo: ActivityQRTokenRepository,
        attendance_repo: AttendanceRecordRepository
    ):
        self.identity_repo = identity_repo
        self.verification_repo = verification_repo
        self.meeting_qr_repo = meeting_qr_repo
        self.activity_qr_repo = activity_qr_repo
        self.attendance_repo = attendance_repo
    
    async def verify_member_qr(
        self,
        qr_token: str,
        verified_by_id: Optional[str] = None,
        verified_by_role: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> VerificationResponse:
        """Verify member via QR token"""
        
        # Find identity by QR token
        identity = await self.identity_repo.get_by_qr_token(qr_token)
        if not identity:
            # Create invalid verification record
            await self._create_verification_record(
                qr_token=qr_token,
                user_id="UNKNOWN",
                is_valid=False,
                verified_by_id=verified_by_id,
                verified_by_role=verified_by_role,
                ip_address=ip_address
            )
            raise NotFoundError("Invalid QR token")
        
        # Check if card is valid
        if not identity.is_active or identity.card_status != IDCardStatus.ACTIVE:
            await self._create_verification_record(
                qr_token=qr_token,
                user_id=identity.user_id,
                is_valid=False,
                verified_by_id=verified_by_id,
                verified_by_role=verified_by_role,
                ip_address=ip_address,
                details={"reason": f"Card status: {identity.card_status}"}
            )
            raise ValidationError(f"Card is {identity.card_status}")
        
        # Update verification count
        identity.verification_count += 1
        identity.last_verified_at = datetime.utcnow()
        await self.identity_repo.update(identity)
        
        # Create verification record
        await self._create_verification_record(
            qr_token=qr_token,
            user_id=identity.user_id,
            is_valid=True,
            verified_by_id=verified_by_id,
            verified_by_role=verified_by_role,
            ip_address=ip_address
        )
        
        # Build verification response
        profile = identity.profile_data
        return VerificationResponse(
            is_valid=True,
            user_id=identity.user_id,
            membership_id=identity.membership_id,
            full_name=f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
            role=identity.role.value,
            email=profile.get('email', ''),
            institution=profile.get('institution', 'Not Specified'),
            chapter=profile.get('chapter', 'General'),
            membership_status=MembershipStatus.ACTIVE.value,
            member_since=profile.get('created_date', datetime.utcnow().isoformat()),
            profile_photo_url=profile.get('profile_photo_url'),
            verified_at=datetime.utcnow().isoformat(),
            verification_method=VerificationMethod.QR_CODE.value
        )
    
    async def create_meeting_qr(self, meeting_id: str) -> MeetingQRToken:
        """Create QR token for meeting attendance"""
        
        # Check if already exists
        existing = await self.meeting_qr_repo.get_by_meeting_id(meeting_id)
        if existing:
            return existing
        
        # Generate QR token
        qr_token = QRToken.generate()
        
        # Create meeting QR
        meeting_qr = MeetingQRToken(
            meeting_id=meeting_id,
            qr_token=qr_token.value
        )
        
        return await self.meeting_qr_repo.create(meeting_qr)
    
    async def create_activity_qr(self, activity_id: str, activity_name: str) -> ActivityQRToken:
        """Create QR token for activity check-in"""
        
        # Check if already exists
        existing = await self.activity_qr_repo.get_by_activity_id(activity_id)
        if existing:
            return existing
        
        # Generate QR token
        qr_token = QRToken.generate()
        
        # Create activity QR
        activity_qr = ActivityQRToken(
            activity_id=activity_id,
            activity_name=activity_name,
            qr_token=qr_token.value
        )
        
        return await self.activity_qr_repo.create(activity_qr)
    
    async def check_in_meeting_qr(
        self,
        qr_token: str,
        event_id: str,
        user_id: str
    ) -> AttendanceRecord:
        """Check-in member to meeting via QR"""
        
        # Get meeting QR
        meeting_qr = await self.meeting_qr_repo.get_by_qr_token(qr_token)
        if not meeting_qr:
            raise NotFoundError("Invalid meeting QR token")
        
        # Get identity by user_id
        identity = await self.identity_repo.get_by_user_id(user_id)
        if not identity:
            raise NotFoundError("Identity not found for user")
        
        # Create attendance record
        attendance = AttendanceRecord(
            user_id=identity.user_id,
            membership_id=identity.membership_id,
            event_type="MEETING",
            event_id=event_id,
            event_name="Meeting",
            qr_token=qr_token,
            verification_method=VerificationMethod.QR_CODE
        )
        
        # Save and update check-in count
        attendance = await self.attendance_repo.create(attendance)
        await self.meeting_qr_repo.add_check_in(event_id, identity.user_id)
        
        return attendance
    
    async def check_in_activity_qr(
        self,
        qr_token: str,
        event_id: str,
        user_id: str
    ) -> AttendanceRecord:
        """Check-in member to activity via QR"""
        
        # Get activity QR
        activity_qr = await self.activity_qr_repo.get_by_qr_token(qr_token)
        if not activity_qr:
            raise NotFoundError("Invalid activity QR token")
        
        # Get identity by user_id
        identity = await self.identity_repo.get_by_user_id(user_id)
        if not identity:
            raise NotFoundError("Identity not found for user")
        
        # Create attendance record
        attendance = AttendanceRecord(
            user_id=identity.user_id,
            membership_id=identity.membership_id,
            event_type="ACTIVITY",
            event_id=event_id,
            event_name=activity_qr.activity_name,
            qr_token=qr_token,
            verification_method=VerificationMethod.QR_CODE
        )
        
        # Save and update check-in count
        attendance = await self.attendance_repo.create(attendance)
        await self.activity_qr_repo.add_check_in(event_id, identity.user_id)
        
        return attendance
    
    async def _create_verification_record(
        self,
        qr_token: str,
        user_id: str,
        is_valid: bool,
        verified_by_id: Optional[str] = None,
        verified_by_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None
    ) -> QRVerificationRecord:
        """Create verification audit record"""
        
        record = QRVerificationRecord(
            qr_token=qr_token,
            user_id=user_id,
            verification_method=VerificationMethod.QR_CODE,
            qr_type=QRTokenType.MEMBER_IDENTITY,
            verified_by_id=verified_by_id,
            verified_by_role=verified_by_role,
            context_type="GENERAL",
            is_valid=is_valid,
            verification_details=details or {},
            ip_address=ip_address
        )
        
        return await self.verification_repo.create(record)
