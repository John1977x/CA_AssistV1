from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# ─── Compliance Schemas ──────────────────────────────────────────────────────

class ComplianceBase(BaseModel):
    """Base compliance schema"""
    compliance_type: str = Field(..., description="GST, ITR, TDS, ROC, AUDIT, PAYROLL, etc.")
    compliance_code: str = Field(..., description="Unique code for this compliance")
    pan: Optional[str] = None
    tan: Optional[str] = None
    gstin: Optional[str] = None
    gst_registration_type: Optional[str] = None
    gst_registration_date: Optional[date] = None
    gst_cancellation_date: Optional[date] = None
    tds_deductor_type: Optional[str] = None
    tds_circle_code: Optional[str] = None
    cin: Optional[str] = None
    company_registration_date: Optional[date] = None
    financial_year: Optional[str] = None
    financial_year_start: Optional[int] = None
    financial_year_end: Optional[int] = None
    status: str = "ACTIVE"
    compliance_status: str = "PENDING"
    last_filing_date: Optional[date] = None
    next_filing_date: Optional[date] = None
    filing_frequency: Optional[str] = None
    registration_number: Optional[str] = None
    registration_certificate_url: Optional[str] = None
    documents_json: Optional[Dict[str, Any]] = None
    contact_person_name: Optional[str] = None
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[str] = None
    registered_address: Optional[str] = None
    notes: Optional[str] = None
    custom_fields_json: Optional[Dict[str, Any]] = None


class ComplianceCreate(ComplianceBase):
    """Create compliance request"""
    customer_id: UUID


class ComplianceUpdate(BaseModel):
    """Update compliance request"""
    compliance_type: Optional[str] = None
    compliance_code: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    gstin: Optional[str] = None
    gst_registration_type: Optional[str] = None
    gst_registration_date: Optional[date] = None
    gst_cancellation_date: Optional[date] = None
    tds_deductor_type: Optional[str] = None
    tds_circle_code: Optional[str] = None
    cin: Optional[str] = None
    company_registration_date: Optional[date] = None
    financial_year: Optional[str] = None
    financial_year_start: Optional[int] = None
    financial_year_end: Optional[int] = None
    status: Optional[str] = None
    compliance_status: Optional[str] = None
    last_filing_date: Optional[date] = None
    next_filing_date: Optional[date] = None
    filing_frequency: Optional[str] = None
    registration_number: Optional[str] = None
    registration_certificate_url: Optional[str] = None
    documents_json: Optional[Dict[str, Any]] = None
    contact_person_name: Optional[str] = None
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[str] = None
    registered_address: Optional[str] = None
    notes: Optional[str] = None
    custom_fields_json: Optional[Dict[str, Any]] = None


class ComplianceResponse(ComplianceBase):
    """Compliance response"""
    compliance_id: UUID
    tenant_id: UUID
    customer_id: UUID
    created_by_user_id: Optional[UUID] = None
    updated_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


# ─── Compliance Task Schemas ─────────────────────────────────────────────────

class ComplianceTaskBase(BaseModel):
    """Base compliance task schema"""
    task_type: str = Field(..., description="FILING, DOCUMENTATION, VERIFICATION, REMEDIATION, etc.")
    description: Optional[str] = None
    due_date: date
    status: str = "ASSIGNED"
    completion_percentage: int = 0
    compliance_requirement: Optional[str] = None
    documents_required: Optional[List[str]] = None
    documents_submitted_json: Optional[Dict[str, Any]] = None
    review_comments: Optional[str] = None


class ComplianceTaskCreate(ComplianceTaskBase):
    """Create compliance task request"""
    compliance_id: UUID
    task_id: UUID
    assigned_to_user_id: UUID
    assigned_by_user_id: Optional[UUID] = None


class ComplianceTaskUpdate(BaseModel):
    """Update compliance task request"""
    task_type: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    completion_percentage: Optional[int] = None
    compliance_requirement: Optional[str] = None
    documents_required: Optional[List[str]] = None
    documents_submitted_json: Optional[Dict[str, Any]] = None
    review_comments: Optional[str] = None


class ComplianceTaskResponse(ComplianceTaskBase):
    """Compliance task response"""
    compliance_task_id: UUID
    compliance_id: UUID
    task_id: UUID
    tenant_id: UUID
    assigned_to_user_id: UUID
    assigned_by_user_id: Optional[UUID] = None
    assigned_date: date
    completed_date: Optional[date] = None
    reviewed_by_user_id: Optional[UUID] = None
    reviewed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


# ─── Compliance History Schemas ──────────────────────────────────────────────

class ComplianceHistoryResponse(BaseModel):
    """Compliance history response"""
    history_id: UUID
    compliance_id: UUID
    tenant_id: UUID
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by_user_id: Optional[UUID] = None
    change_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Compliance Reminder Schemas ─────────────────────────────────────────────

class ComplianceReminderBase(BaseModel):
    """Base compliance reminder schema"""
    reminder_type: str = Field(..., description="FILING_DUE, DOCUMENT_EXPIRY, RENEWAL_DUE, etc.")
    reminder_date: date
    days_before_due: Optional[int] = None
    notify_user_ids: Optional[List[str]] = None
    notification_channels: Optional[List[str]] = None


class ComplianceReminderCreate(ComplianceReminderBase):
    """Create compliance reminder request"""
    compliance_id: UUID


class ComplianceReminderUpdate(BaseModel):
    """Update compliance reminder request"""
    reminder_type: Optional[str] = None
    reminder_date: Optional[date] = None
    days_before_due: Optional[int] = None
    notify_user_ids: Optional[List[str]] = None
    notification_channels: Optional[List[str]] = None
    status: Optional[str] = None


class ComplianceReminderResponse(ComplianceReminderBase):
    """Compliance reminder response"""
    reminder_id: UUID
    compliance_id: UUID
    tenant_id: UUID
    status: str
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Compliance Dashboard Schemas ────────────────────────────────────────────

class ComplianceSummary(BaseModel):
    """Compliance summary for dashboard"""
    total_compliances: int
    active_compliances: int
    pending_compliances: int
    compliant_count: int
    non_compliant_count: int
    upcoming_filings: int
    overdue_tasks: int


class ComplianceTaskSummary(BaseModel):
    """Compliance task summary"""
    total_tasks: int
    assigned_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    pending_review_tasks: int
    overdue_tasks: int


class ComplianceDetailedResponse(ComplianceResponse):
    """Detailed compliance response with related tasks"""
    tasks: List[ComplianceTaskResponse] = []
    history: List[ComplianceHistoryResponse] = []
    reminders: List[ComplianceReminderResponse] = []

    class Config:
        from_attributes = True
