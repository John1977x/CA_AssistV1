from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, SmallInteger, String, Text, func, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Invoice(Base):
    __tablename__ = "invoice"

    invoice_id          = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    branch_id           = Column(Integer, ForeignKey("branch.branch_id"))
    task_id             = Column(Integer, ForeignKey("task.task_id"))       # optional link

    invoice_number      = Column(String(50), nullable=False)                # INV-2024-0001
    invoice_date        = Column(Date, nullable=False)
    due_date            = Column(Date, nullable=False)

    # Amounts
    subtotal            = Column(Numeric(12, 2), nullable=False, default=0)
    discount_pct        = Column(Numeric(5, 2), default=0)
    discount_amount     = Column(Numeric(12, 2), default=0)
    taxable_amount      = Column(Numeric(12, 2), nullable=False, default=0)
    cgst_amount         = Column(Numeric(10, 2), default=0)
    sgst_amount         = Column(Numeric(10, 2), default=0)
    igst_amount         = Column(Numeric(10, 2), default=0)
    total_tax           = Column(Numeric(10, 2), default=0)
    total_amount        = Column(Numeric(12, 2), nullable=False, default=0)
    amount_paid         = Column(Numeric(12, 2), nullable=False, default=0)
    balance_due         = Column(Numeric(12, 2), nullable=False, default=0)
    currency_code       = Column(String(3), nullable=False, default="INR")

    # GST
    place_of_supply     = Column(String(50))   # state code
    is_igst             = Column(Boolean, nullable=False, default=False)
    gst_rate_pct        = Column(Numeric(5, 2), default=18)
    reverse_charge      = Column(Boolean, nullable=False, default=False)

    # Status & meta
    status              = Column(String(20), nullable=False, default="DRAFT")
    # DRAFT → SENT → PARTIALLY_PAID → PAID → CANCELLED → OVERDUE
    payment_terms_days  = Column(Integer, default=30)
    notes               = Column(Text)
    terms_conditions    = Column(Text)
    internal_notes      = Column(Text)

    # Tally / accounting sync
    tally_voucher_number = Column(String(100))
    tally_synced_at     = Column(DateTime(timezone=True))
    zoho_invoice_id     = Column(String(100))
    qb_invoice_id       = Column(String(100))

    sent_at             = Column(DateTime(timezone=True))
    sent_by_user_id     = Column(Integer, ForeignKey("user.user_id"))
    created_by_user_id  = Column(Integer, ForeignKey("user.user_id"))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted          = Column(Boolean, nullable=False, default=False)

    tenant          = relationship("Tenant")
    customer        = relationship("Customer")
    branch          = relationship("Branch")
    task            = relationship("Task")
    line_items      = relationship("InvoiceLineItem", back_populates="invoice",
                                   cascade="all, delete-orphan", order_by="InvoiceLineItem.sort_order")
    payments        = relationship("PaymentReceived", back_populates="invoice",
                                   cascade="all, delete-orphan")
    sent_by         = relationship("User", foreign_keys=[sent_by_user_id])
    created_by      = relationship("User", foreign_keys=[created_by_user_id])


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_item"

    line_item_id        = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id          = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=False)
    description         = Column(String(500), nullable=False)
    hsn_sac_code        = Column(String(20))     # SAC for services
    quantity            = Column(Numeric(10, 3), nullable=False, default=1)
    unit                = Column(String(20))      # hrs, months, flat
    unit_price          = Column(Numeric(12, 2), nullable=False)
    discount_pct        = Column(Numeric(5, 2), default=0)
    taxable_amount      = Column(Numeric(12, 2), nullable=False)
    gst_rate_pct        = Column(Numeric(5, 2), default=18)
    cgst_amount         = Column(Numeric(10, 2), default=0)
    sgst_amount         = Column(Numeric(10, 2), default=0)
    igst_amount         = Column(Numeric(10, 2), default=0)
    line_total          = Column(Numeric(12, 2), nullable=False)
    sort_order          = Column(Integer, nullable=False, default=0)
    task_id             = Column(Integer, ForeignKey("task.task_id"))
    time_log_ids        = Column(ARRAY(Integer))  # linked time logs

    invoice     = relationship("Invoice", back_populates="line_items")
    task        = relationship("Task")


class TimeLog(Base):
    __tablename__ = "time_log"

    time_log_id         = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    user_id             = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    task_id             = Column(Integer, ForeignKey("task.task_id"))

    log_date            = Column(Date, nullable=False)
    start_time          = Column(String(5))      # HH:MM
    end_time            = Column(String(5))      # HH:MM
    duration_minutes    = Column(Integer, nullable=False)    # actual minutes
    billable_minutes    = Column(Integer, nullable=False)    # may differ
    description         = Column(Text, nullable=False)
    is_billable         = Column(Boolean, nullable=False, default=True)
    is_billed           = Column(Boolean, nullable=False, default=False)
    invoice_id          = Column(Integer, ForeignKey("invoice.invoice_id"))
    hourly_rate         = Column(Numeric(10, 2))
    line_amount         = Column(Numeric(10, 2))   # computed

    created_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted  = Column(Boolean, nullable=False, default=False)

    tenant      = relationship("Tenant")
    user        = relationship("User")
    customer    = relationship("Customer")
    task        = relationship("Task")
    invoice     = relationship("Invoice")


class Expense(Base):
    __tablename__ = "expense"

    expense_id          = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    user_id             = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"))  # reimbursable
    task_id             = Column(Integer, ForeignKey("task.task_id"))

    expense_date        = Column(Date, nullable=False)
    category            = Column(String(60), nullable=False)  # TRAVEL, FILING_FEE, OFFICE, etc.
    description         = Column(Text, nullable=False)
    amount              = Column(Numeric(10, 2), nullable=False)
    gst_amount          = Column(Numeric(10, 2), default=0)
    total_amount        = Column(Numeric(10, 2), nullable=False)
    is_billable         = Column(Boolean, nullable=False, default=False)
    is_reimbursed       = Column(Boolean, nullable=False, default=False)
    receipt_url         = Column(Text)
    payment_mode        = Column(String(30))   # CASH, CARD, UPI
    vendor_name         = Column(String(200))
    status              = Column(String(20), nullable=False, default="PENDING")
    # PENDING → APPROVED → REJECTED → REIMBURSED

    approved_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    approved_at         = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant      = relationship("Tenant")
    user        = relationship("User", foreign_keys=[user_id])
    customer    = relationship("Customer")
    task        = relationship("Task")
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])


class PaymentReceived(Base):
    __tablename__ = "payment_received"

    payment_id          = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    invoice_id          = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=False)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)

    payment_date        = Column(Date, nullable=False)
    amount              = Column(Numeric(12, 2), nullable=False)
    payment_mode        = Column(String(30), nullable=False)   # CASH, NEFT, RTGS, UPI, CHEQUE, CARD
    reference_number    = Column(String(100))   # UTR / cheque number
    bank_name           = Column(String(100))
    notes               = Column(Text)
    tds_deducted        = Column(Numeric(10, 2), default=0)
    net_received        = Column(Numeric(12, 2), nullable=False)

    recorded_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant          = relationship("Tenant")
    invoice         = relationship("Invoice", back_populates="payments")
    customer        = relationship("Customer")
    recorded_by     = relationship("User", foreign_keys=[recorded_by_user_id])
