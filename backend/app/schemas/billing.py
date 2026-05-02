from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal


# ─── Line Item ────────────────────────────────────────────────────────────────

class LineItemCreate(BaseModel):
    description:    str = Field(..., min_length=2)
    hsn_sac_code:   Optional[str] = "998231"   # default SAC for CA services
    quantity:       float = 1.0
    unit:           Optional[str] = "flat"      # hrs, months, flat
    unit_price:     float = Field(..., gt=0)
    discount_pct:   float = 0.0
    gst_rate_pct:   float = 18.0
    task_id:        Optional[int] = None
    sort_order:     int = 0


class LineItemOut(BaseModel):
    line_item_id:   int
    description:    str
    hsn_sac_code:   Optional[str]
    quantity:       float
    unit:           Optional[str]
    unit_price:     float
    discount_pct:   float
    taxable_amount: float
    gst_rate_pct:   float
    cgst_amount:    float
    sgst_amount:    float
    igst_amount:    float
    line_total:     float
    sort_order:     int
    task_id:        Optional[int]
    model_config = {"from_attributes": True}


# ─── Invoice ─────────────────────────────────────────────────────────────────

class InvoiceCreate(BaseModel):
    customer_id:        int
    invoice_date:       date
    due_date:           date
    task_id:            Optional[int] = None
    branch_id:          Optional[int] = None
    place_of_supply:    Optional[str] = None
    is_igst:            bool = False
    gst_rate_pct:       float = 18.0
    discount_pct:       float = 0.0
    payment_terms_days: int = 30
    notes:              Optional[str] = None
    terms_conditions:   Optional[str] = None
    internal_notes:     Optional[str] = None
    line_items:         List[LineItemCreate] = Field(default_factory=list)


class InvoiceUpdate(BaseModel):
    invoice_date:       Optional[date] = None
    due_date:           Optional[date] = None
    status:             Optional[str] = None
    place_of_supply:    Optional[str] = None
    is_igst:            Optional[bool] = None
    gst_rate_pct:       Optional[float] = None
    discount_pct:       Optional[float] = None
    notes:              Optional[str] = None
    terms_conditions:   Optional[str] = None
    internal_notes:     Optional[str] = None
    tally_voucher_number: Optional[str] = None


class CustomerBrief(BaseModel):
    customer_id:    int
    display_name:   str
    gstin:          Optional[str]
    pan:            Optional[str]
    phone:          str
    email:          Optional[str]
    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    user_id:        int
    display_name:   Optional[str]
    email:          str
    model_config = {"from_attributes": True}


class InvoiceOut(BaseModel):
    invoice_id:         int
    tenant_id:          int
    customer_id:        int
    invoice_number:     str
    invoice_date:       date
    due_date:           date
    subtotal:           float
    discount_amount:    float
    taxable_amount:     float
    cgst_amount:        float
    sgst_amount:        float
    igst_amount:        float
    total_tax:          float
    total_amount:       float
    amount_paid:        float
    balance_due:        float
    currency_code:      str
    is_igst:            bool
    gst_rate_pct:       float
    status:             str
    payment_terms_days: int
    notes:              Optional[str]
    terms_conditions:   Optional[str]
    tally_voucher_number: Optional[str]
    tally_synced_at:    Optional[datetime]
    sent_at:            Optional[datetime]
    task_id:            Optional[int]
    branch_id:          Optional[int]
    created_at:         datetime
    updated_at:         datetime
    # Relationships removed to avoid greenlet errors
    # customer: Optional[CustomerBrief] = None
    # created_by: Optional[UserBrief] = None
    # line_items: Optional[List[LineItemOut]] = None
    model_config = {"from_attributes": True}


class InvoiceListOut(BaseModel):
    invoice_id:     int
    invoice_number: str
    invoice_date:   date
    due_date:       date
    total_amount:   float
    amount_paid:    float
    balance_due:    float
    status:         str
    customer_id:    int
    # Relationships removed to avoid greenlet errors
    # customer: Optional[CustomerBrief] = None
    created_at:     datetime
    model_config = {"from_attributes": True}


# ─── Time Log ────────────────────────────────────────────────────────────────

class TimeLogCreate(BaseModel):
    customer_id:        int
    task_id:            Optional[int] = None
    log_date:           date
    start_time:         Optional[str] = None    # HH:MM
    end_time:           Optional[str] = None
    duration_minutes:   int = Field(..., gt=0)
    description:        str = Field(..., min_length=2)
    is_billable:        bool = True
    hourly_rate:        Optional[float] = None


