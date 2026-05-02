from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from fastapi import HTTPException
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Tuple
from decimal import Decimal

from app.models.billing import Invoice, InvoiceLineItem, TimeLog, Expense, PaymentReceived
from app.schemas.billing import (
    InvoiceCreate, InvoiceUpdate, LineItemCreate,
    TimeLogCreate, TimeLogUpdate,
    ExpenseCreate, ExpenseUpdate,
    PaymentCreate,
)


# ─── Invoice number generator ─────────────────────────────────────────────────

async def _next_invoice_number(db: AsyncSession, tenant_id: int) -> str:
    year = date.today().year
    result = await db.execute(
        select(func.count(Invoice.invoice_id)).where(
            Invoice.tenant_id == tenant_id,
            func.extract("year", Invoice.invoice_date) == year,
        )
    )
    seq = (result.scalar() or 0) + 1
    return f"INV-{year}-{str(seq).zfill(4)}"


# ─── Tax computation ─────────────────────────────────────────────────────────

def _compute_line(item: LineItemCreate, is_igst: bool) -> dict:
    qty = Decimal(str(item.quantity))
    price = Decimal(str(item.unit_price))
    disc_pct = Decimal(str(item.discount_pct or 0))
    gst_rate = Decimal(str(item.gst_rate_pct or 18))

    gross = qty * price
    discount = gross * disc_pct / 100
    taxable = gross - discount
    total_gst = taxable * gst_rate / 100

    if is_igst:
        cgst = Decimal(0)
        sgst = Decimal(0)
        igst = total_gst
    else:
        cgst = total_gst / 2
        sgst = total_gst / 2
        igst = Decimal(0)

    line_total = taxable + total_gst
    return {
        "taxable_amount": float(taxable.quantize(Decimal("0.01"))),
        "cgst_amount":    float(cgst.quantize(Decimal("0.01"))),
        "sgst_amount":    float(sgst.quantize(Decimal("0.01"))),
        "igst_amount":    float(igst.quantize(Decimal("0.01"))),
        "line_total":     float(line_total.quantize(Decimal("0.01"))),
    }


def _sum_invoice(line_items_data: list, discount_pct: float) -> dict:
    subtotal = sum(i["unit_price"] * i["quantity"] for i in line_items_data)
    disc_amount = subtotal * discount_pct / 100
    taxable = sum(i["taxable_amount"] for i in line_items_data)
    cgst = sum(i["cgst_amount"] for i in line_items_data)
    sgst = sum(i["sgst_amount"] for i in line_items_data)
    igst = sum(i["igst_amount"] for i in line_items_data)
    total_tax = cgst + sgst + igst
    total = taxable + total_tax
    return {
        "subtotal":        round(subtotal, 2),
        "discount_amount": round(disc_amount, 2),
        "taxable_amount":  round(taxable, 2),
        "cgst_amount":     round(cgst, 2),
        "sgst_amount":     round(sgst, 2),
        "igst_amount":     round(igst, 2),
        "total_tax":       round(total_tax, 2),
        "total_amount":    round(total, 2),
        "balance_due":     round(total, 2),
    }


# ─── Invoice CRUD ─────────────────────────────────────────────────────────────

