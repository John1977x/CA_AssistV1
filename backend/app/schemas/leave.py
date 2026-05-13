from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


LEAVE_TYPES = ["Annual", "Sick", "Casual", "Maternity", "Paternity", "Emergency", "Unpaid", "Compensatory", "Other"]
CALCULATIONS = ["MONTHLY", "YEARLY", "QUARTERLY"]
LEAVE_STATUSES = ["PENDING", "APPROVED", "REJECTED"]


# ─── Leave Master ─────────────────────────────────────────────────────────────

class LeaveMasterCreate(BaseModel):
    leave_type:    str = Field(..., min_length=1, max_length=100)
    entitled:      int = Field(..., ge=0)
    calendar_year: int = Field(..., ge=2000, le=2100)
    calculation:   str = Field(..., min_length=1, max_length=50)


class LeaveMasterUpdate(BaseModel):
    leave_type:    Optional[str] = Field(None, min_length=1, max_length=100)
    entitled:      Optional[int] = Field(None, ge=0)
    calendar_year: Optional[int] = Field(None, ge=2000, le=2100)
    calculation:   Optional[str] = Field(None, min_length=1, max_length=50)


class LeaveMasterOut(BaseModel):
    leave_master_id: int
    tenant_id:       int
    leave_type:      str
    entitled:        int
    calendar_year:   int
    calculation:     str
    created_at:      datetime
    updated_at:      datetime

    model_config = {"from_attributes": True}


class PaginatedLeaveMasters(BaseModel):
    items:       List[LeaveMasterOut]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


# ─── Leave Application ────────────────────────────────────────────────────────

class LeaveApplicationCreate(BaseModel):
    leave_type:     str  = Field(..., min_length=1, max_length=100)
    leave_date:     date
    from_date:      date
    to_date:        date
    reason:         Optional[str] = None
    attachment_url: Optional[str] = Field(None, max_length=500)
    approver_id:    Optional[int] = None


class LeaveApplicationUpdate(BaseModel):
    leave_type:     Optional[str]  = Field(None, min_length=1, max_length=100)
    leave_date:     Optional[date] = None
    from_date:      Optional[date] = None
    to_date:        Optional[date] = None
    reason:         Optional[str]  = None
    attachment_url: Optional[str]  = Field(None, max_length=500)
    approver_id:    Optional[int]  = None
    status:         Optional[str]  = None
    approval_notes: Optional[str]  = None


class LeaveApplicationOut(BaseModel):
    leave_application_id: int
    tenant_id:            int
    employee_id:          int
    leave_type:           str
    leave_date:           date
    from_date:            date
    to_date:              date
    reason:               Optional[str] = None
    attachment_url:       Optional[str] = None
    approver_id:          Optional[int] = None
    status:               str
    approval_notes:       Optional[str] = None
    employee_name:        Optional[str] = None
    approver_name:        Optional[str] = None
    created_at:           datetime
    updated_at:           datetime

    model_config = {"from_attributes": True}


class PaginatedLeaveApplications(BaseModel):
    items:       List[LeaveApplicationOut]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


class ApproverOut(BaseModel):
    user_id: int
    name:    str
