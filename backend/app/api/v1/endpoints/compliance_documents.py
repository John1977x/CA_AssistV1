"""
Compliance Document Endpoints - API routes for compliance documents
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.schemas.compliance_document import (
    ComplianceDocumentCreate, ComplianceDocumentUpdate, ComplianceDocumentVerify,
    ComplianceDocumentOut, ComplianceDocumentListResponse,
    ClientUploadedDocumentCreate, ClientUploadedDocumentUpdate,
    ClientUploadedDocumentOut, ClientUploadedDocumentListResponse,
    DocumentTemplateOut, DocumentTemplateListResponse,
    DocumentSummary, DocumentStatusEnum
)
from app.services.compliance_document import (
    create_compliance_document, get_compliance_document, get_compliance_documents,
    update_compliance_document, verify_compliance_document, delete_compliance_document,
    create_client_document, get_client_documents, verify_client_document,
    get_document_templates, get_document_summary
)

router = APIRouter(prefix="/compliance", tags=["Compliance Documents"])


# ─── Compliance Document Endpoints ──────────────────────────────────────────

@router.post("/{compliance_id}/documents", response_model=ComplianceDocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(
    compliance_id: int,
    data: ComplianceDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new compliance document"""
    return await create_compliance_document(db, compliance_id, current_user.user_id, data)


@router.get("/{compliance_id}/documents", response_model=ComplianceDocumentListResponse)
async def list_documents(
    compliance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    document_type: str = Query(None),
    status: str = Query(None),
):
    """Get paginated compliance documents"""
    return await get_compliance_documents(db, compliance_id, page, page_size, document_type, status)


@router.get("/documents/{document_id}", response_model=ComplianceDocumentOut)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single compliance document"""
    return await get_compliance_document(db, document_id)


@router.put("/documents/{document_id}", response_model=ComplianceDocumentOut)
async def update_document(
    document_id: int,
    data: ComplianceDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a compliance document"""
    return await update_compliance_document(db, document_id, data)


@router.post("/documents/{document_id}/verify", response_model=ComplianceDocumentOut)
async def verify_document(
    document_id: int,
    data: ComplianceDocumentVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a compliance document"""
    return await verify_compliance_document(db, document_id, current_user.user_id, data)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a compliance document"""
    await delete_compliance_document(db, document_id, current_user.user_id)


# ─── Client Uploaded Document Endpoints ─────────────────────────────────────

@router.post("/{compliance_id}/client-documents", response_model=ClientUploadedDocumentOut, status_code=status.HTTP_201_CREATED)
async def create_client_document_endpoint(
    compliance_id: int,
    data: ClientUploadedDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a client uploaded document"""
    # For now, use current_user.user_id as client_id
    # In production, this should be the actual client_id from the request
    return await create_client_document(db, compliance_id, current_user.user_id, data)


@router.get("/{compliance_id}/client-documents", response_model=ClientUploadedDocumentListResponse)
async def list_client_documents(
    compliance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
):
    """Get paginated client uploaded documents"""
    return await get_client_documents(db, compliance_id, page, page_size, status)


@router.post("/client-documents/{upload_id}/verify", response_model=ClientUploadedDocumentOut)
async def verify_client_document_endpoint(
    upload_id: int,
    status: DocumentStatusEnum,
    verification_notes: str = Query(None),
    rejection_reason: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a client uploaded document"""
    return await verify_client_document(
        db, upload_id, current_user.user_id, status, verification_notes, rejection_reason
    )


# ─── Document Template Endpoints ────────────────────────────────────────────

@router.get("/templates", response_model=DocumentTemplateListResponse)
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all active document templates"""
    return await get_document_templates(db)


# ─── Document Summary Endpoints ─────────────────────────────────────────────

@router.get("/{compliance_id}/documents/summary", response_model=DocumentSummary)
async def get_summary(
    compliance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document summary for a compliance record"""
    return await get_document_summary(db, compliance_id)
