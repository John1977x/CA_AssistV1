from fastapi import APIRouter, Depends, Query, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.auth import User
from app.schemas.billing import (
    InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceListOut,
    TimeLogCreate, TimeLogUpdate, TimeLogOut,
    ExpenseCreate, ExpenseUpdate, ExpenseOut,
    PaymentCreate, PaymentOut,
    TallyExportRequest,
    PaginatedResponse, MessageResponse,
)
from app.services import billing as svc

router = APIRouter(prefix="/billing", tags=["Billing"])


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def billing_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await svc.get_billing_stats(db, current_user.tenant_id)


# ─── Invoices ────────────────────────────────────────────────────────────────

@router.get("/invoices", response_model=PaginatedResponse)
async def list_invoices(
    page:         int           = Query(1, ge=1),
    page_size:    int           = Query(20, ge=1, le=100),
    search:       Optional[str] = Query(None),
    status:       Optional[str] = Query(None),
    customer_id:  Optional[int] = Query(None),
    overdue_only: bool          = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    invoices, total = await svc.get_invoices(
        db, current_user.tenant_id, page, page_size, search, status, customer_id, overdue_only
    )
    return PaginatedResponse(
        items=[InvoiceListOut.model_validate(i) for i in invoices],
        total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = await svc.create_invoice(db, current_user.tenant_id, data, current_user.user_id)
    return InvoiceOut.model_validate(inv)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = await svc.get_invoice(db, current_user.tenant_id, invoice_id)
    return InvoiceOut.model_validate(inv)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(
    data: InvoiceUpdate,
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = await svc.update_invoice(db, current_user.tenant_id, invoice_id, data)
    return InvoiceOut.model_validate(inv)


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceOut)
async def send_invoice(
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = await svc.send_invoice(db, current_user.tenant_id, invoice_id, current_user.user_id)
    return InvoiceOut.model_validate(inv)


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceOut)
async def cancel_invoice(
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = await svc.cancel_invoice(db, current_user.tenant_id, invoice_id)
    return InvoiceOut.model_validate(inv)


@router.delete("/invoices/{invoice_id}", response_model=MessageResponse)
async def delete_invoice(
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_invoice(db, current_user.tenant_id, invoice_id)
    return MessageResponse(message="Invoice deleted.")


# ─── Payments ────────────────────────────────────────────────────────────────

@router.post("/invoices/{invoice_id}/payments", response_model=PaymentOut, status_code=201)
async def record_payment(
    data: PaymentCreate,
    invoice_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    payment = await svc.record_payment(
        db, current_user.tenant_id, invoice_id, data, current_user.user_id
    )
    return PaymentOut.model_validate(payment)


# ─── Tally Export ─────────────────────────────────────────────────────────────

@router.post("/invoices/tally-export")
async def tally_export(
    data: TallyExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    xml = await svc.generate_tally_xml(db, current_user.tenant_id, data.invoice_ids)
    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=tally_export.xml"},
    )


# ─── Time Logs ───────────────────────────────────────────────────────────────

@router.get("/time-logs", response_model=PaginatedResponse)
async def list_time_logs(
    page:        int           = Query(1, ge=1),
    page_size:   int           = Query(20, ge=1, le=100),
    customer_id: Optional[int] = Query(None),
    task_id:     Optional[int] = Query(None),
    user_id:     Optional[int] = Query(None),
    is_billed:   Optional[bool]= Query(None),
    date_from:   Optional[date]= Query(None),
    date_to:     Optional[date]= Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    logs, total = await svc.get_time_logs(
        db, current_user.tenant_id, page, page_size,
        user_id, customer_id, task_id, is_billed, date_from, date_to,
    )
    return PaginatedResponse(
        items=[TimeLogOut.model_validate(l) for l in logs],
        total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("/time-logs", response_model=TimeLogOut, status_code=201)
async def create_time_log(
    data: TimeLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    log = await svc.create_time_log(db, current_user.tenant_id, current_user.user_id, data)
    return TimeLogOut.model_validate(log)


@router.patch("/time-logs/{log_id}", response_model=TimeLogOut)
async def update_time_log(
    data: TimeLogUpdate,
    log_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    log = await svc.update_time_log(
        db, current_user.tenant_id, log_id, data, current_user.user_id
    )
    return TimeLogOut.model_validate(log)


@router.delete("/time-logs/{log_id}", response_model=MessageResponse)
async def delete_time_log(
    log_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_time_log(db, current_user.tenant_id, log_id)
    return MessageResponse(message="Time log deleted.")


# ─── Expenses ────────────────────────────────────────────────────────────────

@router.get("/expenses", response_model=PaginatedResponse)
async def list_expenses(
    page:      int           = Query(1, ge=1),
    page_size: int           = Query(20, ge=1, le=100),
    status:    Optional[str] = Query(None),
    user_id:   Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    expenses, total = await svc.get_expenses(
        db, current_user.tenant_id, page, page_size, user_id, status
    )
    return PaginatedResponse(
        items=[ExpenseOut.model_validate(e) for e in expenses],
        total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    expense = await svc.create_expense(
        db, current_user.tenant_id, current_user.user_id, data
    )
    return ExpenseOut.model_validate(expense)


@router.post("/expenses/{expense_id}/approve", response_model=ExpenseOut)
async def approve_expense(
    expense_id: int = Path(...),
    approve: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    expense = await svc.approve_expense(
        db, current_user.tenant_id, expense_id, current_user.user_id, approve
    )
    return ExpenseOut.model_validate(expense)
