from datetime import datetime
from typing import Optional

from app.common.models.base_entity import BaseEntity
from pydantic import Field


class Document(BaseEntity):
    """Document domain model"""

    title: str
    description: Optional[str] = None
    file_url: str
    file_size: int
    file_type: str
    category: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
