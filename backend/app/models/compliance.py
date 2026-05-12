from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Compliance(Base):
    """Compliance records for clients/candidates with PAN, TAN, and other details"""
    __tablename__ = "compliance"

    compliance_id           = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    customer_id             = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    
    # Compliance Type
    compliance_type         = Column(String(50), nullable=False)  # GST, ITR, TDS, ROC, AUDIT, PAYROLL, etc.
    compliance_code         = Column(String(30), nullable=False)  # Unique code for this compliance
    
    # PAN & TAN Details
    pan                     = Column(String(10))
    tan                     = Column(String(10))
    
    # GST Details
    gstin                   = Column(String(15))
    gst_registration_type   = Column(String(30))  # REGULAR, COMPOSITION, UNREGISTERED
    gst_registration_date   = Column(Date)
    gst_cancellation_date   = Column(Date)
    
    # TDS Details
    tds_deductor_type       = Column(String(50))  # INDIVIDUAL, COMPANY, PARTNERSHIP, etc.
    tds_circle_code         = Column(String(20))
    
    # ROC Details
    cin                     = Column(String(21))  # Corporate Identification Number
    company_registration_date = Column(Date)
    
    # Financial Details
    financial_year          = Column(String(7))   # 2024-25
    financial_year_start    = Column(Integer)     # Month (1-12)
    financial_year_end      = Column(Integer)     # Month (1-12)
    
    # Compliance Status
    status                  = Column(String(30), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, SUSPENDED, CLOSED
    compliance_status       = Column(String(30), nullable=False, default="PENDING")  # PENDING, IN_PROGRESS, COMPLIANT, NON_COMPLIANT, EXEMPTED
    
    # Filing Details
    last_filing_date        = Column(Date)
    next_filing_date        = Column(Date)
    filing_frequency        = Column(String(20))  # MONTHLY, QUARTERLY, ANNUAL, BIANNUAL
    
    # Documents & References
    registration_number     = Column(String(100))
    registration_certificate_url = Column(Text)
    documents_json          = Column(JSONB)  # Array of document URLs and metadata
    
    # Contact & Address
    contact_person_name     = Column(String(200))
    contact_person_email    = Column(String(150))
    contact_person_phone    = Column(String(15))
    registered_address      = Column(Text)
    
    # Additional Details
    notes                   = Column(Text)
    custom_fields_json      = Column(JSONB)  # For extensibility
    
    # Audit Trail
    created_by_user_id      = Column(Integer, ForeignKey("user.user_id"))
    updated_by_user_id      = Column(Integer, ForeignKey("user.user_id"))
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    # Relationships
    tenant                  = relationship("Tenant")
    customer                = relationship("Customer")
    created_by              = relationship("User", foreign_keys=[created_by_user_id])
    updated_by              = relationship("User", foreign_keys=[updated_by_user_id])
    tasks                   = relationship("ComplianceTask", back_populates="compliance", cascade="all, delete-orphan")


class ComplianceTask(Base):
    """Link between Compliance and Task - tracks which task is assigned for which compliance"""
    __tablename__ = "compliance_task"

    compliance_task_id      = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id           = Column(Integer, ForeignKey("compliance.compliance_id"), nullable=False)
    task_id                 = Column(Integer, ForeignKey("task.task_id"), nullable=False)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    
    # Assignment Details
    assigned_to_user_id     = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    assigned_by_user_id     = Column(Integer, ForeignKey("user.user_id"))
    
    # Task Specific Details
    task_type               = Column(String(60), nullable=False)  # FILING, DOCUMENTATION, VERIFICATION, REMEDIATION, etc.
    description             = Column(Text)
    
    # Dates
    assigned_date           = Column(Date, nullable=False, server_default=func.now())
    due_date                = Column(Date, nullable=False)
    completed_date          = Column(Date)
    
    # Status & Progress
    status                  = Column(String(30), nullable=False, default="ASSIGNED")  # ASSIGNED, IN_PROGRESS, SUBMITTED, APPROVED, REJECTED, COMPLETED
    completion_percentage   = Column(Integer, nullable=False, default=0)
    
    # Compliance Specific
    compliance_requirement  = Column(String(200))  # What compliance requirement this task fulfills
    documents_required      = Column(ARRAY(String))  # List of required documents
    documents_submitted_json = Column(JSONB)  # Submitted documents with URLs
    
    # Review & Approval
    reviewed_by_user_id     = Column(Integer, ForeignKey("user.user_id"))
    reviewed_date           = Column(Date)
    review_comments         = Column(Text)
    
    # Audit Trail
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    # Relationships
    compliance              = relationship("Compliance", back_populates="tasks")
    task                    = relationship("Task")
    tenant                  = relationship("Tenant")
    assigned_to             = relationship("User", foreign_keys=[assigned_to_user_id])
    assigned_by             = relationship("User", foreign_keys=[assigned_by_user_id])
    reviewed_by             = relationship("User", foreign_keys=[reviewed_by_user_id])


class ComplianceHistory(Base):
    """Audit trail for compliance changes"""
    __tablename__ = "compliance_history"

    history_id              = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id           = Column(Integer, ForeignKey("compliance.compliance_id"), nullable=False)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    
    # Change Details
    action                  = Column(String(50), nullable=False)  # CREATED, UPDATED, STATUS_CHANGED, FILED, EXEMPTED, etc.
    field_name              = Column(String(100))  # Which field was changed
    old_value               = Column(Text)
    new_value               = Column(Text)
    
    # User & Context
    changed_by_user_id      = Column(Integer, ForeignKey("user.user_id"))
    change_reason           = Column(Text)
    
    # Metadata
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    compliance              = relationship("Compliance")
    tenant                  = relationship("Tenant")
    changed_by              = relationship("User")


class ComplianceReminder(Base):
    """Reminders for upcoming compliance deadlines"""
    __tablename__ = "compliance_reminder"

    reminder_id             = Column(Integer, primary_key=True, autoincrement=True)
    compliance_id           = Column(Integer, ForeignKey("compliance.compliance_id"), nullable=False)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    
    # Reminder Details
    reminder_type           = Column(String(30), nullable=False)  # FILING_DUE, DOCUMENT_EXPIRY, RENEWAL_DUE, etc.
    reminder_date           = Column(Date, nullable=False)
    days_before_due         = Column(Integer)  # Remind X days before due date
    
    # Notification
    notify_user_ids         = Column(ARRAY(String))  # UUIDs of users to notify
    notification_channels   = Column(ARRAY(String))  # EMAIL, SMS, IN_APP, etc.
    
    # Status
    status                  = Column(String(20), nullable=False, default="PENDING")  # PENDING, SENT, ACKNOWLEDGED, COMPLETED
    sent_at                 = Column(DateTime(timezone=True))
    acknowledged_at         = Column(DateTime(timezone=True))
    
    # Metadata
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    compliance              = relationship("Compliance")
    tenant                  = relationship("Tenant")
