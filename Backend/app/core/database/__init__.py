"""
Database initialization and connection management
"""

import logging
from typing import Optional
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from beanie import init_beanie
from app.core.config import settings
from app.domain.models.user import User
from app.domain.models.member import Member
from app.domain.models.meeting import Meeting
from app.domain.models.document import Document
from app.domain.models.digital_identity import (
    DigitalIdentity, QRVerificationRecord, MeetingQRToken,
    ActivityQRToken, AttendanceRecord
)

logger = logging.getLogger(__name__)

# Global database client
_client: Optional[AsyncMongoClient] = None
_database: Optional[AsyncDatabase] = None


async def connect_to_db() -> bool:
    """
    Connect to MongoDB database
    
    Returns:
        True if connection successful, False otherwise
    """
    global _client, _database
    
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL.split('@')[1] if '@' in settings.MONGODB_URL else settings.MONGODB_URL}")
        
        # Create PyMongo async client
        _client = AsyncMongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Get database
        _database = _client[settings.DATABASE_NAME]
        
        # Test connection by pinging the database
        await _database.command('ping')
        
        # Initialize Beanie ODM
        await init_beanie(
            database=_database,
            document_models=[
                User, Member, Meeting, Document,
                DigitalIdentity, QRVerificationRecord,
                MeetingQRToken, ActivityQRToken, AttendanceRecord
            ]
        )
        
        logger.info(f"✅ MongoDB connected successfully to database: {settings.DATABASE_NAME}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.warning("⚠️  Application will continue without database - some features may not work")
        return False


async def disconnect_from_db():
    """
    Disconnect from MongoDB database
    """
    global _client
    
    try:
        if _client:
            _client.close()
            logger.info("✅ MongoDB disconnected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to disconnect from MongoDB: {str(e)}")


def get_database() -> Optional[AsyncDatabase]:
    """Get the database instance"""
    return _database


def get_client() -> Optional[AsyncMongoClient]:
    """Get the MongoDB client instance"""
    return _client
