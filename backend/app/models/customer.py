from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class Customer(Base):
    __tablename__ = "customer"

    customer_id             = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    branch_id               = Column(Integer, ForeignKey("branch.branch_id"))
    assigned_user_id        = Column(Integer, ForeignKey("user.user_id"))
    customer_code           = Column(String(30), nullable=False)
    customer_type           = Column(String(30), nullable=False, default="INDIVIDUAL")
    display_name            = Column(String(200), nullable=False)
    legal_name              = Column(String(200))
    pan                     = Column(String(10))
    gstin                   = Column(String(15))
    aadhar_number           = Column(String(12))   # store masked/encrypted
    email                   = Column(String(150))
    phone                   = Column(String(15), nullable=False)
    alternate_phone         = Column(String(15))
    whatsapp                = Column(String(15))
    date_of_birth           = Column(Date)
    date_of_incorporation   = Column(Date)
    industry_code           = Column(String(60))
    source_channel          = Column(String(50))
    referred_by_customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    tags                    = Column(ARRAY(Text))
    portal_access           = Column(Boolean, nullable=False, default=False)
    portal_email            = Column(String(150))
    status                  = Column(String(20), nullable=False, default="ACTIVE")
    risk_level              = Column(String(10))
    kyc_status              = Column(String(20), nullable=False, default="PENDING")
    kyc_verified_at         = Column(DateTime(timezone=True))
    onboarded_at            = Column(Date)
    notes                   = Column(Text)
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    tenant          = relationship("Tenant")
    branch          = relationship("Branch")
    assigned_user   = relationship("User", foreign_keys=[assigned_user_id])
    referred_by     = relationship("Customer", remote_side="Customer.customer_id", foreign_keys=[referred_by_customer_id])
    details         = relationship("CustomerDetails", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    enquiries       = relationship("Enquiry", back_populates="converted_customer", foreign_keys="Enquiry.converted_customer_id")


class CustomerDetails(Base):
    __tablename__ = "customer_details"

    customer_detail_id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id                 = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, unique=True)
    registered_address_line1    = Column(String(250))
    registered_address_line2    = Column(String(250))
    registered_city             = Column(String(100))
    registered_state            = Column(String(100))
    registered_pincode          = Column(String(10))
    communication_address       = Column(Text)
    bank_name                   = Column(String(100))
    bank_account_number         = Column(String(20))   # encrypted
    bank_ifsc                   = Column(String(11))
    bank_account_type           = Column(String(20))
    income_tax_status           = Column(String(30))
    gst_registration_type       = Column(String(30))
    gst_registration_date       = Column(Date)
    gst_cancellation_date       = Column(Date)
    tds_deductor_type           = Column(String(50))
    director_partners_json      = Column(JSONB)
    filing_history_json         = Column(JSONB)
    documents_json              = Column(JSONB)
    custom_fields_json          = Column(JSONB)
    created_at                  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at                  = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="details")


class Enquiry(Base):
    __tablename__ = "enquiry"

    enquiry_id              = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    branch_id               = Column(Integer, ForeignKey("branch.branch_id"))
    assigned_to_user_id     = Column(Integer, ForeignKey("user.user_id"))
    enquiry_date            = Column(Date, nullable=False, server_default=func.current_date())
    enquiry_number          = Column(String(30), nullable=False)
    full_name               = Column(String(200), nullable=False)
    email                   = Column(String(150))
    phone                   = Column(String(15), nullable=False)
    company_name            = Column(String(200))
    service_interested      = Column(ARRAY(Text))
    source                  = Column(String(50))
    referred_by_customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    message                 = Column(Text)
    estimated_value         = Column(Numeric(10, 2))
    status                  = Column(String(20), nullable=False, default="NEW")
    follow_up_date          = Column(Date)
    follow_up_notes         = Column(Text)
    lost_reason             = Column(String(200))
    is_converted            = Column(Boolean, nullable=False, default=False)
    converted_customer_id   = Column(Integer, ForeignKey("customer.customer_id"))
    converted_at            = Column(DateTime(timezone=True))
    converted_by_user_id    = Column(Integer, ForeignKey("user.user_id"))
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant              = relationship("Tenant")
    branch              = relationship("Branch")
    assigned_to_user    = relationship("User", foreign_keys=[assigned_to_user_id])
    referred_by         = relationship("Customer", foreign_keys=[referred_by_customer_id])
    converted_customer  = relationship("Customer", back_populates="enquiries", foreign_keys=[converted_customer_id])
    converted_by_user   = relationship("User", foreign_keys=[converted_by_user_id])
