# app/common/models/base_entity.py

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class BaseEntity(Document):
    """Base entity for all domain entities"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    version: int = 1
    
    class Settings:
        is_root = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v),
        }
    
    def is_deleted(self) -> bool:
        """Check if entity is soft deleted"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Soft delete entity"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft deleted entity"""
        self.deleted_at = None
    
    def increment_version(self) -> None:
        """Increment version for optimistic locking"""
        self.version += 1
        self.updated_at = datetime.utcnow()