async def get_invoices(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    overdue_only: bool = False,
) -> Tuple[List[Invoice], int]:
    query = select(Invoice).where(
        Invoice.tenant_id == tenant_id,
        Invoice.is_deleted == False,
    )
    if search:
        query = query.where(Invoice.invoice_number.ilike(f"%{search}%"))
    if status:
        query = query.where(Invoice.status == status)
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    if overdue_only:
        query = query.where(
            Invoice.due_date < date.today(),
            Invoice.status.not_in(["PAID", "CANCELLED"]),
        )
    count = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count.scalar()
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Invoice.invoice_date.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_invoice(db: AsyncSession, tenant_id: int, invoice_id: int) -> Invoice:
    result = await db.execute(
        select(Invoice).where(
            Invoice.invoice_id == invoice_id,
            Invoice.tenant_id == tenant_id,
            Invoice.is_deleted == False,
        )
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return inv


async def create_invoice(
    db: AsyncSession, tenant_id: int, data: InvoiceCreate, created_by: int
) -> Invoice:
    inv_number = await _next_invoice_number(db, tenant_id)

    # Compute line totals
    line_computed = []
    for item in data.line_items:
        comp = _compute_line(item, data.is_igst)
        line_computed.append({**item.model_dump(), **comp})

    totals = _sum_invoice(line_computed, data.discount_pct)

    invoice = Invoice(
        tenant_id=tenant_id,
        customer_id=data.customer_id,
        branch_id=data.branch_id,
        task_id=data.task_id,
        invoice_number=inv_number,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        place_of_supply=data.place_of_supply,
        is_igst=data.is_igst,
        gst_rate_pct=data.gst_rate_pct,
        discount_pct=data.discount_pct,
        payment_terms_days=data.payment_terms_days,
        notes=data.notes,
        terms_conditions=data.terms_conditions,
        internal_notes=data.internal_notes,
        created_by_user_id=created_by,
        status="DRAFT",
        **totals,
    )
    db.add(invoice)
    await db.flush()

    for i, ld in enumerate(line_computed):
        li = InvoiceLineItem(invoice_id=invoice.invoice_id, **ld)
        db.add(li)

    await db.commit()
    await db.refresh(invoice)
    return invoice


async def update_invoice(
    db: AsyncSession, tenant_id: int, invoice_id: int, data: InvoiceUpdate
) -> Invoice:
    invoice = await get_invoice(db, tenant_id, invoice_id)
    if invoice.status == "PAID":
        raise HTTPException(status_code=400, detail="Cannot edit a fully paid invoice.")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(Invoice).where(Invoice.invoice_id == invoice_id).values(**update_data))
        await db.commit()
        await db.refresh(invoice)
    return invoice


async def send_invoice(db: AsyncSession, tenant_id: int, invoice_id: int, user_id: int) -> Invoice:
    invoice = await get_invoice(db, tenant_id, invoice_id)
    if invoice.status not in ("DRAFT",):
        raise HTTPException(status_code=400, detail="Only draft invoices can be sent.")
    await db.execute(
        update(Invoice).where(Invoice.invoice_id == invoice_id).values(
            status="SENT",
            sent_at=datetime.now(timezone.utc),
            sent_by_user_id=user_id,
        )
    )
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def cancel_invoice(db: AsyncSession, tenant_id: int, invoice_id: int) -> Invoice:
    invoice = await get_invoice(db, tenant_id, invoice_id)
    if invoice.status == "PAID":
        raise HTTPException(status_code=400, detail="Cannot cancel a paid invoice.")
    await db.execute(
        update(Invoice).where(Invoice.invoice_id == invoice_id).values(status="CANCELLED")
    )
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def delete_invoice(db: AsyncSession, tenant_id: int, invoice_id: int):
    invoice = await get_invoice(db, tenant_id, invoice_id)
    if invoice.status not in ("DRAFT", "CANCELLED"):
        raise HTTPException(status_code=400, detail="Only draft or cancelled invoices can be deleted.")
    await db.execute(
        update(Invoice).where(Invoice.invoice_id == invoice_id).values(is_deleted=True)
    )
    await db.commit()


# ─── Payment ─────────────────────────────────────────────────────────────────

async def record_payment(
    db: AsyncSession, tenant_id: int, invoice_id: int,
    data: PaymentCreate, user_id: int,
) -> PaymentReceived:
    invoice = await get_invoice(db, tenant_id, invoice_id)

    if data.amount > float(invoice.balance_due):
        raise HTTPException(
            status_code=400,
            detail=f"Payment ₹{data.amount:,.2f} exceeds balance due ₹{float(invoice.balance_due):,.2f}."
        )

    net = data.amount - data.tds_deducted
    payment = PaymentReceived(
        tenant_id=tenant_id,
        invoice_id=invoice_id,
        customer_id=invoice.customer_id,
        net_received=net,
        recorded_by_user_id=user_id,
        **data.model_dump(),
    )
    db.add(payment)
    await db.flush()

    new_paid = float(invoice.amount_paid) + data.amount
    new_balance = float(invoice.total_amount) - new_paid
    new_status = "PAID" if new_balance <= 0 else "PARTIALLY_PAID"

    await db.execute(
        update(Invoice).where(Invoice.invoice_id == invoice_id).values(
            amount_paid=new_paid,
            balance_due=max(0, new_balance),
            status=new_status,
        )
    )
    await db.commit()
    await db.refresh(payment)
    return payment


