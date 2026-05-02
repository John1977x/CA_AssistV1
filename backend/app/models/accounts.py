from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class AccountHead(Base):
    """Account Head - Chart of accounts"""
    __tablename__ = "account_heads"

    account_head_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    head_name       = Column(String(150), nullable=False)
    head_code       = Column(String(20), nullable=False, unique=True)  # e.g. INC-001
    head_type       = Column(String(20), nullable=False, index=True)  # ASSET / LIABILITY / INCOME / EXPENSE
    head_sub_type   = Column(String(50))  # e.g. SERVICE_FEES / GST / CLIENT_COST
    parent_head_id  = Column(UUID(as_uuid=True), ForeignKey("account_heads.account_head_id"))  # Self-referencing for hierarchy
    description     = Column(String(300))
    is_system       = Column(Boolean, nullable=False, default=False)  # 1 = system-defined, cannot be deleted
    is_active       = Column(Boolean, nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    parent = relationship("AccountHead", remote_side=[account_head_id], foreign_keys=[parent_head_id], backref="children")
    transactions = relationship("AccountTransaction", back_populates="account_head")
    ledgers = relationship("AccountLedger", back_populates="account_head")


class AccountTransaction(Base):
    """Account Transaction"""
    __tablename__ = "account_transactions"

    txn_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    account_head_id = Column(UUID(as_uuid=True), ForeignKey("account_heads.account_head_id"), nullable=False, index=True)
    ref_type        = Column(String(30))  # TASK_PAYMENT / CLIENT_SUBSCRIPTION / CA_SUBSCRIPTION / EXPENSE / MANUAL
    ref_id          = Column(String(100))  # ID of referenced record (stored as string for flexibility)
    financial_year  = Column(String(10), nullable=False, index=True)  # e.g. 2024-25
    txn_date        = Column(Date, nullable=False, index=True)
    amount          = Column(Numeric(12, 2), nullable=False)
    txn_type        = Column(String(10), nullable=False)  # CREDIT / DEBIT
    currency        = Column(String(5), nullable=False, default='INR')
    exchange_rate   = Column(Numeric(10, 6), nullable=False, default=1.0)  # For foreign currency
    description     = Column(String(300))
    created_by      = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    status          = Column(String(20), nullable=False, default='Posted')  # Draft / Posted / Voided
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    account_head = relationship("AccountHead", back_populates="transactions")
    creator = relationship("User", foreign_keys=[created_by])


class AccountLedger(Base):
    """Account Ledger (View / Snapshot)"""
    __tablename__ = "account_ledgers"

    ledger_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    account_head_id = Column(UUID(as_uuid=True), ForeignKey("account_heads.account_head_id"), nullable=False, index=True)
    financial_year  = Column(String(10), nullable=False, index=True)
    opening_balance = Column(Numeric(15, 2), nullable=False, default=0.00)  # Balance at start of FY
    total_credits   = Column(Numeric(15, 2), nullable=False, default=0.00)
    total_debits    = Column(Numeric(15, 2), nullable=False, default=0.00)
    closing_balance = Column(Numeric(15, 2), nullable=False, default=0.00)  # Opening + Credits - Debits
    as_of           = Column(Date, nullable=False)  # Snapshot date
    currency        = Column(String(5), nullable=False, default='INR')
    updated_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())  # Recomputed on each new transaction

    tenant = relationship("Tenant")
    account_head = relationship("AccountHead", back_populates="ledgers")
