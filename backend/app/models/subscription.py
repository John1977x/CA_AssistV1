from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class CAPlan(Base):
    """CA Subscription Plan - Plans for CA firms"""
    __tablename__ = "ca_plans"

    ca_plan_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_name       = Column(String(100), nullable=False)
    plan_code       = Column(String(30), nullable=False, unique=True)  # e.g. CA_STARTER
    description     = Column(String(300))
    price_monthly   = Column(Numeric(12, 2), nullable=False)
    price_yearly    = Column(Numeric(12, 2), nullable=False)
    gst_pct         = Column(Numeric(5, 2), nullable=False, default=18.00)
    max_clients     = Column(Integer, nullable=False)  # -1 = Unlimited
    max_users       = Column(Integer, nullable=False)  # -1 = Unlimited
    max_storage_gb  = Column(Integer, nullable=False)  # -1 = Unlimited
    features_json   = Column(JSONB)  # Feature flags JSON
    is_active       = Column(Boolean, nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    subscriptions = relationship("CASubscription", back_populates="plan")


class CASubscription(Base):
    """CA Subscription - Subscriptions for CA firms"""
    __tablename__ = "ca_subscriptions"

    ca_sub_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    ca_plan_id      = Column(UUID(as_uuid=True), ForeignKey("ca_plans.ca_plan_id"), nullable=False, index=True)
    start_date      = Column(Date, nullable=False)
    end_date        = Column(Date, nullable=False)
    billing_cycle   = Column(String(20), nullable=False)  # MONTHLY / QUARTERLY / YEARLY
    amount          = Column(Numeric(12, 2), nullable=False)  # Net amount before GST
    gst_amount      = Column(Numeric(12, 2), nullable=False)
    total_amount    = Column(Numeric(12, 2), nullable=False)  # Amount + GST
    payment_status  = Column(String(20), nullable=False, default='Pending')  # Pending / Paid / Failed
    payment_date    = Column(Date)
    transaction_ref = Column(String(100))
    status          = Column(String(20), nullable=False, default='Active', index=True)  # Active / Suspended / Cancelled / Expired
    auto_renew      = Column(Boolean, nullable=False, default=True)
    cancelled_at    = Column(DateTime(timezone=True))
    cancel_reason   = Column(String(300))
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    plan = relationship("CAPlan", back_populates="subscriptions")


class ClientPlan(Base):
    """Client Service Plan - Plans that CAs offer to their clients"""
    __tablename__ = "client_plans"

    client_plan_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)  # CA creates custom plans for their clients
    plan_name           = Column(String(100), nullable=False)
    plan_code           = Column(String(30), nullable=False, unique=True)
    description         = Column(String(300))
    price_monthly       = Column(Numeric(12, 2), nullable=False)
    price_yearly        = Column(Numeric(12, 2), nullable=False)
    gst_pct             = Column(Numeric(5, 2), nullable=False, default=18.00)
    services_included   = Column(JSONB)  # JSON array: ["GST","ITR","ROC"]
    max_documents       = Column(Integer, nullable=False, default=-1)  # -1 = Unlimited
    is_active           = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    subscriptions = relationship("ClientSubscription", back_populates="plan")


class ClientSubscription(Base):
    """Client Subscription - Subscriptions that clients have with CAs"""
    __tablename__ = "client_subscriptions"

    client_sub_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    customer_id     = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    client_plan_id  = Column(UUID(as_uuid=True), ForeignKey("client_plans.client_plan_id"), nullable=False, index=True)
    start_date      = Column(Date, nullable=False)
    end_date        = Column(Date, nullable=False)
    billing_cycle   = Column(String(20), nullable=False)  # MONTHLY / QUARTERLY / HALF_YEARLY / YEARLY
    amount          = Column(Numeric(12, 2), nullable=False)
    gst_amount      = Column(Numeric(12, 2), nullable=False)
    total_amount    = Column(Numeric(12, 2), nullable=False)
    payment_status  = Column(String(20), nullable=False, default='Pending')
    payment_date    = Column(Date)
    transaction_ref = Column(String(100))
    status          = Column(String(20), nullable=False, default='Active', index=True)
    auto_renew      = Column(Boolean, nullable=False, default=True)
    cancelled_at    = Column(DateTime(timezone=True))
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    customer = relationship("Customer")
    plan = relationship("ClientPlan", back_populates="subscriptions")
    invoices = relationship("ClientInvoice", back_populates="subscription")


class ClientInvoice(Base):
    """Client Invoice - Invoices for client subscriptions or ad-hoc services"""
    __tablename__ = "client_invoices"

    invoice_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    customer_id     = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    client_sub_id   = Column(UUID(as_uuid=True), ForeignKey("client_subscriptions.client_sub_id"), index=True)  # NULL = ad-hoc invoice
    task_id         = Column(Integer, ForeignKey("task.task_id"), index=True)  # NULL = subscription invoice
    invoice_number  = Column(String(50), nullable=False, unique=True)
    invoice_date    = Column(Date, nullable=False)
    due_date        = Column(Date)
    amount          = Column(Numeric(12, 2), nullable=False)
    gst_amount      = Column(Numeric(12, 2), nullable=False)
    total_amount    = Column(Numeric(12, 2), nullable=False)
    payment_status  = Column(String(20), nullable=False, default='Pending')
    payment_date    = Column(Date)
    pdf_url         = Column(String(500))  # Generated invoice PDF
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    customer = relationship("Customer")
    subscription = relationship("ClientSubscription", back_populates="invoices")
    task = relationship("Task")
