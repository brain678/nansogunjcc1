"""
Repositories for Digital Identity and QR Token persistence
"""

from typing import Optional, List
from datetime import datetime
from app.domain.models.digital_identity import (
    DigitalIdentity, QRVerificationRecord, MeetingQRToken, 
    ActivityQRToken, AttendanceRecord
)


class DigitalIdentityRepository:
    """Repository for Digital Identity persistence"""
    
    async def create(self, identity: DigitalIdentity) -> DigitalIdentity:
        """Create new digital identity"""
        return await identity.insert()
    
    async def get_by_user_id(self, user_id: str) -> Optional[DigitalIdentity]:
        """Get identity by user ID"""
        return await DigitalIdentity.find_one({"user_id": user_id})
    
    async def get_by_membership_id(self, membership_id: str) -> Optional[DigitalIdentity]:
        """Get identity by membership ID"""
        return await DigitalIdentity.find_one({"membership_id": membership_id})
    
    async def get_by_qr_token(self, qr_token: str) -> Optional[DigitalIdentity]:
        """Get identity by QR token"""
        return await DigitalIdentity.find_one({"qr_token": qr_token})
    
    async def update(self, identity: DigitalIdentity) -> DigitalIdentity:
        """Update digital identity"""
        identity.updated_at = datetime.utcnow()
        return await identity.save()
    
    async def find_all_active(self, skip: int = 0, limit: int = 10) -> List[DigitalIdentity]:
        """Find all active identities"""
        return await DigitalIdentity.find(
            {"is_active": True}
        ).skip(skip).limit(limit).to_list()
    
    async def count(self) -> int:
        """Count total identities"""
        return await DigitalIdentity.count()
    
    async def count_active(self) -> int:
        """Count active identities"""
        return await DigitalIdentity.count({"is_active": True})


class QRVerificationRecordRepository:
    """Repository for QR Verification Records"""
    
    async def create(self, record: QRVerificationRecord) -> QRVerificationRecord:
        """Create new verification record"""
        return await record.insert()
    
    async def get_by_id(self, record_id: str) -> Optional[QRVerificationRecord]:
        """Get verification record by ID"""
        return await QRVerificationRecord.get(record_id)
    
    async def get_by_qr_token(self, qr_token: str) -> List[QRVerificationRecord]:
        """Get all verification records for a QR token"""
        return await QRVerificationRecord.find(
            {"qr_token": qr_token}
        ).sort([("verified_at", -1)]).to_list()
    
    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 10) -> List[QRVerificationRecord]:
        """Get verification records for a user"""
        return await QRVerificationRecord.find(
            {"user_id": user_id}
        ).sort([("verified_at", -1)]).skip(skip).limit(limit).to_list()
    
    async def get_by_verifier_id(self, verifier_id: str, skip: int = 0, limit: int = 10) -> List[QRVerificationRecord]:
        """Get verification records performed by a verifier"""
        return await QRVerificationRecord.find(
            {"verified_by_id": verifier_id}
        ).sort([("verified_at", -1)]).skip(skip).limit(limit).to_list()
    
    async def get_by_context(self, context_type: str, context_id: str) -> List[QRVerificationRecord]:
        """Get verification records for a specific context"""
        return await QRVerificationRecord.find(
            {"context_type": context_type, "context_id": context_id}
        ).sort([("verified_at", -1)]).to_list()
    
    async def count_by_user(self, user_id: str) -> int:
        """Count verifications for a user"""
        return await QRVerificationRecord.count({"user_id": user_id})


class MeetingQRTokenRepository:
    """Repository for Meeting QR Tokens"""
    
    async def create(self, token: MeetingQRToken) -> MeetingQRToken:
        """Create new meeting QR token"""
        return await token.insert()
    
    async def get_by_meeting_id(self, meeting_id: str) -> Optional[MeetingQRToken]:
        """Get QR token for a meeting"""
        return await MeetingQRToken.find_one({"meeting_id": meeting_id})
    
    async def get_by_qr_token(self, qr_token: str) -> Optional[MeetingQRToken]:
        """Get meeting by QR token"""
        return await MeetingQRToken.find_one({"qr_token": qr_token})
    
    async def update(self, token: MeetingQRToken) -> MeetingQRToken:
        """Update meeting QR token"""
        return await token.save()
    
    async def add_check_in(self, meeting_id: str, member_id: str) -> Optional[MeetingQRToken]:
        """Record a check-in for a meeting"""
        token = await self.get_by_meeting_id(meeting_id)
        if not token:
            return None
        
        token.check_in_count += 1
        if member_id not in token.unique_members_checked_in:
            token.unique_members_checked_in.append(member_id)
        
        return await token.save()


class ActivityQRTokenRepository:
    """Repository for Activity QR Tokens"""
    
    async def create(self, token: ActivityQRToken) -> ActivityQRToken:
        """Create new activity QR token"""
        return await token.insert()
    
    async def get_by_activity_id(self, activity_id: str) -> Optional[ActivityQRToken]:
        """Get QR token for an activity"""
        return await ActivityQRToken.find_one({"activity_id": activity_id})
    
    async def get_by_qr_token(self, qr_token: str) -> Optional[ActivityQRToken]:
        """Get activity by QR token"""
        return await ActivityQRToken.find_one({"qr_token": qr_token})
    
    async def update(self, token: ActivityQRToken) -> ActivityQRToken:
        """Update activity QR token"""
        return await token.save()
    
    async def add_check_in(self, activity_id: str, member_id: str) -> Optional[ActivityQRToken]:
        """Record a check-in for an activity"""
        token = await self.get_by_activity_id(activity_id)
        if not token:
            return None
        
        token.check_in_count += 1
        if member_id not in token.unique_members_checked_in:
            token.unique_members_checked_in.append(member_id)
        
        return await token.save()


class AttendanceRecordRepository:
    """Repository for Attendance Records"""
    
    async def create(self, record: AttendanceRecord) -> AttendanceRecord:
        """Create new attendance record"""
        return await record.insert()
    
    async def get_by_id(self, record_id: str) -> Optional[AttendanceRecord]:
        """Get attendance record by ID"""
        return await AttendanceRecord.get(record_id)
    
    async def get_by_event(self, event_type: str, event_id: str) -> List[AttendanceRecord]:
        """Get all attendance records for an event"""
        return await AttendanceRecord.find(
            {"event_type": event_type, "event_id": event_id}
        ).sort([("check_in_time", -1)]).to_list()
    
    async def get_by_member(self, user_id: str, skip: int = 0, limit: int = 10) -> List[AttendanceRecord]:
        """Get attendance records for a member"""
        return await AttendanceRecord.find(
            {"user_id": user_id}
        ).sort([("check_in_time", -1)]).skip(skip).limit(limit).to_list()
    
    async def get_by_member_and_event(self, user_id: str, event_type: str, event_id: str) -> Optional[AttendanceRecord]:
        """Check if member attended specific event"""
        return await AttendanceRecord.find_one(
            {"user_id": user_id, "event_type": event_type, "event_id": event_id}
        )
    
    async def count_by_event(self, event_type: str, event_id: str) -> int:
        """Count attendees for an event"""
        return await AttendanceRecord.count({"event_type": event_type, "event_id": event_id})
    
    async def count_by_member(self, user_id: str, event_type: str) -> int:
        """Count member's attendance for event type"""
        return await AttendanceRecord.count({"user_id": user_id, "event_type": event_type})
    
    async def update(self, record: AttendanceRecord) -> AttendanceRecord:
        """Update attendance record (e.g., add check-out time)"""
        return await record.save()
