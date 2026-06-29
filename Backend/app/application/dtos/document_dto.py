from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentUploadResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    file_url: str
    file_size: int
    file_type: str
    category: str
    uploaded_by: str
    uploaded_at: datetime
    version: int = Field(default=1)
