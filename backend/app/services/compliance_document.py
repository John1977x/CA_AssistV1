"""
Compliance Document Service - Handles compliance document operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, and_
from datetime import datetime, timezone
from typing import Optional, List

from app.models.compliance_document import (
    ComplianceDocument, ClientUploadedDocument, DocumentTemplate,
    DocumentTypeEnum, DocumentStatusEnum
)
from app.models.compliance import Compliance
from app.schemas.compliance_document import (
    ComplianceDocumentCreate, ComplianceDocumentUpdate, ComplianceDocumentVerify,
    ComplianceDocumentOut, ComplianceDocumentListResponse,
    ClientUploadedDocumentCreate, ClientUploadedDocumentUpdate,
    ClientUploadedDocumentOut, ClientUploadedDocumentListResponse,
    DocumentTemplateOut, DocumentTemplateListResponse,
    DocumentSummary
)
from app.core.errors import ResourceNotFoundError, ValidationError, AuthorizationError
from app.core.security import hash_password


# ─── Compliance Document CRUD ────────────────────────────────────────────────

async def create_compliance_document(
    db: AsyncSession,
    compliance_id: int,
    user_id: int,
    data: ComplianceDocumentCreate
) -> ComplianceDocumentOut:
    """Create a new compliance document"""
    # Verify compliance exists
    compliance_result = await db.execute(
        select(Compliance).where(Compliance.compliance_id == compliance_id)
    )
    if not compliance_result.scalar_one_or_none():
        raise ResourceNotFoundError("Compliance")

    # Hash password if provided
    password_hash = None
    if data.password_hash:
        password_hash = hash_password(data.password_hash)

    document = ComplianceDocument(
        compliance_id=compliance_id,
        document_type=data.document_type,
        document_name=data.document_name,
        document_number=data.document_number,
        file_url=data.file_url,
        file_name=data.file_name,
        file_size=data.file_size,
        file_type=data.file_type,
        username=data.username,
        password_hash=password_hash,
        access_url=data.access_url,
        issue_date=data.issue_date,
        expiry_date=data.expiry_date,
        description=data.description,
        metadata=data.metadata or {},
        uploaded_by_user_id=user_id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return ComplianceDocumentOut.model_validate(document)


async def get_compliance_document(db: AsyncSession, document_id: int) -> ComplianceDocumentOut:
    """Get a single compliance document"""
    result = await db.execute(
        select(ComplianceDocument).where(
            and_(
                ComplianceDocument.document_id == document_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise ResourceNotFoundError("Document")
    return ComplianceDocumentOut.model_validate(document)


async def get_compliance_documents(
    db: AsyncSession,
    compliance_id: int,
    page: int = 1,
    page_size: int = 20,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
) -> ComplianceDocumentListResponse:
    """Get paginated compliance documents for a compliance record"""
    # Verify compliance exists
    compliance_result = await db.execute(
        select(Compliance).where(Compliance.compliance_id == compliance_id)
    )
    if not compliance_result.scalar_one_or_none():
        raise ResourceNotFoundError("Compliance")

    # Build query
    query = select(ComplianceDocument).where(
        and_(
            ComplianceDocument.compliance_id == compliance_id,
            ComplianceDocument.is_deleted == False
        )
    )

    # Filter by type if provided
    if document_type:
        query = query.where(ComplianceDocument.document_type == document_type)

    # Filter by status if provided
    if status:
        query = query.where(ComplianceDocument.status == status)

    # Order by created_at descending
    query = query.order_by(desc(ComplianceDocument.uploaded_at))

    # Get total count
    count_result = await db.execute(
        select(func.count(ComplianceDocument.document_id)).where(
            and_(
                ComplianceDocument.compliance_id == compliance_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    return ComplianceDocumentListResponse(
        documents=[ComplianceDocumentOut.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


async def update_compliance_document(
    db: AsyncSession,
    document_id: int,
    data: ComplianceDocumentUpdate
) -> ComplianceDocumentOut:
    """Update a compliance document"""
    document = await db.execute(
        select(ComplianceDocument).where(
            and_(
                ComplianceDocument.document_id == document_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    document = document.scalar_one_or_none()
    if not document:
        raise ResourceNotFoundError("Document")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    
    # Hash password if provided
    if "password_hash" in update_data and update_data["password_hash"]:
        update_data["password_hash"] = hash_password(update_data["password_hash"])

    for field, value in update_data.items():
        setattr(document, field, value)

    document.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(document)
    return ComplianceDocumentOut.model_validate(document)


async def verify_compliance_document(
    db: AsyncSession,
    document_id: int,
    user_id: int,
    data: ComplianceDocumentVerify
) -> ComplianceDocumentOut:
    """Verify a compliance document"""
    document = await db.execute(
        select(ComplianceDocument).where(
            and_(
                ComplianceDocument.document_id == document_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    document = document.scalar_one_or_none()
    if not document:
        raise ResourceNotFoundError("Document")

    document.status = data.status
    document.verified_by_user_id = user_id
    document.verified_at = datetime.now(timezone.utc)
    document.verification_notes = data.verification_notes
    await db.commit()
    await db.refresh(document)
    return ComplianceDocumentOut.model_validate(document)


async def delete_compliance_document(db: AsyncSession, document_id: int, user_id: int) -> dict:
    """Soft delete a compliance document"""
    document = await db.execute(
        select(ComplianceDocument).where(
            and_(
                ComplianceDocument.document_id == document_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    document = document.scalar_one_or_none()
    if not document:
        raise ResourceNotFoundError("Document")

    document.is_deleted = True
    document.deleted_at = datetime.now(timezone.utc)
    document.deleted_by_user_id = user_id
    await db.commit()
    return {"message": "Document deleted"}


# ─── Client Uploaded Document CRUD ──────────────────────────────────────────

async def create_client_document(
    db: AsyncSession,
    compliance_id: int,
    client_id: int,
    data: ClientUploadedDocumentCreate
) -> ClientUploadedDocumentOut:
    """Create a client uploaded document"""
    # Verify compliance exists
    compliance_result = await db.execute(
        select(Compliance).where(Compliance.compliance_id == compliance_id)
    )
    if not compliance_result.scalar_one_or_none():
        raise ResourceNotFoundError("Compliance")

    # Hash password if provided
    password_hash = None
    if data.password_hash:
        password_hash = hash_password(data.password_hash)

    document = ClientUploadedDocument(
        compliance_id=compliance_id,
        client_id=client_id,
        document_type=data.document_type,
        document_name=data.document_name,
        document_number=data.document_number,
        file_url=data.file_url,
        file_name=data.file_name,
        file_size=data.file_size,
        file_type=data.file_type,
        username=data.username,
        password_hash=password_hash,
        access_url=data.access_url,
        issue_date=data.issue_date,
        expiry_date=data.expiry_date,
        description=data.description,
        metadata=data.metadata or {},
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return ClientUploadedDocumentOut.model_validate(document)


async def get_client_documents(
    db: AsyncSession,
    compliance_id: int,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
) -> ClientUploadedDocumentListResponse:
    """Get paginated client uploaded documents"""
    # Verify compliance exists
    compliance_result = await db.execute(
        select(Compliance).where(Compliance.compliance_id == compliance_id)
    )
    if not compliance_result.scalar_one_or_none():
        raise ResourceNotFoundError("Compliance")

    # Build query
    query = select(ClientUploadedDocument).where(
        and_(
            ClientUploadedDocument.compliance_id == compliance_id,
            ClientUploadedDocument.is_deleted == False
        )
    )

    # Filter by status if provided
    if status:
        query = query.where(ClientUploadedDocument.status == status)

    # Order by uploaded_at descending
    query = query.order_by(desc(ClientUploadedDocument.uploaded_at))

    # Get total count
    count_result = await db.execute(
        select(func.count(ClientUploadedDocument.upload_id)).where(
            and_(
                ClientUploadedDocument.compliance_id == compliance_id,
                ClientUploadedDocument.is_deleted == False
            )
        )
    )
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    return ClientUploadedDocumentListResponse(
        documents=[ClientUploadedDocumentOut.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


async def verify_client_document(
    db: AsyncSession,
    upload_id: int,
    user_id: int,
    status: DocumentStatusEnum,
    verification_notes: Optional[str] = None,
    rejection_reason: Optional[str] = None,
) -> ClientUploadedDocumentOut:
    """Verify a client uploaded document"""
    document = await db.execute(
        select(ClientUploadedDocument).where(
            and_(
                ClientUploadedDocument.upload_id == upload_id,
                ClientUploadedDocument.is_deleted == False
            )
        )
    )
    document = document.scalar_one_or_none()
    if not document:
        raise ResourceNotFoundError("Document")

    document.status = status
    document.verified_by_user_id = user_id
    document.verified_at = datetime.now(timezone.utc)
    document.verification_notes = verification_notes
    if status == DocumentStatusEnum.REJECTED:
        document.rejection_reason = rejection_reason
    await db.commit()
    await db.refresh(document)
    return ClientUploadedDocumentOut.model_validate(document)


# ─── Document Templates ─────────────────────────────────────────────────────

async def get_document_templates(db: AsyncSession) -> DocumentTemplateListResponse:
    """Get all active document templates"""
    result = await db.execute(
        select(DocumentTemplate)
        .where(DocumentTemplate.is_active == True)
        .order_by(DocumentTemplate.display_name)
    )
    templates = result.scalars().all()

    count_result = await db.execute(
        select(func.count(DocumentTemplate.template_id)).where(
            DocumentTemplate.is_active == True
        )
    )
    total = count_result.scalar() or 0

    return DocumentTemplateListResponse(
        templates=[DocumentTemplateOut.model_validate(t) for t in templates],
        total=total,
    )


# ─── Document Summary ───────────────────────────────────────────────────────

async def get_document_summary(
    db: AsyncSession,
    compliance_id: int
) -> DocumentSummary:
    """Get summary of all documents for a compliance record"""
    # Get compliance documents
    compliance_docs_result = await db.execute(
        select(ComplianceDocument).where(
            and_(
                ComplianceDocument.compliance_id == compliance_id,
                ComplianceDocument.is_deleted == False
            )
        )
    )
    compliance_docs = compliance_docs_result.scalars().all()

    # Get client documents
    client_docs_result = await db.execute(
        select(ClientUploadedDocument).where(
            and_(
                ClientUploadedDocument.compliance_id == compliance_id,
                ClientUploadedDocument.is_deleted == False
            )
        )
    )
    client_docs = client_docs_result.scalars().all()

    # Count by status
    verified_count = sum(1 for d in compliance_docs + client_docs if d.status == DocumentStatusEnum.VERIFIED)
    pending_count = sum(1 for d in compliance_docs + client_docs if d.status == DocumentStatusEnum.PENDING)
    rejected_count = sum(1 for d in compliance_docs + client_docs if d.status == DocumentStatusEnum.REJECTED)
    expired_count = sum(1 for d in compliance_docs + client_docs if d.status == DocumentStatusEnum.EXPIRED)

    return DocumentSummary(
        compliance_id=compliance_id,
        total_documents=len(compliance_docs) + len(client_docs),
        verified_documents=verified_count,
        pending_documents=pending_count,
        rejected_documents=rejected_count,
        expired_documents=expired_count,
        compliance_documents=[ComplianceDocumentOut.model_validate(d) for d in compliance_docs],
        client_documents=[ClientUploadedDocumentOut.model_validate(d) for d in client_docs],
    )
