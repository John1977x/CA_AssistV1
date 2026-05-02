from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


# ─── Email Templates & Queue ─────────────────────────────────────────────────

class EmailTemplate(Base):
    """Email Template"""
    __tablename__ = "email_templates"

    template_id     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    template_name   = Column(String(150), nullable=False)
    template_code   = Column(String(50), nullable=False, unique=True)  # e.g. WELCOME_EMAIL
    subject         = Column(String(300), nullable=False)  # Supports {{variable}} tokens
    body_html       = Column(Text, nullable=False)  # HTML body with {{variable}} tokens
    variables_json  = Column(JSONB)  # Schema: {"name":"string","due_date":"date"}
    category        = Column(String(50))  # Onboarding / Reminder / Promotion / Birthday
    is_active       = Column(Boolean, nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    queue_items = relationship("EmailQueue", back_populates="template")
    schedulers = relationship("EmailScheduler", back_populates="template")


class EmailQueue(Base):
    """Email Queue"""
    __tablename__ = "email_queue"

    queue_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    template_id     = Column(UUID(as_uuid=True), ForeignKey("email_templates.template_id"), index=True)  # NULL if free-form email
    from_email      = Column(String(150), nullable=False)
    to_email        = Column(String(500), nullable=False, index=True)  # Comma-separated for multiple
    cc              = Column(String(500))
    bcc             = Column(String(500))
    subject         = Column(String(300), nullable=False)
    body_html       = Column(Text, nullable=False)  # Rendered HTML
    priority        = Column(String(10), nullable=False, default='NORMAL')  # LOW / NORMAL / HIGH
    scheduled_at    = Column(DateTime(timezone=True), index=True)  # NULL = send immediately
    sent_at         = Column(DateTime(timezone=True))
    status          = Column(String(20), nullable=False, default='Queued', index=True)  # Queued / Sending / Sent / Failed / Cancelled
    retry_count     = Column(Integer, nullable=False, default=0)  # Max 3 retries
    error_message   = Column(String(500))  # Last error if failed
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    template = relationship("EmailTemplate", back_populates="queue_items")
    logs = relationship("EmailLog", back_populates="queue")


class EmailLog(Base):
    """Email Log"""
    __tablename__ = "email_logs"

    log_id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id            = Column(UUID(as_uuid=True), ForeignKey("email_queue.queue_id"), nullable=False, index=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    to_email            = Column(String(500), nullable=False)
    subject             = Column(String(300), nullable=False)
    sent_at             = Column(DateTime(timezone=True), index=True)
    status              = Column(String(20), nullable=False)  # Sent / Failed / Bounced
    provider_response   = Column(String(500))  # SMTP / SES / SendGrid response
    opened_at           = Column(DateTime(timezone=True))  # Email tracking pixel
    clicked_at          = Column(DateTime(timezone=True))  # Link click tracking
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    queue = relationship("EmailQueue", back_populates="logs")
    tenant = relationship("Tenant")


class EmailScheduler(Base):
    """Email Scheduler"""
    __tablename__ = "email_schedulers"

    scheduler_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    template_id         = Column(UUID(as_uuid=True), ForeignKey("email_templates.template_id"), nullable=False, index=True)
    trigger_type        = Column(String(20), nullable=False)  # EVENT / CRON / MANUAL
    trigger_event       = Column(String(50))  # BIRTHDAY / ANNIVERSARY / TAX_DEADLINE etc.
    cron_expression     = Column(String(50))  # e.g. 0 9 * * MON
    recipient_type      = Column(String(30), nullable=False)  # All / Customer / Specific
    recipient_filter    = Column(JSONB)  # JSON filter criteria
    is_active           = Column(Boolean, nullable=False, default=True)
    last_run_at         = Column(DateTime(timezone=True))
    next_run_at         = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    template = relationship("EmailTemplate", back_populates="schedulers")


# ─── WhatsApp Templates & Queue ──────────────────────────────────────────────

class WATemplate(Base):
    """WhatsApp Template"""
    __tablename__ = "wa_templates"

    wa_template_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    template_name           = Column(String(150), nullable=False)
    template_code           = Column(String(50), nullable=False, unique=True)  # Internal code
    language                = Column(String(10), nullable=False, default='en')  # en / hi / gu etc.
    category                = Column(String(30), nullable=False)  # UTILITY / MARKETING / AUTHENTICATION
    header_type             = Column(String(20))  # TEXT / IMAGE / VIDEO / DOCUMENT / NONE
    header_content          = Column(String(300))
    body_text               = Column(Text, nullable=False)  # Supports {{1}} {{2}} placeholders
    footer_text             = Column(String(300))
    buttons_json            = Column(JSONB)  # Quick reply / CTA button config
    provider_template_id    = Column(String(100))  # Meta / WABA template ID
    status                  = Column(String(20), nullable=False, default='PENDING')  # PENDING / APPROVED / REJECTED
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    queue_items = relationship("WAQueue", back_populates="template")
    schedulers = relationship("WAScheduler", back_populates="template")


class WAQueue(Base):
    """WhatsApp Queue"""
    __tablename__ = "wa_queue"

    wa_queue_id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    wa_template_id      = Column(UUID(as_uuid=True), ForeignKey("wa_templates.wa_template_id"), nullable=False, index=True)
    to_phone            = Column(String(20), nullable=False, index=True)  # E.164 format e.g. 919876543210
    variables_json      = Column(JSONB)  # Placeholder values: {"1":"Ravi","2":"ITR"}
    media_url           = Column(String(500))  # For header IMAGE / VIDEO
    priority            = Column(String(10), nullable=False, default='NORMAL')
    scheduled_at        = Column(DateTime(timezone=True), index=True)
    sent_at             = Column(DateTime(timezone=True))
    status              = Column(String(20), nullable=False, default='Queued', index=True)  # Queued / Sent / Delivered / Read / Failed
    wa_message_id       = Column(String(100))  # Meta message ID after send
    error_code          = Column(String(20))
    error_message       = Column(String(300))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    template = relationship("WATemplate", back_populates="queue_items")
    logs = relationship("WALog", back_populates="queue")


class WALog(Base):
    """WhatsApp Log"""
    __tablename__ = "wa_logs"

    wa_log_id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wa_queue_id         = Column(UUID(as_uuid=True), ForeignKey("wa_queue.wa_queue_id"), nullable=False, index=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    to_phone            = Column(String(20), nullable=False)
    wa_message_id       = Column(String(100), index=True)
    sent_at             = Column(DateTime(timezone=True))
    delivered_at        = Column(DateTime(timezone=True))
    read_at             = Column(DateTime(timezone=True))
    status              = Column(String(20), nullable=False)  # Sent / Delivered / Read / Failed
    provider_response   = Column(JSONB)  # Full webhook payload JSON
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    queue = relationship("WAQueue", back_populates="logs")
    tenant = relationship("Tenant")


class WAScheduler(Base):
    """WhatsApp Scheduler"""
    __tablename__ = "wa_schedulers"

    scheduler_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    wa_template_id      = Column(UUID(as_uuid=True), ForeignKey("wa_templates.wa_template_id"), nullable=False, index=True)
    trigger_type        = Column(String(20), nullable=False)  # EVENT / CRON / MANUAL
    trigger_event       = Column(String(50))  # BIRTHDAY / ANNIVERSARY / DUE_DATE etc.
    cron_expression     = Column(String(50))
    recipient_type      = Column(String(30), nullable=False)
    recipient_filter    = Column(JSONB)  # JSON filter
    is_active           = Column(Boolean, nullable=False, default=True)
    last_run_at         = Column(DateTime(timezone=True))
    next_run_at         = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    template = relationship("WATemplate", back_populates="schedulers")
