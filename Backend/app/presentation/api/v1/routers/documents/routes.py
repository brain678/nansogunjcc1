from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.application.dtos.document_dto import DocumentUploadResponse
from app.core.config import PROJECT_ROOT, settings
from app.domain.models.document import Document
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.member_repository import MemberRepository
from app.presentation.api.v1.dependencies import get_current_user_id
from app.presentation.api.v1.dependencies import get_current_user, require_permission


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"]
)


@router.get(
    "/{document_id}",
    response_model=DocumentUploadResponse,
    summary="Get document metadata",
    description="Retrieve uploaded document metadata by document ID."
)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
) -> DocumentUploadResponse:
    """Return document metadata for a previously uploaded document."""
    repository = DocumentRepository()
    document = await repository.get_by_id(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentUploadResponse(
        id=str(document.id),
        title=document.title,
        description=document.description,
        file_url=document.file_url,
        file_size=document.file_size,
        file_type=document.file_type,
        category=document.category,
        uploaded_by=document.uploaded_by,
        uploaded_at=document.uploaded_at,
        version=document.version,
    )


@router.get(
    "/by-user/{user_id}",
    response_model=list[DocumentUploadResponse],
    summary="List documents by user",
    description="Retrieve uploaded document metadata for a specific user."
)
async def get_documents_by_user(
    user_id: str,
    current_user = Depends(get_current_user),
) -> list[DocumentUploadResponse]:
    """Return uploaded document metadata for a specific user."""
    require_permission(current_user, "members", "read", "any")
    repository = DocumentRepository()
    documents = await repository.list_by_uploaded_by(user_id)

    return [
        DocumentUploadResponse(
            id=str(document.id),
            title=document.title,
            description=document.description,
            file_url=document.file_url,
            file_size=document.file_size,
            file_type=document.file_type,
            category=document.category,
            uploaded_by=document.uploaded_by,
            uploaded_at=document.uploaded_at,
            version=document.version,
        )
        for document in documents
    ]


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    summary="Upload document",
    description="Upload a document file and return metadata for the uploaded document."
)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    user_id: str = Depends(get_current_user_id),
    request: Request = None,
) -> DocumentUploadResponse:
    """Upload a document and return its metadata."""
    try:
        upload_dir = PROJECT_ROOT / settings.UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename).suffix
        filename = f"{uuid4().hex}{suffix}"
        file_path = upload_dir / filename

        contents = await file.read()
        file_path.write_bytes(contents)

        file_url = f"/uploads/{filename}"

        document = Document(
            title=file.filename,
            description=None,
            file_url=file_url,
            file_size=len(contents),
            file_type=file.content_type or "application/octet-stream",
            category=category,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow(),
        )

        repository = DocumentRepository()
        created_document = await repository.create(document)

        member_repository = MemberRepository()
        member = await member_repository.find_by_user_id(user_id)
        if member:
            if str(created_document.id) not in member.document_ids:
                member.document_ids.append(str(created_document.id))
                member.updated_at = datetime.utcnow()
                await member_repository.save(member)

        return DocumentUploadResponse(
            id=str(created_document.id),
            title=created_document.title,
            description=created_document.description,
            file_url=created_document.file_url,
            file_size=created_document.file_size,
            file_type=created_document.file_type,
            category=created_document.category,
            uploaded_by=created_document.uploaded_by,
            uploaded_at=created_document.uploaded_at,
            version=created_document.version,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