# ─── Time Log ────────────────────────────────────────────────────────────────

async def get_time_logs(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    task_id: Optional[int] = None,
    is_billed: Optional[bool] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Tuple[List[TimeLog], int]:
    query = select(TimeLog).where(
        TimeLog.tenant_id == tenant_id,
        TimeLog.is_deleted == False,
    )
    if user_id:     query = query.where(TimeLog.user_id == user_id)
    if customer_id: query = query.where(TimeLog.customer_id == customer_id)
    if task_id:     query = query.where(TimeLog.task_id == task_id)
    if is_billed is not None: query = query.where(TimeLog.is_billed == is_billed)
    if date_from:   query = query.where(TimeLog.log_date >= date_from)
    if date_to:     query = query.where(TimeLog.log_date <= date_to)

    count = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count.scalar()
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(TimeLog.log_date.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_time_log(
    db: AsyncSession, tenant_id: int, user_id: int, data: TimeLogCreate
) -> TimeLog:
    amount = None
    if data.is_billable and data.hourly_rate:
        hours = data.duration_minutes / 60
        amount = round(hours * data.hourly_rate, 2)

    log = TimeLog(
        tenant_id=tenant_id,
        user_id=user_id,
        billable_minutes=data.duration_minutes,
        line_amount=amount,
        **data.model_dump(),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def update_time_log(
    db: AsyncSession, tenant_id: int, log_id: int, data: TimeLogUpdate, user_id: int
) -> TimeLog:
    result = await db.execute(
        select(TimeLog).where(
            TimeLog.time_log_id == log_id,
            TimeLog.tenant_id == tenant_id,
            TimeLog.is_deleted == False,
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    if log.is_billed:
        raise HTTPException(status_code=400, detail="Cannot edit a billed time log.")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(TimeLog).where(TimeLog.time_log_id == log_id).values(**update_data))
        await db.commit()
        await db.refresh(log)
    return log


async def delete_time_log(db: AsyncSession, tenant_id: int, log_id: int):
    result = await db.execute(
        select(TimeLog).where(TimeLog.time_log_id == log_id, TimeLog.tenant_id == tenant_id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    if log.is_billed:
        raise HTTPException(status_code=400, detail="Cannot delete a billed time log.")
    await db.execute(
        update(TimeLog).where(TimeLog.time_log_id == log_id).values(is_deleted=True)
    )
    await db.commit()


# ─── Expense ──────────────────────────────────────────────────────────────────

async def get_expenses(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Tuple[List[Expense], int]:
    query = select(Expense).where(Expense.tenant_id == tenant_id)
    if user_id: query = query.where(Expense.user_id == user_id)
    if status:  query = query.where(Expense.status == status)
    count = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count.scalar()
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Expense.expense_date.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_expense(
    db: AsyncSession, tenant_id: int, user_id: int, data: ExpenseCreate
) -> Expense:
    total = data.amount + data.gst_amount
    expense = Expense(
        tenant_id=tenant_id,
        user_id=user_id,
        total_amount=total,
        **data.model_dump(),
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def approve_expense(
    db: AsyncSession, tenant_id: int, expense_id: int, approver_id: int, approve: bool
) -> Expense:
    result = await db.execute(
        select(Expense).where(Expense.expense_id == expense_id, Expense.tenant_id == tenant_id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")
    await db.execute(
        update(Expense).where(Expense.expense_id == expense_id).values(
            status="APPROVED" if approve else "REJECTED",
            approved_by_user_id=approver_id,
            approved_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(expense)
    return expense


# ─── Stats ────────────────────────────────────────────────────────────────────

async def get_billing_stats(db: AsyncSession, tenant_id: int) -> dict:
    today = date.today()
    month_start = today.replace(day=1)

    base = and_(Invoice.tenant_id == tenant_id, Invoice.is_deleted == False)

    total_inv   = await db.execute(select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(base, Invoice.status != "CANCELLED"))
    total_paid  = await db.execute(select(func.coalesce(func.sum(Invoice.amount_paid), 0)).where(base))
    total_bal   = await db.execute(select(func.coalesce(func.sum(Invoice.balance_due), 0)).where(base, Invoice.status.not_in(["PAID","CANCELLED"])))
    total_odue  = await db.execute(select(func.coalesce(func.sum(Invoice.balance_due), 0)).where(
        base, Invoice.due_date < today, Invoice.status.not_in(["PAID","CANCELLED"])
    ))
    inv_count   = await db.execute(select(func.count(Invoice.invoice_id)).where(base))
    draft_count = await db.execute(select(func.count(Invoice.invoice_id)).where(base, Invoice.status == "DRAFT"))
    odue_count  = await db.execute(select(func.count(Invoice.invoice_id)).where(
        base, Invoice.due_date < today, Invoice.status.not_in(["PAID","CANCELLED"])
    ))
    month_rev   = await db.execute(select(func.coalesce(func.sum(Invoice.amount_paid), 0)).where(
        base, Invoice.invoice_date >= month_start
    ))
    unbilled_hrs= await db.execute(select(func.coalesce(func.sum(TimeLog.billable_minutes), 0)).where(
        TimeLog.tenant_id == tenant_id,
        TimeLog.is_billable == True,
        TimeLog.is_billed == False,
        TimeLog.is_deleted == False,
    ))

    return {
        "total_invoiced":     float(total_inv.scalar()),
        "total_collected":    float(total_paid.scalar()),
        "total_outstanding":  float(total_bal.scalar()),
        "total_overdue":      float(total_odue.scalar()),
        "invoice_count":      inv_count.scalar(),
        "draft_count":        draft_count.scalar(),
        "overdue_count":      odue_count.scalar(),
        "unbilled_hours":     round(float(unbilled_hrs.scalar()) / 60, 2),
        "this_month_revenue": float(month_rev.scalar()),
    }


# ─── Tally XML Export ─────────────────────────────────────────────────────────

async def generate_tally_xml(
    db: AsyncSession, tenant_id: int, invoice_ids: List[int]
) -> str:
    vouchers_xml = []

    for inv_id in invoice_ids:
        inv = await get_invoice(db, tenant_id, inv_id)
        # Load customer
        from app.models.customer import Customer
        cust_r = await db.execute(select(Customer).where(Customer.customer_id == inv.customer_id))
        cust = cust_r.scalar_one_or_none()
        cust_name = cust.display_name if cust else "Unknown"

        items_xml = ""
        for li in inv.line_items:
            items_xml += f"""
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>{li.description[:40]}</LEDGERNAME>
                <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                <AMOUNT>-{li.taxable_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""

        if inv.cgst_amount:
            items_xml += f"""
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>CGST @ {inv.gst_rate_pct / 2:.1f}%</LEDGERNAME>
                <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                <AMOUNT>-{inv.cgst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>SGST @ {inv.gst_rate_pct / 2:.1f}%</LEDGERNAME>
                <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                <AMOUNT>-{inv.sgst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""

        if inv.igst_amount:
            items_xml += f"""
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>IGST @ {inv.gst_rate_pct:.1f}%</LEDGERNAME>
                <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                <AMOUNT>-{inv.igst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""

        vouchers_xml.append(f"""
        <VOUCHER VCHTYPE="Sales" ACTION="Create">
            <DATE>{inv.invoice_date.strftime('%Y%m%d')}</DATE>
            <VOUCHERNUMBER>{inv.invoice_number}</VOUCHERNUMBER>
            <PARTYLEDGERNAME>{cust_name}</PARTYLEDGERNAME>
            <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
            <NARRATION>{inv.notes or ''}</NARRATION>
            <ALLLEDGERENTRIES.LIST>
                <LEDGERNAME>{cust_name}</LEDGERNAME>
                <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                <AMOUNT>{inv.total_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            {items_xml}
        </VOUCHER>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>CA Assists Export</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    {''.join(vouchers_xml)}
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
    return xml
