"""
Compliance Document Schemas - Request/Response models for compliance documents
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class DocumentTypeEnum(str, Enum):
    """Types of compliance documents"""
    PAN = "pan"
    TAN = "tan"
    GSTIN = "gstin"
    CIN = "cin"
    AADHAR = "aadhar"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    BANK_STATEMENT = "bank_statement"
    UTILITY_BILL = "utility_bill"
    RENT_AGREEMENT = "rent_agreement"
    PROPERTY_DEED = "property_deed"
    COMPANY_REGISTRATION = "company_registration"
    PARTNERSHIP_DEED = "partnership_deed"
    MOA_AOA = "moa_aoa"
    BOARD_RESOLUTION = "board_resolution"
    DIRECTOR_IDENTIFICATION = "director_identification"
    AUDITOR_CERTIFICATE = "auditor_certificate"
    FINANCIAL_STATEMENT = "financial_statement"
    ITR = "itr"
    GST_RETURN = "gst_return"
    TDS_CERTIFICATE = "tds_certificate"
    FORM_16 = "form_16"
    FORM_26AS = "form_26as"
    CUSTOM = "custom"


class DocumentStatusEnum(str, Enum):
    """Status of compliance documents"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


# ─── Compliance Document Schemas ─────────────────────────────────────────────

class ComplianceDocumentCreate(BaseModel):
    """Create compliance document request"""
    document_type: DocumentTypeEnum
    document_name: str = Field(..., min_length=1, max_length=200)
    document_number: Optional[str] = None
    file_url: str
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    access_url: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class ComplianceDocumentUpdate(BaseModel):
    """Update compliance document request"""
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    access_url: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[dict] = None


class ComplianceDocumentVerify(BaseModel):
    """Verify compliance document request"""
    status: DocumentStatusEnum
    verification_notes: Optional[str] = None


class ComplianceDocumentOut(BaseModel):
    """Compliance document response"""
    document_id: int
    compliance_id: int
    document_type: DocumentTypeEnum
    document_name: str
    document_number: Optional[str]
    file_url: str
    file_name: str
    file_size: Optional[int]
    file_type: Optional[str]
    username: Optional[str]
    access_url: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]
    is_active: bool
    status: DocumentStatusEnum
    verified_by_user_id: Optional[int]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    description: Optional[str]
    metadata: Optional[dict]
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceDocumentListResponse(BaseModel):
    """List compliance documents response"""
    documents: List[ComplianceDocumentOut]
    total: int
    page: int
    page_size: int


# ─── Client Uploaded Document Schemas ────────────────────────────────────────

class ClientUploadedDocumentCreate(BaseModel):
    """Create client uploaded document request"""
    document_type: DocumentTypeEnum
    document_name: str = Field(..., min_length=1, max_length=200)
    document_number: Optional[str] = None
    file_url: str
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    access_url: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class ClientUploadedDocumentUpdate(BaseModel):
    """Update client uploaded document request"""
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    access_url: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class ClientUploadedDocumentOut(BaseModel):
    """Client uploaded document response"""
    upload_id: int
    compliance_id: int
    client_id: int
    document_type: DocumentTypeEnum
    document_name: str
    document_number: Optional[str]
    file_url: str
    file_name: str
    file_size: Optional[int]
    file_type: Optional[str]
    username: Optional[str]
    access_url: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]
    status: DocumentStatusEnum
    verified_by_user_id: Optional[int]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    rejection_reason: Optional[str]
    description: Optional[str]
    metadata: Optional[dict]
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientUploadedDocumentListResponse(BaseModel):
    """List client uploaded documents response"""
    documents: List[ClientUploadedDocumentOut]
    total: int
    page: int
    page_size: int


# ─── Document Template Schemas ───────────────────────────────────────────────

class DocumentTemplateOut(BaseModel):
    """Document template response"""
    template_id: int
    document_type: DocumentTypeEnum
    display_name: str
    description: Optional[str]
    is_mandatory: bool
    is_recurring: bool
    renewal_frequency: Optional[str]
    accepted_file_types: Optional[str]
    max_file_size: Optional[int]
    is_active: bool
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentTemplateListResponse(BaseModel):
    """List document templates response"""
    templates: List[DocumentTemplateOut]
    total: int


# ─── Document Summary Schemas ────────────────────────────────────────────────

class DocumentSummary(BaseModel):
    """Summary of all documents for a compliance record"""
    compliance_id: int
    total_documents: int
    verified_documents: int
    pending_documents: int
    rejected_documents: int
    expired_documents: int
    compliance_documents: List[ComplianceDocumentOut]
    client_documents: List[ClientUploadedDocumentOut]