class TimeLogUpdate(BaseModel):
    log_date:           Optional[date] = None
    duration_minutes:   Optional[int] = None
    description:        Optional[str] = None
    is_billable:        Optional[bool] = None
    hourly_rate:        Optional[float] = None
    task_id:            Optional[int] = None


class TimeLogOut(BaseModel):
    time_log_id:        int
    tenant_id:          int
    user_id:            int
    customer_id:        int
    task_id:            Optional[int]
    log_date:           date
    start_time:         Optional[str]
    end_time:           Optional[str]
    duration_minutes:   int
    billable_minutes:   int
    description:        str
    is_billable:        bool
    is_billed:          bool
    hourly_rate:        Optional[float]
    line_amount:        Optional[float]
    invoice_id:         Optional[int]
    created_at:         datetime
    # Relationships removed to avoid greenlet errors
    # user: Optional[UserBrief] = None
    # customer: Optional[CustomerBrief] = None
    model_config = {"from_attributes": True}


# ─── Expense ─────────────────────────────────────────────────────────────────

EXPENSE_CATEGORIES = [
    "TRAVEL", "FILING_FEE", "OFFICE_SUPPLIES", "COURIER",
    "GOVERNMENT_FEE", "PROFESSIONAL_FEE", "MEALS", "SOFTWARE",
    "INTERNET", "PRINTING", "MISCELLANEOUS",
]

class ExpenseCreate(BaseModel):
    expense_date:   date
    category:       str
    description:    str = Field(..., min_length=2)
    amount:         float = Field(..., gt=0)
    gst_amount:     float = 0.0
    customer_id:    Optional[int] = None
    task_id:        Optional[int] = None
    is_billable:    bool = False
    payment_mode:   Optional[str] = None
    vendor_name:    Optional[str] = None
    receipt_url:    Optional[str] = None


class ExpenseUpdate(BaseModel):
    expense_date:   Optional[date] = None
    category:       Optional[str] = None
    description:    Optional[str] = None
    amount:         Optional[float] = None
    gst_amount:     Optional[float] = None
    status:         Optional[str] = None
    is_billable:    Optional[bool] = None
    vendor_name:    Optional[str] = None
    receipt_url:    Optional[str] = None


class ExpenseOut(BaseModel):
    expense_id:     int
    tenant_id:      int
    user_id:        int
    customer_id:    Optional[int]
    task_id:        Optional[int]
    expense_date:   date
    category:       str
    description:    str
    amount:         float
    gst_amount:     float
    total_amount:   float
    is_billable:    bool
    is_reimbursed:  bool
    payment_mode:   Optional[str]
    vendor_name:    Optional[str]
    receipt_url:    Optional[str]
    status:         str
    approved_at:    Optional[datetime]
    created_at:     datetime
    # Relationships removed to avoid greenlet errors
    # user: Optional[UserBrief] = None
    model_config = {"from_attributes": True}


# ─── Payment ────────────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    payment_date:       date
    amount:             float = Field(..., gt=0)
    payment_mode:       str
    reference_number:   Optional[str] = None
    bank_name:          Optional[str] = None
    notes:              Optional[str] = None
    tds_deducted:       float = 0.0


class PaymentOut(BaseModel):
    payment_id:         int
    invoice_id:         int
    customer_id:        int
    payment_date:       date
    amount:             float
    payment_mode:       str
    reference_number:   Optional[str]
    bank_name:          Optional[str]
    notes:              Optional[str]
    tds_deducted:       float
    net_received:       float
    created_at:         datetime
    # Relationships removed to avoid greenlet errors
    # recorded_by: Optional[UserBrief] = None
    model_config = {"from_attributes": True}


# ─── Stats & Reports ─────────────────────────────────────────────────────────

class BillingStats(BaseModel):
    total_invoiced:     float
    total_collected:    float
    total_outstanding:  float
    total_overdue:      float
    invoice_count:      int
    draft_count:        int
    overdue_count:      int
    unbilled_hours:     float
    this_month_revenue: float


# ─── Tally Export ─────────────────────────────────────────────────────────────

class TallyExportRequest(BaseModel):
    invoice_ids:    List[int]
    format:         str = "XML"   # XML or CSV


# ─── Shared ──────────────────────────────────────────────────────────────────

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
