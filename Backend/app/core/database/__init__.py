"""
Database initialization and connection management
"""

import logging
from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase
)
from beanie import init_beanie

from app.core.config import settings

from app.domain.models.user import User
from app.domain.models.member import Member
from app.domain.models.meeting import Meeting
from app.domain.models.document import Document
from app.domain.models.digital_identity import (
    DigitalIdentity,
    QRVerificationRecord,
    MeetingQRToken,
    ActivityQRToken,
    AttendanceRecord,
)

logger = logging.getLogger(__name__)

# Global database client and database instances
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_db() -> bool:
    """
    Connect to MongoDB and initialize Beanie.
    """
    global _client, _database

    try:
        # Log connection target safely
        mongodb_host = (
            settings.MONGODB_URL.split("@")[1]
            if "@" in settings.MONGODB_URL
            else settings.MONGODB_URL
        )

        logger.info(f"Connecting to MongoDB at {mongodb_host}")

        # Create MongoDB client
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
        )

        # Get database instance
        _database = _client[settings.DATABASE_NAME]

        # Verify database connectivity
        await _database.command("ping")

        # Initialize Beanie ODM
        await init_beanie(
            database=_database,
            document_models=[
                User,
                Member,
                Meeting,
                Document,
                DigitalIdentity,
                QRVerificationRecord,
                MeetingQRToken,
                ActivityQRToken,
                AttendanceRecord,
            ],
        )

        logger.info(
            f"MongoDB connected successfully to database: "
            f"{settings.DATABASE_NAME}"
        )

        return True

    except Exception as e:
        logger.exception(
            f"Failed to connect to MongoDB: {str(e)}"
        )

        # For production systems, fail startup completely
        raise


async def disconnect_from_db():
    """
    Close MongoDB connection.
    """
    global _client

    try:
        if _client:
            _client.close()
            logger.info("MongoDB disconnected successfully")

    except Exception as e:
        logger.exception(
            f"Failed to disconnect MongoDB: {str(e)}"
        )


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """
    Get MongoDB database instance.
    """
    return _database


def get_client() -> Optional[AsyncIOMotorClient]:
    """
    Get MongoDB client instance.
    """
    return _client
