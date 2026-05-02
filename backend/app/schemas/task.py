from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime, date


TASK_TYPES = [
    "GSTR1", "GSTR3B", "GSTR9", "GSTR9C",
    "ITR1", "ITR2", "ITR3", "ITR4", "ITR5", "ITR6", "ITR7",
    "TDS_RETURN_24Q", "TDS_RETURN_26Q", "TDS_RETURN_27Q",
    "ROC_AOC4", "ROC_MGT7", "ROC_DIR3KYC",
    "AUDIT_TAX", "AUDIT_STAT", "AUDIT_INTERNAL",
    "PT_RETURN", "PF_RETURN", "ESIC_RETURN",
    "ADVANCE_TAX", "FORM_15CA", "CUSTOM",
]

TASK_STATUSES = [
    "PENDING", "IN_PROGRESS", "PENDING_DOCS",
    "UNDER_REVIEW", "COMPLETED", "FILED", "CANCELLED",
]

PRIORITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
BILLING_STATUSES = ["UNBILLED", "INVOICED", "PAID"]
STEP_STATUSES = ["PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", "BLOCKED"]


# ─── Brief refs ───────────────────────────────────────────────────────────────

class UserBrief(BaseModel):
    user_id:        int
    display_name:   Optional[str]
    email:          str
    model_config = {"from_attributes": True}


class CustomerBrief(BaseModel):
    customer_id:    int
    customer_code:  str
    display_name:   str
    pan:            Optional[str]
    phone:          str
    model_config = {"from_attributes": True}


# ─── TaskDetail ───────────────────────────────────────────────────────────────

class TaskDetailCreate(BaseModel):
    step_title:         str = Field(..., min_length=2, max_length=200)
    step_description:   Optional[str] = None
    step_order:         int = 0
    assigned_to_user_id: Optional[int] = None
    is_required:        bool = True
    is_client_action:   bool = False
    due_date:           Optional[date] = None


class TaskDetailUpdate(BaseModel):
    step_title:         Optional[str] = None
    step_description:   Optional[str] = None
    step_order:         Optional[int] = None
    assigned_to_user_id: Optional[int] = None
    status:             Optional[str] = None
    is_required:        Optional[bool] = None
    is_client_action:   Optional[bool] = None
    due_date:           Optional[date] = None
    notes_json:         Optional[List[Dict[str, Any]]] = None
    form_data_json:     Optional[Dict[str, Any]] = None


class TaskDetailOut(BaseModel):
    task_detail_id:     int
    task_id:            int
    step_title:         str
    step_description:   Optional[str]
    step_order:         int
    status:             str
    is_required:        bool
    is_client_action:   bool
    due_date:           Optional[date]
    completed_at:       Optional[datetime]
    notes_json:         Optional[List[Dict[str, Any]]]
    form_data_json:     Optional[Dict[str, Any]]
    attachments_json:   Optional[List[Dict[str, Any]]]
    assigned_to_user_id: Optional[int]
    completed_by_user_id: Optional[int]
    # Relationships removed to avoid greenlet errors
    # assigned_to: Optional[UserBrief] = None
    # completed_by: Optional[UserBrief] = None
    created_at:         datetime
    updated_at:         datetime
    model_config = {"from_attributes": True}


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    customer_id:            int
    task_type_code:         str
    task_title:             str = Field(..., min_length=2, max_length=300)
    description:            Optional[str] = None
    financial_year:         Optional[str] = None   # 2024-25
    return_period:          Optional[str] = None
    due_date:               date
    internal_due_date:      Optional[date] = None
    priority:               str = "MEDIUM"
    assigned_to_user_id:    Optional[int] = None
    reviewer_user_id:       Optional[int] = None
    branch_id:              Optional[int] = None
    estimated_hours:        Optional[float] = None
    tags:                   Optional[List[str]] = None
    parent_task_id:         Optional[int] = None
    # Optional checklist to create immediately
    steps:                  Optional[List[TaskDetailCreate]] = None


