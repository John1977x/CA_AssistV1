from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class CustomerEvent(Base):
    """Customer Event (Birthday/Anniversary)"""
    __tablename__ = "customer_events"

    event_id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    event_type          = Column(String(20), nullable=False)  # BIRTHDAY / ANNIVERSARY / CUSTOM
    event_date          = Column(Date, nullable=False, index=True)  # Full date; year used for BIRTHDAY triggers
    recurring_yearly    = Column(Boolean, nullable=False, default=True)  # 1 = trigger every year
    last_triggered_year = Column(Integer)  # Prevents duplicate sends in same year
    is_active           = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    customer = relationship("Customer")
    tenant = relationship("Tenant")
    notifications = relationship("CustomerEventNotification", back_populates="event")


class CustomerEventNotification(Base):
    """Customer Event Notification"""
    __tablename__ = "customer_event_notifications"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id        = Column(UUID(as_uuid=True), ForeignKey("customer_events.event_id"), nullable=False, index=True)
    customer_id     = Column(Integer, ForeignKey("customer.customer_id"), nullable=False, index=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    channel         = Column(String(20), nullable=False)  # EMAIL / WHATSAPP / SMS
    template_id     = Column(UUID(as_uuid=True), ForeignKey("email_templates.template_id"))  # Email template ref if channel=EMAIL
    wa_template_id  = Column(UUID(as_uuid=True), ForeignKey("wa_templates.wa_template_id"))  # WA template ref if channel=WHATSAPP
    scheduled_at    = Column(DateTime(timezone=True), nullable=False)
    sent_at         = Column(DateTime(timezone=True))
    status          = Column(String(20), nullable=False, default='Pending')  # Pending / Sent / Failed
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    event = relationship("CustomerEvent", back_populates="notifications")
    customer = relationship("Customer")
    tenant = relationship("Tenant")
    email_template = relationship("EmailTemplate", foreign_keys=[template_id])
    wa_template = relationship("WATemplate", foreign_keys=[wa_template_id])
