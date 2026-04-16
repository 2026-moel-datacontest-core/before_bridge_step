from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.document_draft import (
    DocumentDraftRequest,
    DocumentDraftResponse,
)
from backend.app.services.document_draft import build_document_draft

router = APIRouter(prefix="/api/v1/documents", tags=["document_draft"])


@router.post("/draft", response_model=DocumentDraftResponse)
def draft_document(payload: DocumentDraftRequest) -> DocumentDraftResponse:
    return build_document_draft(payload)
