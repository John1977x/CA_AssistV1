"""
Compliance Document Models - For storing and managing compliance documents
"""

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, Text, func, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.db.session import Base


class DocumentTypeEnum(str, enum.Enum):
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
    MOA_AOA = "moa_aoa"  # Memorandum and Articles of Association
    BOARD_RESOLUTION = "board_resolution"
    DIRECTOR_IDENTIFICATION = "director_identification"
    AUDITOR_CERTIFICATE = "auditor_certificate"
    FINANCIAL_STATEMENT = "financial_statement"
    ITR = "itr"  # Income Tax Return
    GST_RETURN = "gst_return"
    TDS_CERTIFICATE = "tds_certificate"
    FORM_16 = "form_16"
    FORM_26AS = "form_26as"
    CUSTOM = "custom"


class DocumentStatusEnum(str, enum.Enum):
    """Status of compliance documents"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ComplianceDocument(Base):
    """
    Compliance Documents - Stores documents for compliance records
    Supports multiple document types with separate credentials for each
    """
    __tablename__ = "compliance_document"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id = Column(Integer, ForeignKey("compliance.compliance_id"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(SQLEnum(DocumentTypeEnum), nullable=False, index=True)
    document_name = Column(String(200), nullable=False)
    document_number = Column(String(100))  # PAN, TAN, GSTIN, etc.
    
    # File Information
    file_url = Column(Text, nullable=False)  # S3 or storage URL
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # In bytes
    file_type = Column(String(50))  # pdf, jpg, png, etc.
    
    # Document Credentials (separate username for each document)
    username = Column(String(200))  # Username for accessing this document
    password_hash = Column(Text)  # Hashed password for accessing this document
    access_url = Column(Text)  # URL to access the document (e.g., portal login)
    
    # Document Validity
    issue_date = Column(Date)
    expiry_date = Column(Date)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Status & Verification
    status = Column(SQLEnum(DocumentStatusEnum), nullable=False, default=DocumentStatusEnum.PENDING)
    verified_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    verified_at = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    
    # Additional Information
    description = Column(Text)
    metadata = Column(JSONB, default={})  # Additional data like issuing authority, etc.
    
    # Audit Trail
    uploaded_by_user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Soft Delete
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by_user_id = Column(Integer, ForeignKey("user.user_id"))

    # Relationships
    compliance = relationship("Compliance", foreign_keys=[compliance_id])
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])
    deleted_by = relationship("User", foreign_keys=[deleted_by_user_id])

    def __repr__(self):
        return f"<ComplianceDocument {self.document_id}: {self.document_type}>"


class ClientUploadedDocument(Base):
    """
    Client Uploaded Documents - Documents uploaded by clients for compliance
    Allows clients to upload their own documents with separate credentials
    """
    __tablename__ = "client_uploaded_document"

    upload_id = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id = Column(Integer, ForeignKey("compliance.compliance_id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    
    # Document Details
    document_type = Column(SQLEnum(DocumentTypeEnum), nullable=False)
    document_name = Column(String(200), nullable=False)
    document_number = Column(String(100))
    
    # File Information
    file_url = Column(Text, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    
    # Client Credentials (separate for each document)
    username = Column(String(200))  # Client's username for this document
    password_hash = Column(Text)  # Hashed password
    access_url = Column(Text)  # URL to access the document
    
    # Document Validity
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    # Status & Verification
    status = Column(SQLEnum(DocumentStatusEnum), nullable=False, default=DocumentStatusEnum.PENDING)
    verified_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    verified_at = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Additional Information
    description = Column(Text)
    metadata = Column(JSONB, default={})
    
    # Audit Trail
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Soft Delete
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    compliance = relationship("Compliance", foreign_keys=[compliance_id])
    client = relationship("Customer", foreign_keys=[client_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])

    def __repr__(self):
        return f"<ClientUploadedDocument {self.upload_id}: {self.document_type}>"


class DocumentTemplate(Base):
    """
    Document Templates - Pre-configured document types for compliance
    Helps standardize document collection across clients
    """
    __tablename__ = "document_template"

    template_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Template Details
    document_type = Column(SQLEnum(DocumentTypeEnum), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Requirements
    is_mandatory = Column(Boolean, nullable=False, default=False)
    is_recurring = Column(Boolean, nullable=False, default=False)  # Needs renewal
    renewal_frequency = Column(String(50))  # ANNUAL, BIANNUAL, MONTHLY, etc.
    
    # Validation Rules
    accepted_file_types = Column(String(200))  # pdf, jpg, png, etc.
    max_file_size = Column(Integer)  # In MB
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DocumentTemplate {self.template_id}: {self.document_type}>"
