from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class TenantCompany(Base):
    """Tenant Company - Companies owned/managed by the CA firm"""
    __tablename__ = "tenant_companies"

    company_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_code    = Column(String(20), nullable=False, unique=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    company_name    = Column(String(200), nullable=False, index=True)
    phone           = Column(String(20))
    address1        = Column(String(200))
    address2        = Column(String(200))
    city            = Column(String(100))
    state           = Column(String(100))
    pincode         = Column(String(10))
    country         = Column(String(100))
    status          = Column(String(1), nullable=False, default='Y')  # Y/N
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")


class CustomerCompany(Base):
    """Customer Company - Companies owned by customers"""
    __tablename__ = "customer_companies"

    company_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_code        = Column(String(20), nullable=False, unique=True)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    company_name        = Column(String(200), nullable=False, index=True)
    company_type        = Column(String(50))  # PRIVATE_LIMITED / LLP / PARTNERSHIP / SOLE_PROP / HUF / TRUST / NGO
    cin                 = Column(String(21), index=True)  # Company Identification Number
    pan                 = Column(String(10), index=True)
    tan                 = Column(String(10), index=True)
    gstin               = Column(String(15), index=True)
    incorporation_date  = Column(Date)
    registered_address  = Column(String(300))
    city                = Column(String(100))
    state               = Column(String(100))
    pincode             = Column(String(10))
    country             = Column(String(100))
    phone               = Column(String(20))
    email               = Column(String(150))
    is_primary          = Column(Boolean, nullable=False, default=False)  # 1 = primary company for this customer
    status              = Column(String(1), nullable=False, default='Y')
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    customer = relationship("Customer")
    tenant = relationship("Tenant")
    documents = relationship("ClientDocument", back_populates="company")
    # tasks relationship removed - Task model no longer has company_id column


class ClientDocument(Base):
    """Client Document - Documents for customers and their companies"""
    __tablename__ = "client_documents"

    client_doc_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id     = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    company_id      = Column(UUID(as_uuid=True), ForeignKey("customer_companies.company_id"), index=True)  # NULL = personal doc
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    document_type   = Column(String(50), nullable=False)  # COMPANY_CHARTER / PAN / TAN / AADHAR / GST / CIN / UDYAM / IEC / OTHER
    document_number = Column(String(50), index=True)  # e.g. PAN: ABCDE1234F
    document_name   = Column(String(200), nullable=False)  # Display name of file
    url             = Column(String(500), nullable=False)  # S3 / storage path
    size_kb         = Column(Integer)  # File size in KB
    issue_date      = Column(Date)
    expiry_date     = Column(Date)  # NULL = no expiry
    verified_by     = Column(Integer, ForeignKey("user.user_id"))  # CA who verified
    verified_at     = Column(DateTime(timezone=True))
    status          = Column(String(20), nullable=False, default='Active')  # Active / Expired / Rejected
    remarks         = Column(String(300))
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    customer = relationship("Customer")
    company = relationship("CustomerCompany", back_populates="documents")
    tenant = relationship("Tenant")
    verifier = relationship("User", foreign_keys=[verified_by])