class TaskUpdate(BaseModel):
    task_title:             Optional[str] = None
    description:            Optional[str] = None
    due_date:               Optional[date] = None
    internal_due_date:      Optional[date] = None
    priority:               Optional[str] = None
    status:                 Optional[str] = None
    completion_percentage:  Optional[int] = Field(None, ge=0, le=100)
    assigned_to_user_id:    Optional[int] = None
    reviewer_user_id:       Optional[int] = None
    estimated_hours:        Optional[float] = None
    actual_hours:           Optional[float] = None
    billing_status:         Optional[str] = None
    billed_amount:          Optional[float] = None
    tags:                   Optional[List[str]] = None
    acknowledgement_number: Optional[str] = None


class TaskOut(BaseModel):
    task_id:                int
    tenant_id:              int
    customer_id:            int
    task_type_code:         str
    task_title:             str
    description:            Optional[str]
    financial_year:         Optional[str]
    return_period:          Optional[str]
    due_date:               date
    internal_due_date:      Optional[date]
    priority:               str
    status:                 str
    completion_percentage:  int
    billing_status:         str
    billed_amount:          Optional[float]
    estimated_hours:        Optional[float]
    actual_hours:           Optional[float]
    acknowledgement_number: Optional[str]
    filed_at:               Optional[datetime]
    filed_by_user_id:       Optional[int]
    tags:                   Optional[List[str]]
    branch_id:              Optional[int]
    parent_task_id:         Optional[int]
    assigned_to_user_id:    Optional[int]
    reviewer_user_id:       Optional[int]
    created_at:             datetime
    updated_at:             datetime
    # Relationships removed to avoid greenlet errors
    # customer: Optional[CustomerBrief] = None
    # assigned_to: Optional[UserBrief] = None
    # reviewer: Optional[UserBrief] = None
    # details: Optional[List[TaskDetailOut]] = None

    model_config = {"from_attributes": True}


class TaskListOut(BaseModel):
    task_id:                int
    task_type_code:         str
    task_title:             str
    financial_year:         Optional[str]
    return_period:          Optional[str]
    due_date:               date
    internal_due_date:      Optional[date]
    priority:               str
    status:                 str
    completion_percentage:  int
    billing_status:         str
    tags:                   Optional[List[str]]
    customer_id:            int
    assigned_to_user_id:    Optional[int]
    branch_id:              Optional[int]
    # Relationships removed to avoid greenlet errors
    # customer: Optional[CustomerBrief] = None
    # assigned_to: Optional[UserBrief] = None
    created_at:             datetime
    model_config = {"from_attributes": True}


# ─── Reminder ─────────────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    reminder_type:      str = "USER"     # USER or CUSTOMER
    target_user_id:     Optional[int] = None
    target_customer_id: Optional[int] = None
    channel:            str = "EMAIL"
    subject:            Optional[str] = None
    message_body:       str
    scheduled_at:       datetime
    is_recurring:       bool = False
    recurrence_rule:    Optional[str] = None


class ReminderOut(BaseModel):
    reminder_id:        int
    task_id:            int
    reminder_type:      str
    channel:            str
    subject:            Optional[str]
    message_body:       str
    scheduled_at:       datetime
    sent_at:            Optional[datetime]
    delivery_status:    str
    is_recurring:       bool
    is_acknowledged:    bool
    created_at:         datetime
    model_config = {"from_attributes": True}


# ─── Stats ─────────────────────────────────────────────────────────────────────

class TaskStats(BaseModel):
    total:              int
    pending:            int
    in_progress:        int
    completed:          int
    overdue:            int
    due_today:          int
    due_this_week:      int
    by_status:          Dict[str, int]
    by_priority:        Dict[str, int]
    by_type:            Dict[str, int]


# ─── Shared ────────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items:          List[Any]
    total:          int
    page:           int
    page_size:      int
    total_pages:    int


class MessageResponse(BaseModel):
    message:    str
    success:    bool = True
    data:       Optional[Any] = None
