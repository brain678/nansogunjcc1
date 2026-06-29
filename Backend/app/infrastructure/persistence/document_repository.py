from app.domain.models.document import Document
from app.common.exceptions import EntityNotFoundError


class DocumentRepository:
    """Document repository using Beanie ODM"""

    def __init__(self):
        self.model = Document

    async def create(self, document: Document) -> Document:
        try:
            created = await document.save()
            return created
        except Exception as exc:
            raise EntityNotFoundError(f"Failed to create document: {str(exc)}")

    async def get_by_id(self, document_id: str) -> Document | None:
        try:
            document = await self.model.get(document_id)
            if document and not document.is_deleted():
                return document
            return None
        except Exception:
            return None

    async def save(self, document: Document) -> Document:
        try:
            saved = await document.save()
            return saved
        except Exception as exc:
            raise EntityNotFoundError(f"Failed to save document: {str(exc)}")
