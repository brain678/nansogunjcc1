from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.presentation.api.v1.routers.documents.routes as document_routes
from app.presentation.api.v1.dependencies import get_current_user_id


def test_get_document_by_id_returns_document_metadata(monkeypatch):
    class FakeDocumentRepository:
        async def get_by_id(self, document_id: str):
            return type(
                "Document",
                (),
                {
                    "id": document_id,
                    "title": "student-id.pdf",
                    "description": "Student ID card",
                    "file_url": "http://localhost:8000/uploads/student-id.pdf",
                    "file_size": 2048,
                    "file_type": "application/pdf",
                    "category": "student_id_card",
                    "uploaded_by": "user-1",
                    "uploaded_at": "2024-01-01T00:00:00",
                    "version": 1,
                },
            )()

    monkeypatch.setattr(document_routes, "DocumentRepository", FakeDocumentRepository)

    app = FastAPI()
    app.include_router(document_routes.router)
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"

    client = TestClient(app)
    response = client.get("/api/v1/documents/doc-123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "doc-123"
    assert payload["title"] == "student-id.pdf"
    assert payload["category"] == "student_id_card"
